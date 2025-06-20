# FastAPI TST ID Auth

🚀 **Простая и гибкая OAuth интеграция с TST ID для FastAPI приложений**

[![PyPI version](https://badge.fury.io/py/fastapi-tst-id-auth.svg)](https://badge.fury.io/py/fastapi-tst-id-auth)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Особенности

- 🔐 **Готовая OAuth интеграция** с TST ID сервисом
- 🚀 **Простая интеграция** - всего несколько строк кода
- 🔧 **Гибкая настройка** - адаптируется под любую архитектуру
- 📦 **Готовые роутеры** - подключай и используй
- 🛡️ **Типобезопасность** - полная поддержка TypeScript-style типов
- 🧪 **Тестируемость** - легко мокать и тестировать
- 📚 **Подробная документация** - с примерами для всех случаев

## 📦 Установка

```bash
pip install fastapi-tst-id-auth
```

Или с дополнительными зависимостями для разработки:

```bash
pip install fastapi-tst-id-auth[dev]
```

## 🚀 Быстрый старт

### 1. Простейшая интеграция

```python
from fastapi import FastAPI
from fastapi_tst_id_auth import setup_tst_auth

app = FastAPI()

# Подключаем TST ID авторизацию
setup_tst_auth(
    app,
    user_repository_dependency=get_user_repository,
    jwt_service_dependency=get_jwt_service
)

# Готово! Теперь доступен POST /api/v1/auth/tst-id/login
```

### 2. Использование в защищенных роутах

```python
from fastapi import Depends
from fastapi_tst_id_auth import get_current_tst_user

@app.get("/protected")
async def protected_endpoint(
    current_user = Depends(get_current_tst_user)
):
    return {"message": f"Hello {current_user.username}!"}
```

### 3. Кастомная интеграция

```python
from fastapi_tst_id_auth import (
    create_tst_auth_router,
    TSTIdAuthenticator,
    TSTIdService
)

# Создаем кастомный роутер
auth_router = create_tst_auth_router(
    user_repository_dependency=get_user_repository,
    jwt_service_dependency=get_jwt_service,
    user_mapper_dependency=get_user_mapper,
    prefix="/custom-auth",
    tags=["Custom TST Auth"]
)

app.include_router(auth_router)
```

## 🔧 Конфигурация

### Переменные окружения

```bash
# TST ID API настройки
TST_ID_BASE_URL=https://id.tstservice.tech
TST_ID_AUTH_ENDPOINT=/api/v1/auth/me
TST_ID_TIMEOUT=30

# Настройки авторизации
TST_ID_AUTO_CREATE_USERS=true
TST_ID_AUTO_VERIFY_TST_USERS=true
TST_ID_LINK_EXISTING_USERS=true

# Кеширование
TST_ID_CACHE_USER_INFO=false
TST_ID_CACHE_TTL_SECONDS=300

# Отладка
TST_ID_ENABLE_DEBUG_LOGGING=false
```

### Программная конфигурация

```python
from fastapi_tst_id_auth import TSTIdConfig

config = TSTIdConfig(
    tst_id_base_url="https://id.tstservice.tech",
    auto_create_users=True,
    auto_verify_tst_users=True,
    enable_debug_logging=True
)
```

## 🏗️ Архитектура интеграции

### Необходимые интерфейсы

Пакет требует реализации нескольких интерфейсов для интеграции с вашей системой:

#### 1. UserRepository

```python
from fastapi_tst_id_auth import UserRepositoryInterface

class MyUserRepository(UserRepositoryInterface):
    async def find_by_tst_id(self, tst_id: int):
        # Найти пользователя по TST ID
        pass
    
    async def find_by_email(self, email: str):
        # Найти пользователя по email
        pass
    
    async def save(self, user):
        # Сохранить пользователя
        pass
    
    async def update(self, user):
        # Обновить пользователя
        pass
```

#### 2. JWTService

```python
from fastapi_tst_id_auth import JWTServiceInterface

class MyJWTService(JWTServiceInterface):
    def create_token_pair(self, user_id, email):
        # Создать access и refresh токены
        return {
            "access_token": "...",
            "refresh_token": "...",
            "token_type": "bearer"
        }
    
    def validate_access_token(self, token: str):
        # Валидировать и декодировать токен
        return {"user_id": "...", "email": "..."}
    
    @property
    def access_token_expire_minutes(self) -> int:
        return 30
```

#### 3. UserMapper (опционально)

```python
from fastapi_tst_id_auth import UserMapperInterface, TSTIdUserData

class MyUserMapper(UserMapperInterface):
    def create_user_from_tst_data(self, tst_data: TSTIdUserData):
        # Создать пользователя из данных TST ID
        return MyUser(
            email=tst_data.email,
            full_name=tst_data.full_name,
            tst_id=tst_data.tst_id,
            # ...
        )
    
    def update_user_with_tst_data(self, user, tst_data: TSTIdUserData):
        # Обновить пользователя данными TST ID
        user.username = tst_data.username
        user.tst_role = tst_data.role
        return user
    
    def to_response_model(self, user):
        # Преобразовать в схему ответа
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            # ...
        }
```

## 📋 Примеры использования

### Пример с SQLAlchemy

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_tst_id_auth import setup_tst_auth

app = FastAPI()

# Ваши зависимости
def get_db_session() -> AsyncSession:
    # Возвращает сессию базы данных
    pass

def get_user_repository(session: AsyncSession = Depends(get_db_session)):
    return SQLAlchemyUserRepository(session)

def get_jwt_service():
    return JWTService()

# Подключаем TST ID авторизацию
setup_tst_auth(
    app,
    user_repository_dependency=get_user_repository,
    jwt_service_dependency=get_jwt_service
)
```

### Пример с пользовательским маппером

```python
from fastapi_tst_id_auth import create_tst_auth_router

class UserMapper(UserMapperInterface):
    def create_user_from_tst_data(self, tst_data):
        return User(
            email=tst_data.email,
            full_name=tst_data.full_name,
            tst_id=tst_data.tst_id,
            username=tst_data.username,
            is_verified=True,  # TST пользователи авто-верифицированы
            tst_role=tst_data.role,
            position_id=tst_data.position_id,
            github_token=tst_data.github_token
        )

def get_user_mapper():
    return UserMapper()

router = create_tst_auth_router(
    user_repository_dependency=get_user_repository,
    jwt_service_dependency=get_jwt_service,
    user_mapper_dependency=get_user_mapper
)

app.include_router(router, prefix="/api/v1")
```

## 🔐 API Документация

### POST /auth/tst-id/login

Авторизация через TST ID токен.

**Запрос:**
```json
{
  "tst_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Ответ:**
```json
{
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "is_verified": true,
    "tst_id": 123,
    "username": "johndoe",
    "role": "user",
    "position_id": 1,
    "position": null,
    "github_token": "ghp_...",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

## 🛡️ Безопасность

- ✅ Токены TST ID валидируются через официальный API
- ✅ Поддержка автоматической верификации пользователей
- ✅ Гибкая настройка создания пользователей
- ✅ Защита от повторной привязки TST ID
- ✅ Таймауты для предотвращения зависания

## 🧪 Тестирование

### Модульные тесты

```python
import pytest
from fastapi_tst_id_auth import TSTIdService, TSTIdAuthenticator

@pytest.mark.asyncio
async def test_tst_service():
    service = TSTIdService()
    
    # Мокаем HTTP клиент
    mock_client = MockHTTPClient()
    service.http_client = mock_client
    
    user_data = await service.validate_and_get_user_data("mock_token")
    
    assert user_data.email == "test@example.com"
    assert user_data.tst_id == 123
```

### Интеграционные тесты

```python
from fastapi.testclient import TestClient

def test_tst_login():
    client = TestClient(app)
    
    response = client.post("/api/v1/auth/tst-id/login", json={
        "tst_token": "valid_token"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "tokens" in data
```

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Настройки TST ID через переменные окружения
ENV TST_ID_BASE_URL=https://id.tstservice.tech
ENV TST_ID_AUTO_CREATE_USERS=true

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Переменные окружения в production

```bash
TST_ID_BASE_URL=https://id.tstservice.tech
TST_ID_TIMEOUT=10
TST_ID_AUTO_CREATE_USERS=true
TST_ID_AUTO_VERIFY_TST_USERS=true
TST_ID_ENABLE_DEBUG_LOGGING=false
```

## 🤝 Содействие

Мы приветствуем ваши предложения! Пожалуйста:

1. Форкните репозиторий
2. Создайте ветку для вашей функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - смотрите файл [LICENSE](LICENSE) для деталей.

## 🙏 Благодарности

- [FastAPI](https://fastapi.tiangolo.com/) - за отличный веб-фреймворк
- [Pydantic](https://pydantic-docs.helpmanual.io/) - за валидацию данных
- [aiohttp](https://docs.aiohttp.org/) - за асинхронные HTTP запросы

## 📞 Поддержка

- 📧 Email: support@tstservice.tech
- 🐛 Issues: [GitHub Issues](https://github.com/tst-team/fastapi-tst-id-auth/issues)
- 📖 Документация: [GitHub Pages](https://tst-team.github.io/fastapi-tst-id-auth/)
- 🌐 TST ID Service: [id.tstservice.tech](https://id.tstservice.tech)

---

**Сделано с ❤️ командой TST** 