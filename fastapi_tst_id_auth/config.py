"""Конфигурация для TST ID Auth"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class TSTIdConfig(BaseSettings):
    """Настройки для TST ID авторизации"""
    
    # TST ID API settings
    tst_id_base_url: str = Field(
        default="https://id.tstservice.tech",
        description="Базовый URL TST ID API"
    )
    tst_id_auth_endpoint: str = Field(
        default="/api/v1/auth/me",
        description="Эндпоинт для получения информации о пользователе"
    )
    tst_id_timeout: int = Field(
        default=30,
        description="Таймаут запросов к TST ID API в секундах"
    )
    
    # Connection settings
    tst_id_max_retries: int = Field(
        default=3,
        description="Максимальное количество попыток подключения"
    )
    tst_id_retry_delay: int = Field(
        default=1,
        description="Задержка между попытками подключения в секундах"
    )
    tst_id_connection_pool_size: int = Field(
        default=10,
        description="Размер пула соединений"
    )
    tst_id_keepalive_timeout: int = Field(
        default=30,
        description="Таймаут keep-alive соединений"
    )
    
    # Auth settings
    auto_create_users: bool = Field(
        default=True,
        description="Автоматически создавать пользователей при первом входе"
    )
    auto_verify_tst_users: bool = Field(
        default=True,
        description="Автоматически верифицировать пользователей из TST ID"
    )
    link_existing_users: bool = Field(
        default=True,
        description="Привязывать TST ID к существующим пользователям по email"
    )
    
    # Cache settings (опционально)
    cache_user_info: bool = Field(
        default=False,
        description="Кешировать информацию о пользователях"
    )
    cache_ttl_seconds: int = Field(
        default=300,
        description="Время жизни кеша в секундах"
    )
    
    # Logging
    enable_debug_logging: bool = Field(
        default=False,
        description="Включить отладочное логирование"
    )
    
    class Config:
        env_prefix = "TST_ID_"
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Игнорируем дополнительные поля из .env


# Глобальный экземпляр конфигурации
default_config = TSTIdConfig() 