"""Логика авторизации TST ID"""

import asyncio
from typing import Any, Optional, Dict, Union
from uuid import UUID

from .service import TSTIdService
from .schemas import TSTIdUserData, TSTIdLoginResponse, TSTIdUserResponse, TokenResponse
from .config import TSTIdConfig, default_config
from .interfaces import (
    UserRepositoryInterface,
    JWTServiceInterface,
    UserMapperInterface
)
from .exceptions import (
    TSTIdAuthError,
    TSTIdValidationError,
    TSTIdIntegrationError
)


class TSTIdAuthenticator:
    """Класс для обработки авторизации через TST ID"""
    
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        jwt_service: JWTServiceInterface,
        tst_service: Optional[TSTIdService] = None,
        user_mapper: Optional[UserMapperInterface] = None,
        config: Optional[TSTIdConfig] = None
    ):
        self.user_repository = user_repository
        self.jwt_service = jwt_service
        self.tst_service = tst_service or TSTIdService(config)
        self.user_mapper = user_mapper
        self.config = config or default_config
    
    async def authenticate(self, tst_token: str) -> TSTIdLoginResponse:
        """
        Выполняет полную авторизацию пользователя через TST ID
        
        Args:
            tst_token: JWT токен от TST ID
            
        Returns:
            TSTIdLoginResponse: Данные пользователя и токены
            
        Raises:
            TSTIdValidationError: При неверном токене
            TSTIdIntegrationError: При ошибке интеграции
        """
        try:
            # 1. Получаем и валидируем данные от TST ID
            tst_user_data = await self.tst_service.validate_and_get_user_data(tst_token)
            
            # 2. Находим или создаем пользователя (с retry для БД)
            user = await self._find_or_create_user_with_retry(tst_user_data)
            
            # 3. Генерируем токены
            tokens = self._generate_tokens(user)
            
            # 4. Формируем ответ
            user_response = self._build_user_response(user, tst_user_data)
            
            return TSTIdLoginResponse(
                user=user_response,
                tokens=tokens
            )
            
        except (TSTIdValidationError, TSTIdAuthError):
            raise
        except Exception as e:
            raise TSTIdIntegrationError(f"Authentication failed: {str(e)}")
    
    async def _find_or_create_user_with_retry(self, tst_data: TSTIdUserData) -> Any:
        """
        Находит существующего пользователя или создает нового с retry логикой для БД
        
        Args:
            tst_data: Данные пользователя от TST ID
            
        Returns:
            Пользователь (любой тип, зависит от реализации)
        """
        max_retries = self.config.tst_id_db_max_retries
        retry_delay = self.config.tst_id_db_retry_delay
        
        for attempt in range(max_retries):
            try:
                return await self._find_or_create_user(tst_data)
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Проверяем, что это ошибка соединения с БД
                if any(keyword in error_str for keyword in [
                    'connection', 'closed', 'timeout', 'network', 
                    'asyncpg', 'postgresql', 'database'
                ]):
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                        continue
                    else:
                        raise TSTIdIntegrationError(
                            f"Database connection failed after {max_retries} attempts: {str(e)}"
                        )
                else:
                    # Не ошибка соединения - пробрасываем дальше
                    raise

    async def _find_or_create_user(self, tst_data: TSTIdUserData) -> Any:
        """
        Находит существующего пользователя или создает нового
        
        Args:
            tst_data: Данные пользователя от TST ID
            
        Returns:
            Пользователь (любой тип, зависит от реализации)
        """
        # Ищем пользователя по TST ID
        user = await self._safe_db_operation(
            self.user_repository.find_by_tst_id, tst_data.tst_id
        )
        
        if user:
            # Пользователь найден - обновляем его данными из TST ID
            return await self._update_existing_user(user, tst_data)
        
        # Пользователь не найден - проверяем по email
        if self.config.link_existing_users:
            existing_user = await self._safe_db_operation(
                self.user_repository.find_by_email, tst_data.email
            )
            if existing_user:
                # Есть пользователь с таким email - привязываем TST ID
                return await self._link_tst_id_to_existing_user(existing_user, tst_data)
        
        # Создаем нового пользователя
        if self.config.auto_create_users:
            return await self._create_new_user(tst_data)
        else:
            raise TSTIdAuthError("User not found and auto-creation is disabled")
    
    async def _safe_db_operation(self, operation, *args, **kwargs):
        """
        Безопасное выполнение операции с БД с обработкой ошибок соединения
        """
        max_retries = 2  # Меньше попыток для отдельных операций
        retry_delay = self.config.tst_id_db_retry_delay * 0.5
        
        for attempt in range(max_retries):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                error_str = str(e).lower()
                
                # Проверяем, что это ошибка соединения с БД
                if any(keyword in error_str for keyword in [
                    'connection', 'closed', 'timeout', 'network', 
                    'asyncpg', 'postgresql', 'database'
                ]) and attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    raise

    async def _update_existing_user(self, user: Any, tst_data: TSTIdUserData) -> Any:
        """Обновляет существующего пользователя данными из TST ID"""
        if self.user_mapper:
            user = self.user_mapper.update_user_with_tst_data(user, tst_data)
        else:
            # Обновляем стандартные поля
            if hasattr(user, 'update_tst_info'):
                user.update_tst_info(
                    username=tst_data.username,
                    tst_role=tst_data.role,
                    position_id=tst_data.position_id,
                    github_token=tst_data.github_token
                )
            if hasattr(user, 'update_profile'):
                user.update_profile(full_name=tst_data.full_name)
            
            # Обновляем активность
            if hasattr(user, 'activate') and tst_data.is_active:
                user.activate()
            elif hasattr(user, 'deactivate') and not tst_data.is_active:
                user.deactivate()
        
        return await self._safe_db_operation(self.user_repository.update, user)
    
    async def _link_tst_id_to_existing_user(self, user: Any, tst_data: TSTIdUserData) -> Any:
        """Привязывает TST ID к существующему пользователю"""
        # Проверяем, что у пользователя еще нет TST ID
        if hasattr(user, 'tst_id') and user.tst_id is not None:
            raise TSTIdAuthError("User already linked to different TST ID")
        
        if self.user_mapper:
            user = self.user_mapper.link_tst_id_to_user(user, tst_data)
        else:
            # Стандартная привязка
            if hasattr(user, 'tst_id'):
                user.tst_id = tst_data.tst_id
            if hasattr(user, 'update_tst_info'):
                user.update_tst_info(
                    username=tst_data.username,
                    tst_role=tst_data.role,
                    position_id=tst_data.position_id,
                    github_token=tst_data.github_token
                )
            if hasattr(user, 'verify_email') and self.config.auto_verify_tst_users:
                user.verify_email()
        
        return await self._safe_db_operation(self.user_repository.update, user)
    
    async def _create_new_user(self, tst_data: TSTIdUserData) -> Any:
        """Создает нового пользователя"""
        if self.user_mapper:
            user = self.user_mapper.create_user_from_tst_data(tst_data)
        else:
            # Стандартное создание пользователя
            # Тут нужна фабрика пользователей или конструктор
            # Это зависит от конкретной реализации
            raise TSTIdIntegrationError(
                "User mapper is required for creating new users. "
                "Please provide user_mapper in TSTIdAuthenticator constructor."
            )
        
        return await self._safe_db_operation(self.user_repository.save, user)
    
    def _generate_tokens(self, user: Any) -> TokenResponse:
        """Генерирует токены для пользователя"""
        # Получаем ID пользователя
        user_id = getattr(user, 'id', None)
        if user_id is None:
            raise TSTIdIntegrationError("User object must have 'id' attribute")
        
        # Получаем email пользователя
        email = getattr(user, 'email', None)
        if email is None:
            raise TSTIdIntegrationError("User object must have 'email' attribute")
        
        # Генерируем токены
        tokens = self.jwt_service.create_token_pair(user_id, email)
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens.get("token_type", "bearer"),
            expires_in=self.jwt_service.access_token_expire_minutes * 60
        )
    
    def _build_user_response(self, user: Any, tst_data: TSTIdUserData) -> TSTIdUserResponse:
        """Формирует ответ с данными пользователя"""
        if self.user_mapper:
            user_dict = self.user_mapper.to_response_model(user)
            return TSTIdUserResponse(**user_dict)
        else:
            # Стандартное формирование ответа
            return TSTIdUserResponse(
                id=str(getattr(user, 'id', '')),
                email=getattr(user, 'email', ''),
                full_name=getattr(user, 'full_name', ''),
                is_active=getattr(user, 'is_active', True),
                is_verified=getattr(user, 'is_verified', False),
                tst_id=getattr(user, 'tst_id', tst_data.tst_id),
                username=getattr(user, 'username', tst_data.username),
                role=getattr(user, 'tst_role', tst_data.role),
                position_id=getattr(user, 'position_id', tst_data.position_id),
                position=None,  # TODO: Implement position fetching
                github_token=getattr(user, 'github_token', tst_data.github_token),
                created_at=getattr(user, 'created_at', '').isoformat() if hasattr(getattr(user, 'created_at', ''), 'isoformat') else str(getattr(user, 'created_at', '')),
                updated_at=getattr(user, 'updated_at', '').isoformat() if hasattr(getattr(user, 'updated_at', ''), 'isoformat') else str(getattr(user, 'updated_at', ''))
            ) 