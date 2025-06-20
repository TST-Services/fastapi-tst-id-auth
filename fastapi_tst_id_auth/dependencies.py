"""FastAPI Dependencies для TST ID Auth"""

from typing import Callable, Optional, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import TSTIdConfig, default_config
from .service import TSTIdService
from .interfaces import (
    UserRepositoryInterface,
    JWTServiceInterface,
    UserMapperInterface
)
from .exceptions import (
    TSTIdAuthError,
    TSTIdValidationError,
    TSTIdUserNotFoundError,
    TSTIdAPIError
)


# Глобальные переменные для хранения пользовательских зависимостей
_user_repository_dependency: Optional[Callable] = None
_jwt_service_dependency: Optional[Callable] = None
_user_mapper_dependency: Optional[Callable] = None

# Security scheme
security = HTTPBearer()


def configure_dependencies(
    user_repository_dependency: Callable,
    jwt_service_dependency: Callable,
    user_mapper_dependency: Optional[Callable] = None
) -> None:
    """
    Конфигурирует пользовательские зависимости
    
    Args:
        user_repository_dependency: Зависимость для получения репозитория пользователей
        jwt_service_dependency: Зависимость для получения JWT сервиса
        user_mapper_dependency: Зависимость для получения маппера пользователей (опционально)
    """
    global _user_repository_dependency, _jwt_service_dependency, _user_mapper_dependency
    
    _user_repository_dependency = user_repository_dependency
    _jwt_service_dependency = jwt_service_dependency
    _user_mapper_dependency = user_mapper_dependency


async def get_tst_config() -> TSTIdConfig:
    """Получает конфигурацию TST ID"""
    return default_config


async def get_tst_service(
    config: TSTIdConfig = Depends(get_tst_config)
) -> TSTIdService:
    """Получает сервис TST ID"""
    return TSTIdService(config=config)


def get_user_repository() -> UserRepositoryInterface:
    """Получает репозиторий пользователей"""
    if _user_repository_dependency is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User repository dependency not configured. Call configure_dependencies() first."
        )
    return _user_repository_dependency()


def get_jwt_service() -> JWTServiceInterface:
    """Получает JWT сервис"""
    if _jwt_service_dependency is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT service dependency not configured. Call configure_dependencies() first."
        )
    return _jwt_service_dependency()


def get_user_mapper() -> Optional[UserMapperInterface]:
    """Получает маппер пользователей"""
    if _user_mapper_dependency is None:
        return None
    return _user_mapper_dependency()


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_service: JWTServiceInterface = Depends(get_jwt_service),
    user_repository: UserRepositoryInterface = Depends(get_user_repository)
) -> Any:
    """
    Получает текущего пользователя из JWT токена
    
    Args:
        credentials: Учетные данные из Authorization header
        jwt_service: Сервис для работы с JWT
        user_repository: Репозиторий пользователей
        
    Returns:
        Пользователь из базы данных
        
    Raises:
        HTTPException: При ошибке аутентификации
    """
    try:
        # Валидируем токен
        payload = jwt_service.validate_access_token(credentials.credentials)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Получаем пользователя из базы
        # Поддерживаем как UUID, так и строковые ID
        if hasattr(user_repository, 'find_by_id'):
            user = await user_repository.find_by_id(user_id)
        else:
            # Fallback для кастомных репозиториев
            user = await user_repository.find_by_email(payload.get("email", ""))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Проверяем активность пользователя
        if hasattr(user, 'is_active') and not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_tst_user(
    current_user: Any = Depends(get_current_user_from_token)
) -> Any:
    """
    Получает текущего пользователя TST ID
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        Пользователь TST ID
        
    Raises:
        HTTPException: Если пользователь не является TST ID пользователем
    """
    # Проверяем, что пользователь является TST ID пользователем
    if hasattr(current_user, 'tst_id'):
        if current_user.tst_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="TST ID authentication required"
            )
    elif hasattr(current_user, 'is_tst_user'):
        if not current_user.is_tst_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="TST ID authentication required"
            )
    else:
        # Если нет способа проверить TST ID, просто возвращаем пользователя
        pass
    
    return current_user


async def get_current_active_user(
    current_user: Any = Depends(get_current_user_from_token)
) -> Any:
    """
    Получает текущего активного пользователя
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        Активный пользователь
        
    Raises:
        HTTPException: Если пользователь неактивен
    """
    if hasattr(current_user, 'is_active') and not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: Any = Depends(get_current_user_from_token)
) -> Any:
    """
    Получает текущего верифицированного пользователя
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        Верифицированный пользователь
        
    Raises:
        HTTPException: Если пользователь не верифицирован
    """
    if hasattr(current_user, 'is_verified') and not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    return current_user


# Alias для удобства использования
TSTIdUserDependency = Depends(get_current_tst_user) 