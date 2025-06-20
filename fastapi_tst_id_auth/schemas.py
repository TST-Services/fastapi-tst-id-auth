"""Pydantic схемы для TST ID Auth"""

from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class TSTIdLoginRequest(BaseModel):
    """Схема запроса для входа через TST ID"""
    tst_token: str = Field(..., description="JWT токен от TST ID")


class TSTIdPositionResponse(BaseModel):
    """Схема должности в TST ID"""
    id: int = Field(..., description="ID должности")
    name: str = Field(..., description="Название должности")
    description: Optional[str] = Field(None, description="Описание должности")
    is_active: bool = Field(..., description="Активна ли должность")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class TSTIdUserResponse(BaseModel):
    """Схема пользователя TST ID"""
    id: str = Field(..., description="ID пользователя в локальной системе")
    email: str = Field(..., description="Email пользователя")
    full_name: str = Field(..., description="Полное имя пользователя")
    is_active: bool = Field(..., description="Активен ли пользователь")
    is_verified: bool = Field(..., description="Подтвержден ли email")
    
    # TST ID specific fields
    tst_id: int = Field(..., description="ID пользователя в TST ID")
    username: str = Field(..., description="Имя пользователя в TST ID")
    role: str = Field(..., description="Роль пользователя в TST ID")
    position_id: Optional[int] = Field(None, description="ID должности")
    position: Optional[TSTIdPositionResponse] = Field(None, description="Должность пользователя")
    github_token: Optional[str] = Field(None, description="GitHub токен")
    
    created_at: str = Field(..., description="Дата создания")
    updated_at: str = Field(..., description="Дата обновления")


class TokenResponse(BaseModel):
    """Схема ответа с токенами"""
    access_token: str = Field(..., description="Access токен")
    refresh_token: str = Field(..., description="Refresh токен")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни access токена в секундах")


class TSTIdLoginResponse(BaseModel):
    """Схема ответа при входе через TST ID"""
    user: TSTIdUserResponse = Field(..., description="Данные пользователя")
    tokens: TokenResponse = Field(..., description="Токены аутентификации")


class TSTIdUserInfo(BaseModel):
    """Схема информации о пользователе от TST ID API"""
    username: str = Field(..., description="Имя пользователя")
    email: str = Field(..., description="Email пользователя")
    full_name: str = Field(..., description="Полное имя")
    role: str = Field(..., description="Роль пользователя")
    position_id: Optional[int] = Field(None, description="ID должности")
    is_active: bool = Field(..., description="Активен ли пользователь")
    github_token: Optional[str] = Field(None, description="GitHub токен")
    id: int = Field(..., description="ID пользователя в TST ID")
    position: Optional[TSTIdPositionResponse] = Field(None, description="Должность")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class TSTIdAuthConfig(BaseModel):
    """Схема конфигурации для TST ID авторизации"""
    base_url: str = Field(..., description="Базовый URL TST ID")
    auth_endpoint: str = Field(..., description="Эндпоинт авторизации")
    timeout: int = Field(default=30, description="Таймаут запросов")
    auto_create_users: bool = Field(default=True, description="Автосоздание пользователей")
    auto_verify_users: bool = Field(default=True, description="Автоверификация пользователей")
    link_existing_users: bool = Field(default=True, description="Привязка к существующим пользователям")


class TSTIdUserData(BaseModel):
    """Нормализованные данные пользователя"""
    email: str
    full_name: str
    username: str
    tst_id: int
    role: str
    position_id: Optional[int] = None
    position: Optional[Dict[str, Any]] = None
    is_active: bool = True
    github_token: Optional[str] = None
    tst_created_at: Optional[datetime] = None
    tst_updated_at: Optional[datetime] = None 