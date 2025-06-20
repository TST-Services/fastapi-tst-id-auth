"""FastAPI Router для TST ID авторизации"""

from typing import Callable, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from .schemas import TSTIdLoginRequest, TSTIdLoginResponse
from .auth import TSTIdAuthenticator
from .dependencies import (
    get_tst_service,
    get_user_repository,
    get_jwt_service,
    get_user_mapper
)
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
    TSTIdAPIError,
    TSTIdIntegrationError
)


def create_tst_auth_router(
    user_repository_dependency: Callable[[], UserRepositoryInterface],
    jwt_service_dependency: Callable[[], JWTServiceInterface],
    user_mapper_dependency: Optional[Callable[[], UserMapperInterface]] = None,
    prefix: str = "/auth",
    tags: Optional[list] = None
) -> APIRouter:
    """
    Создает готовый роутер для TST ID авторизации
    
    Args:
        user_repository_dependency: Зависимость для получения репозитория пользователей
        jwt_service_dependency: Зависимость для получения JWT сервиса
        user_mapper_dependency: Зависимость для получения маппера пользователей (опционально)
        prefix: Префикс для роутера
        tags: Теги для группировки в документации
        
    Returns:
        APIRouter: Настроенный роутер
    """
    router = APIRouter(
        prefix=prefix,
        tags=tags or ["TST ID Authentication"]
    )
    
    @router.post("/tst-id/login", response_model=TSTIdLoginResponse)
    async def tst_id_login(
        request: TSTIdLoginRequest,
        tst_service: TSTIdService = Depends(get_tst_service),
        user_repository: UserRepositoryInterface = Depends(user_repository_dependency),
        jwt_service: JWTServiceInterface = Depends(jwt_service_dependency),
        user_mapper: Optional[UserMapperInterface] = Depends(user_mapper_dependency) if user_mapper_dependency else None
    ):
        """
        Авторизация через TST ID
        
        - **tst_token**: JWT токен от TST ID сервиса
        
        Возвращает пользователя и токены для дальнейшей работы с API.
        """
        try:
            authenticator = TSTIdAuthenticator(
                user_repository=user_repository,
                jwt_service=jwt_service,
                tst_service=tst_service,
                user_mapper=user_mapper
            )
            
            return await authenticator.authenticate(request.tst_token)
            
        except TSTIdValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid TST ID token: {str(e)}"
            )
        except TSTIdUserNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found: {str(e)}"
            )
        except TSTIdAPIError as e:
            if e.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid TST ID token"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"TST ID service error: {str(e)}"
                )
        except TSTIdIntegrationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Integration error: {str(e)}"
            )
        except TSTIdAuthError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication failed: {str(e)}"
            )
    
    return router


def create_simple_tst_auth_router(
    prefix: str = "/auth",
    tags: Optional[list] = None
) -> APIRouter:
    """
    Создает упрощенный роутер для TST ID авторизации с глобальными зависимостями
    
    Использует глобально настроенные зависимости через configure_dependencies()
    
    Args:
        prefix: Префикс для роутера
        tags: Теги для группировки в документации
        
    Returns:
        APIRouter: Настроенный роутер
    """
    router = APIRouter(
        prefix=prefix,
        tags=tags or ["TST ID Authentication"]
    )
    
    @router.post("/tst-id/login", response_model=TSTIdLoginResponse)
    async def tst_id_login(
        request: TSTIdLoginRequest,
        tst_service: TSTIdService = Depends(get_tst_service),
        user_repository: UserRepositoryInterface = Depends(get_user_repository),
        jwt_service: JWTServiceInterface = Depends(get_jwt_service),
        user_mapper: Optional[UserMapperInterface] = Depends(get_user_mapper)
    ):
        """
        Авторизация через TST ID
        
        - **tst_token**: JWT токен от TST ID сервиса
        
        Возвращает пользователя и токены для дальнейшей работы с API.
        """
        try:
            authenticator = TSTIdAuthenticator(
                user_repository=user_repository,
                jwt_service=jwt_service,
                tst_service=tst_service,
                user_mapper=user_mapper
            )
            
            return await authenticator.authenticate(request.tst_token)
            
        except TSTIdValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid TST ID token: {str(e)}"
            )
        except TSTIdUserNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found: {str(e)}"
            )
        except TSTIdAPIError as e:
            if e.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid TST ID token"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"TST ID service error: {str(e)}"
                )
        except TSTIdIntegrationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Integration error: {str(e)}"
            )
        except TSTIdAuthError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication failed: {str(e)}"
            )
    
    return router


# Удобные функции для быстрого создания роутеров
def setup_tst_auth(
    app,
    user_repository_dependency: Callable[[], UserRepositoryInterface],
    jwt_service_dependency: Callable[[], JWTServiceInterface],
    user_mapper_dependency: Optional[Callable[[], UserMapperInterface]] = None,
    prefix: str = "/api/v1/auth",
    tags: Optional[list] = None
) -> None:
    """
    Быстрая настройка TST ID авторизации для FastAPI приложения
    
    Args:
        app: FastAPI приложение
        user_repository_dependency: Зависимость для получения репозитория пользователей
        jwt_service_dependency: Зависимость для получения JWT сервиса
        user_mapper_dependency: Зависимость для получения маппера пользователей (опционально)
        prefix: Префикс для роутера
        tags: Теги для группировки в документации
    """
    router = create_tst_auth_router(
        user_repository_dependency=user_repository_dependency,
        jwt_service_dependency=jwt_service_dependency,
        user_mapper_dependency=user_mapper_dependency,
        prefix="",  # Префикс задается при включении
        tags=tags
    )
    
    app.include_router(router, prefix=prefix) 