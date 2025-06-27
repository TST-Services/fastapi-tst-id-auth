# 🚀 Интеграция fastapi-tst-id-auth

Простая и быстрая интеграция TST ID авторизации в ваш FastAPI проект.

## 📦 Установка

```bash
pip install git+https://github.com/TST-Services/fastapi-tst-id-auth.git
```

## ⚡ Быстрый старт

### 1. Настройка переменных окружения

Создайте `.env` файл:

```bash
# TST ID Authentication
TST_ID_BASE_URL=https://id.tstservice.tech
TST_ID_AUTH_ENDPOINT=/api/v1/auth/me
TST_ID_TIMEOUT=30
TST_ID_AUTO_CREATE_USERS=true
TST_ID_AUTO_VERIFY_TST_USERS=true
TST_ID_LINK_EXISTING_USERS=true
TST_ID_CACHE_USER_INFO=false
TST_ID_CACHE_TTL_SECONDS=300
TST_ID_ENABLE_DEBUG_LOGGING=false

# Connection settings для устранения проблем с соединением
TST_ID_MAX_RETRIES=3
TST_ID_RETRY_DELAY=1
TST_ID_CONNECTION_POOL_SIZE=10
TST_ID_KEEPALIVE_TIMEOUT=30

# Database settings для устранения проблем с БД
TST_ID_DB_MAX_RETRIES=5
TST_ID_DB_RETRY_DELAY=2.0
TST_ID_DB_OPERATION_TIMEOUT=15
```

### 2. Обновите модель пользователя

Добавьте поля TST ID в вашу модель пользователя:

```python
# models.py
class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # TST ID поля
    tst_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tst_role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    position_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    github_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
```

### 3. Создайте адаптеры

```python
# adapters/tst_id_adapters.py
from fastapi_tst_id_auth import (
    UserRepositoryInterface,
    JWTServiceInterface, 
    UserMapperInterface,
    TSTIdUserData
)

class UserRepositoryAdapter(UserRepositoryInterface):
    def __init__(self, repository):
        self._repository = repository
    
    async def find_by_tst_id(self, tst_id: int):
        return await self._repository.find_by_tst_id(tst_id)
    
    async def find_by_email(self, email: str):
        return await self._repository.find_by_email(email)
    
    async def save(self, user):
        return await self._repository.save(user)
    
    async def update(self, user):
        return await self._repository.update(user)

class JWTServiceAdapter(JWTServiceInterface):
    def __init__(self, jwt_service):
        self._jwt_service = jwt_service
    
    def create_token_pair(self, user_id, email):
        return self._jwt_service.create_token_pair(user_id, email)
    
    def create_access_token(self, user_id, email):
        return self._jwt_service.create_access_token(user_id, email)

class UserMapperAdapter(UserMapperInterface):
    def create_user_from_tst_data(self, tst_data: TSTIdUserData):
        # Создайте User из TST данных
        return User(
            email=tst_data.email,
            full_name=tst_data.full_name,
            is_verified=True,
            tst_id=tst_data.tst_id,
            username=tst_data.username,
            # ... другие поля
        )
    
    def update_user_with_tst_data(self, user, tst_data: TSTIdUserData):
        # Обновите пользователя данными из TST
        user.username = tst_data.username
        user.tst_role = tst_data.role
        # ... другие поля
        return user
```

### 4. Настройте зависимости

```python
# dependencies/auth.py
from fastapi_tst_id_auth.dependencies import configure_dependencies

def get_tst_user_repository_adapter():
    repository = YourUserRepository()  # Ваш репозиторий
    return UserRepositoryAdapter(repository)

def get_tst_jwt_service_adapter():
    jwt_service = YourJWTService()  # Ваш JWT сервис
    return JWTServiceAdapter(jwt_service)

def get_tst_user_mapper_adapter():
    return UserMapperAdapter()

def setup_tst_dependencies():
    configure_dependencies(
        user_repository_dependency=get_tst_user_repository_adapter,
        jwt_service_dependency=get_tst_jwt_service_adapter,
        user_mapper_dependency=get_tst_user_mapper_adapter
    )
```

### 5. Настройте роутер

```python
# routes/auth.py
from fastapi_tst_id_auth import create_tst_auth_router

# Глобальная переменная для роутера
tst_auth_router = None

def setup_tst_router():
    global tst_auth_router
    tst_auth_router = create_tst_auth_router(
        user_repository_dependency=get_tst_user_repository_adapter,
        jwt_service_dependency=get_tst_jwt_service_adapter,
        user_mapper_dependency=get_tst_user_mapper_adapter,
        prefix="",
        tags=["TST ID Authentication"]
    )
```

### 6. Интегрируйте в main.py

```python
# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Настраиваем TST ID зависимости
    from .dependencies.auth import setup_tst_dependencies
    setup_tst_dependencies()
    
    # Создаем TST ID роутер
    from .routes.auth import setup_tst_router
    setup_tst_router()
    
    # Подключаем роутер
    from .routes.auth import tst_auth_router
    if tst_auth_router:
        app.include_router(tst_auth_router, prefix="/api/v1/auth")
    
    yield

app = FastAPI(lifespan=lifespan)
```

## 🎯 Готово!

Теперь у вас доступен endpoint:

```
POST /api/v1/auth/tst-id/login
```

**Запрос:**
```json
{
  "tst_token": "jwt_token_from_tst_id"
}
```

