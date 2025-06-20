"""Исключения для TST ID Auth"""

from typing import Optional, Any, Dict


class TSTIdAuthError(Exception):
    """Базовое исключение для TST ID Auth"""
    
    def __init__(
        self, 
        message: str = "TST ID authentication error", 
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class TSTIdValidationError(TSTIdAuthError):
    """Ошибка валидации TST ID токена"""
    
    def __init__(
        self, 
        message: str = "Invalid TST ID token", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)


class TSTIdUserNotFoundError(TSTIdAuthError):
    """Пользователь не найден в TST ID"""
    
    def __init__(
        self, 
        message: str = "User not found in TST ID", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)


class TSTIdAPIError(TSTIdAuthError):
    """Ошибка при обращении к TST ID API"""
    
    def __init__(
        self, 
        message: str = "TST ID API error", 
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        super().__init__(message, details)


class TSTIdConfigError(TSTIdAuthError):
    """Ошибка конфигурации TST ID"""
    
    def __init__(
        self, 
        message: str = "TST ID configuration error", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)


class TSTIdIntegrationError(TSTIdAuthError):
    """Ошибка интеграции с пользовательской системой"""
    
    def __init__(
        self, 
        message: str = "TST ID integration error", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details) 