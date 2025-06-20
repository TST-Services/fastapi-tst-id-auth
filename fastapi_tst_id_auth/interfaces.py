"""Интерфейсы для интеграции TST ID Auth с пользовательскими системами"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, Union
from uuid import UUID

from .schemas import TSTIdUserData, TokenResponse


class UserRepositoryInterface(ABC):
    """Интерфейс репозитория пользователей"""
    
    @abstractmethod
    async def find_by_tst_id(self, tst_id: int) -> Optional[Any]:
        """Находит пользователя по TST ID"""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[Any]:
        """Находит пользователя по email"""
        pass
    
    @abstractmethod
    async def save(self, user: Any) -> Any:
        """Сохраняет пользователя"""
        pass
    
    @abstractmethod
    async def update(self, user: Any) -> Any:
        """Обновляет пользователя"""
        pass
    
    @abstractmethod
    async def exists_by_tst_id(self, tst_id: int) -> bool:
        """Проверяет существование пользователя по TST ID"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Проверяет существование пользователя по email"""
        pass


class JWTServiceInterface(ABC):
    """Интерфейс сервиса JWT токенов"""
    
    @abstractmethod
    def create_token_pair(self, user_id: Union[str, UUID], email: str) -> Dict[str, str]:
        """Создает пару токенов (access + refresh)"""
        pass
    
    @abstractmethod
    def create_access_token(self, user_id: Union[str, UUID], email: str) -> str:
        """Создает access токен"""
        pass
    
    @abstractmethod
    def create_refresh_token(self, user_id: Union[str, UUID], email: str) -> str:
        """Создает refresh токен"""
        pass
    
    @abstractmethod
    def validate_access_token(self, token: str) -> Dict[str, Any]:
        """Валидирует access токен"""
        pass
    
    @property
    @abstractmethod
    def access_token_expire_minutes(self) -> int:
        """Время жизни access токена в минутах"""
        pass


class UserMapperInterface(ABC):
    """Интерфейс маппера пользователей"""
    
    @abstractmethod
    def create_user_from_tst_data(self, tst_data: TSTIdUserData) -> Any:
        """Создает пользователя из данных TST ID"""
        pass
    
    @abstractmethod
    def update_user_with_tst_data(self, user: Any, tst_data: TSTIdUserData) -> Any:
        """Обновляет пользователя данными из TST ID"""
        pass
    
    @abstractmethod
    def link_tst_id_to_user(self, user: Any, tst_data: TSTIdUserData) -> Any:
        """Привязывает TST ID к существующему пользователю"""
        pass
    
    @abstractmethod
    def to_response_model(self, user: Any) -> Dict[str, Any]:
        """Преобразует пользователя в схему ответа"""
        pass


class UserFactoryInterface(ABC):
    """Интерфейс фабрики пользователей"""
    
    @abstractmethod
    def create_user(
        self,
        email: str,
        full_name: str,
        tst_id: int,
        username: str,
        role: str,
        **kwargs
    ) -> Any:
        """Создает нового пользователя"""
        pass


class CacheInterface(ABC):
    """Интерфейс кеша для TST ID данных"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Получает значение из кеша"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Сохраняет значение в кеш"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Удаляет значение из кеша"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Очищает весь кеш"""
        pass


class LoggerInterface(ABC):
    """Интерфейс логгера"""
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Логирует информационное сообщение"""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Логирует предупреждение"""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Логирует ошибку"""
        pass
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Логирует отладочное сообщение"""
        pass


class HTTPClientInterface(ABC):
    """Интерфейс HTTP клиента"""
    
    @abstractmethod
    async def get(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Выполняет GET запрос"""
        pass
    
    @abstractmethod
    async def post(
        self, 
        url: str, 
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Выполняет POST запрос"""
        pass 