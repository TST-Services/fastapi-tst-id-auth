"""
FastAPI TST ID Auth - OAuth интеграция с TST ID для FastAPI приложений

Простая и гибкая библиотека для интеграции авторизации через TST ID в FastAPI проекты.
"""

__version__ = "0.1.0"
__author__ = "TST Team"
__email__ = "support@tstservice.tech"

from .config import TSTIdConfig
from .service import TSTIdService
from .schemas import (
    TSTIdLoginRequest,
    TSTIdLoginResponse,
    TSTIdUserResponse,
    TSTIdPositionResponse
)
from .dependencies import (
    get_tst_service,
    get_current_tst_user,
    TSTIdUserDependency
)
from .router import create_tst_auth_router
from .interfaces import (
    UserRepositoryInterface,
    JWTServiceInterface,
    UserMapperInterface
)
from .exceptions import (
    TSTIdAuthError,
    TSTIdValidationError,
    TSTIdUserNotFoundError
)

__all__ = [
    # Core components
    "TSTIdConfig",
    "TSTIdService",
    
    # Schemas
    "TSTIdLoginRequest",
    "TSTIdLoginResponse", 
    "TSTIdUserResponse",
    "TSTIdPositionResponse",
    
    # Dependencies
    "get_tst_service",
    "get_current_tst_user",
    "TSTIdUserDependency",
    
    # Router
    "create_tst_auth_router",
    
    # Interfaces
    "UserRepositoryInterface",
    "JWTServiceInterface",
    "UserMapperInterface",
    
    # Exceptions
    "TSTIdAuthError",
    "TSTIdValidationError",
    "TSTIdUserNotFoundError",
    
    # Version info
    "__version__",
] 