**Ответ:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "tst_id": 123,
    "username": "johndoe",
    "role": "user"
  },
  "tokens": {
    "access_token": "your_access_token",
    "refresh_token": "your_refresh_token",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

## 🔧 Конфигурация

Все настройки через переменные окружения с префиксом `TST_ID_`:

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `TST_ID_BASE_URL` | `https://id.tstservice.tech` | URL TST ID сервиса |
| `TST_ID_AUTO_CREATE_USERS` | `true` | Автосоздание пользователей |
| `TST_ID_LINK_EXISTING_USERS` | `true` | Привязка к существующим пользователям |
| `TST_ID_AUTO_VERIFY_TST_USERS` | `true` | Автоверификация TST пользователей |

## 🛠️ Кастомизация

### Кастомная логика создания пользователей

```python
class CustomUserMapperAdapter(UserMapperInterface):
    def create_user_from_tst_data(self, tst_data: TSTIdUserData):
        # Ваша кастомная логика
        user = User(
            email=tst_data.email,
            full_name=tst_data.full_name,
            # Добавьте свои поля
            department=self.get_department_by_position(tst_data.position_id),
            permissions=self.get_default_permissions(tst_data.role)
        )
        return user
```

### Кастомные проверки безопасности

```python
def setup_tst_dependencies():
    configure_dependencies(
        user_repository_dependency=get_tst_user_repository_adapter,
        jwt_service_dependency=get_tst_jwt_service_adapter,
        user_mapper_dependency=get_custom_user_mapper_adapter  # Ваш адаптер
    )
```

## 🚨 Устранение неполадок

### ❌ "Authentication failed: (sqlalchemy.dialects.postgresql.asyncpg.Error) <class 'asyncpg.exceptions.ConnectionDoesNotExistError'>: connection was closed in the middle of operation"

**Причина**: Проблемы с соединением к базе данных PostgreSQL во время операций аутентификации

**Решения**:

1. **Настройте retry логику для БД**:
```bash
TST_ID_DB_MAX_RETRIES=5
TST_ID_DB_RETRY_DELAY=2.0
TST_ID_DB_OPERATION_TIMEOUT=15
```

2. **Включите отладочное логирование**:
```bash
TST_ID_ENABLE_DEBUG_LOGGING=true
```

3. **Проверьте настройки пула соединений SQLAlchemy**:
```python
# В вашем database.py или main.py
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True,  # Важно для обнаружения разорванных соединений
}
```

4. **Оптимизируйте таймауты PostgreSQL**:
```bash
# В postgresql.conf или переменных окружения
POSTGRES_STATEMENT_TIMEOUT=30000
POSTGRES_IDLE_IN_TRANSACTION_SESSION_TIMEOUT=60000
```

5. **Проверьте соединение с БД**:
```bash
# Тест соединения
pg_isready -h your_host -p 5432 -U your_user
```

### ❌ "Authentication failed: connection was closed in the middle of operation" (HTTP)

**Причина**: Проблемы с сетевым соединением к TST ID API

**Решения**:

1. **Увеличьте таймаут и количество попыток**:
```bash
TST_ID_TIMEOUT=60
TST_ID_MAX_RETRIES=5
TST_ID_RETRY_DELAY=2
```

2. **Оптимизируйте настройки HTTP соединения**:
```bash
TST_ID_CONNECTION_POOL_SIZE=20
TST_ID_KEEPALIVE_TIMEOUT=45
```

3. **Проверьте доступность TST ID сервиса**:
```bash
curl -I https://id.tstservice.tech/api/v1/auth/me
```

### ❌ "User not found"
- Проверьте настройку `TST_ID_AUTO_CREATE_USERS=true`
- Убедитесь, что `UserMapperAdapter.create_user_from_tst_data()` работает корректно

### ❌ "Invalid TST ID token"
- Проверьте срок действия токена TST ID
- Убедитесь, что токен передается в правильном формате: `Bearer <token>`

### ❌ Ошибка конфигурации
- Проверьте все переменные окружения `TST_ID_*`
- Убедитесь, что `.env` файл загружается

### ❌ Проблемы с JWT
- Проверьте реализацию `JWTServiceAdapter`
- Убедитесь, что `create_token_pair()` возвращает правильный формат

### 🔍 Диагностика проблем

1. **Включите подробное логирование**:
```python
import logging
logging.getLogger("fastapi_tst_id_auth").setLevel(logging.DEBUG)
```

2. **Проверьте сетевые настройки**:
```python
import aiohttp
import asyncio

async def test_connection():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://id.tstservice.tech/api/v1/auth/me") as response:
            print(f"Status: {response.status}")

asyncio.run(test_connection())
```

3. **Мониторинг ошибок**:
```python
from fastapi_tst_id_auth.exceptions import TSTIdAPIError

try:
    # ваш код аутентификации
    pass
except TSTIdAPIError as e:
    print(f"API Error: {e.message}, Status: {e.status_code}")
```

## 🎉 Готово к продакшену!

- ✅ Автоматическое создание/обновление пользователей
- ✅ Безопасная JWT авторизация
- ✅ Поддержка кастомной бизнес-логики
- ✅ Полная типизация TypeScript-style
- ✅ Подробное логирование и отладка

**Документация пакета:** [GitHub Repository](https://github.com/TST-Services/fastapi-tst-id-auth)