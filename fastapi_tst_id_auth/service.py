"""TST ID Service - основной сервис для работы с TST ID API"""

from typing import Dict, Any, Optional
import aiohttp
from urllib.parse import urljoin
import logging

from .config import TSTIdConfig, default_config
from .schemas import TSTIdUserInfo, TSTIdUserData
from .exceptions import (
    TSTIdAPIError,
    TSTIdValidationError,
    TSTIdUserNotFoundError
)
from .interfaces import HTTPClientInterface, LoggerInterface


class DefaultHTTPClient(HTTPClientInterface):
    """Дефолтная реализация HTTP клиента на основе aiohttp"""
    
    async def get(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Выполняет GET запрос"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    text = await response.text()
                    raise TSTIdAPIError(
                        f"HTTP {response.status}: {text}",
                        status_code=response.status
                    )
    
    async def post(
        self, 
        url: str, 
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Выполняет POST запрос"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                json=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    text = await response.text()
                    raise TSTIdAPIError(
                        f"HTTP {response.status}: {text}",
                        status_code=response.status
                    )


class DefaultLogger(LoggerInterface):
    """Дефолтная реализация логгера"""
    
    def __init__(self, name: str = "fastapi_tst_id_auth"):
        self.logger = logging.getLogger(name)
    
    def info(self, message: str, **kwargs) -> None:
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        self.logger.debug(message, extra=kwargs)


class TSTIdService:
    """Сервис для работы с TST ID API"""
    
    def __init__(
        self,
        config: Optional[TSTIdConfig] = None,
        http_client: Optional[HTTPClientInterface] = None,
        logger: Optional[LoggerInterface] = None
    ):
        self.config = config or default_config
        self.http_client = http_client or DefaultHTTPClient()
        self.logger = logger or DefaultLogger()
        
        # Настройка логирования
        if self.config.enable_debug_logging:
            logging.getLogger("fastapi_tst_id_auth").setLevel(logging.DEBUG)
    
    @property
    def auth_url(self) -> str:
        """Получает полный URL для авторизации"""
        return urljoin(self.config.tst_id_base_url, self.config.tst_id_auth_endpoint)
    
    async def get_user_info(self, jwt_token: str) -> TSTIdUserInfo:
        """
        Получает информацию о пользователе из TST ID API
        
        Args:
            jwt_token: JWT токен от TST ID
            
        Returns:
            TSTIdUserInfo: Информация о пользователе
            
        Raises:
            TSTIdValidationError: При неверном токене
            TSTIdAPIError: При ошибке API
            TSTIdUserNotFoundError: Если пользователь не найден
        """
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        try:
            self.logger.debug("Запрос информации о пользователе из TST ID", url=self.auth_url)
            
            response_data = await self.http_client.get(
                url=self.auth_url,
                headers=headers,
                timeout=self.config.tst_id_timeout
            )
            
            # Валидируем ответ через Pydantic
            user_info = TSTIdUserInfo(**response_data)
            
            self.logger.info(
                "Пользователь успешно получен из TST ID",
                user_id=user_info.id,
                email=user_info.email
            )
            
            return user_info
            
        except aiohttp.ClientError as e:
            self.logger.error("Ошибка сети при обращении к TST ID", error=str(e))
            raise TSTIdAPIError(f"Network error: {str(e)}")
            
        except TSTIdAPIError as e:
            if e.status_code == 401:
                self.logger.warning("Неверный TST ID токен")
                raise TSTIdValidationError("Invalid TST ID token")
            elif e.status_code == 404:
                self.logger.warning("Пользователь не найден в TST ID")
                raise TSTIdUserNotFoundError("User not found in TST ID")
            else:
                self.logger.error("Ошибка TST ID API", status_code=e.status_code, error=e.message)
                raise
                
        except Exception as e:
            self.logger.error("Неожиданная ошибка при обращении к TST ID", error=str(e))
            raise TSTIdAPIError(f"Unexpected error: {str(e)}")
    
    def normalize_user_data(self, user_info: TSTIdUserInfo) -> TSTIdUserData:
        """
        Нормализует данные пользователя из TST ID
        
        Args:
            user_info: Информация о пользователе от TST ID
            
        Returns:
            TSTIdUserData: Нормализованные данные
        """
        return TSTIdUserData(
            email=user_info.email,
            full_name=user_info.full_name,
            username=user_info.username,
            tst_id=user_info.id,
            role=user_info.role,
            position_id=user_info.position_id,
            position=user_info.position.dict() if user_info.position else None,
            is_active=user_info.is_active,
            github_token=user_info.github_token,
            tst_created_at=user_info.created_at,
            tst_updated_at=user_info.updated_at
        )
    
    async def validate_and_get_user_data(self, jwt_token: str) -> TSTIdUserData:
        """
        Валидирует токен и возвращает нормализованные данные пользователя
        
        Args:
            jwt_token: JWT токен от TST ID
            
        Returns:
            TSTIdUserData: Нормализованные данные пользователя
        """
        user_info = await self.get_user_info(jwt_token)
        return self.normalize_user_data(user_info) 