# Интеграция с fastapi-tst-id-auth

## 🎉 Обновление завершено!

Проект успешно обновлен для использования нового пакета `fastapi-tst-id-auth`. Вся логика TST ID авторизации теперь вынесена в отдельный переиспользуемый пакет.

## 📦 Установка зависимостей

1. **Активируйте виртуальное окружение:**
   ```bash
   source venv/bin/activate
   ```

2. **Установите обновленные зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

   Это автоматически установит пакет `fastapi-tst-id-auth` из GitHub репозитория.

## 🧹 Что было удалено

### Файлы:
- `app/infrastructure/external_services/tst_id_service.py`
- `app/use_cases/commands/user/authenticate_tst_id_command.py`

### Схемы (из `app/shared/schemas/auth.py`):
- `TSTIdLoginRequest`
- `TSTIdPositionResponse`  
- `TSTIdUserResponse`
- `TSTIdLoginResponse`

### Импорты:
Удалены все старые импорты TST ID логики из роутов и зависимостей.

## 🔧 Что было добавлено

### Новые адаптеры (`app/infrastructure/adapters/tst_id_adapters.py`):
- `UserRepositoryAdapter` - адаптер для репозитория пользователей
- `JWTServiceAdapter` - адаптер для JWT сервиса  
- `UserMapperAdapter` - адаптер для маппинга пользователей

### Обновленные зависимости (`app/api/dependencies/auth.py`):
- `get_tst_user_repository_adapter()`
- `get_tst_jwt_service_adapter()`
- `get_tst_user_mapper_adapter()`

### Новый роутер:
TST ID роутер теперь создается с использованием пакета `fastapi-tst-id-auth` и подключается в `main.py`.

## 🛠️ Архитектура интеграции

```
┌─────────────────────────────────────┐
│        fastapi-tst-id-auth          │
│                                     │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ TSTIdService│ │ TSTIdConfig │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │   Schemas   │ │   Router    │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│           Ваш проект                │
│                                     │
│  ┌─────────────────────────────┐   │
│  │        Адаптеры             │   │
│  │  ┌─────────────────────┐   │   │
│  │  │ UserRepositoryAdapt.│   │   │
│  │  │ JWTServiceAdapter   │   │   │
│  │  │ UserMapperAdapter   │   │   │
│  │  └─────────────────────┘   │   │
│  └─────────────────────────────┘   │
│           │                         │
│           ▼                         │
│  ┌─────────────────────────────┐   │
│  │    Ваша бизнес-логика       │   │
│  │  ┌─────────────────────┐   │   │
│  │  │ User Entity         │   │   │
│  │  │ UserRepository      │   │   │
│  │  │ JWTService          │   │   │
│  │  └─────────────────────┘   │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

## 🧪 Тестирование

Запустите тестовый скрипт для проверки интеграции:

```bash
python test_integration.py
```

Этот скрипт проверит:
- ✅ Импорты всех компонентов
- ✅ Создание сервисов и адаптеров
- ✅ Создание роутеров
- ✅ Корректность конфигурации

## 🚀 Запуск приложения

После установки зависимостей запустите приложение как обычно:

```bash
uvicorn app.main:app --reload
```

## 📡 API Endpoints

Теперь доступен новый endpoint:

```
POST /api/v1/auth/tst-id/login
```

**Пример запроса:**
```json
{
  "tst_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Пример ответа:**
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

## 🔧 Конфигурация

Вы можете настроить поведение TST ID авторизации через переменные окружения:

```bash
# .env
TST_ID_BASE_URL=https://id.tstservice.tech
TST_ID_AUTO_CREATE_USERS=true
TST_ID_AUTO_VERIFY_TST_USERS=true
TST_ID_LINK_EXISTING_USERS=true
TST_ID_ENABLE_DEBUG_LOGGING=false
```

## 🎯 Преимущества новой архитектуры

### ✅ Переиспользуемость
- Пакет можно использовать в других проектах
- Единая реализация для всех сервисов TST

### ✅ Разделение ответственности  
- Ваш проект сосредоточен на бизнес-логике
- Пакет отвечает только за TST ID авторизацию

### ✅ Простота обновления
- Обновления TST ID логики происходят в одном месте
- Автоматическое получение новых возможностей

### ✅ Тестируемость
- Пакет имеет собственные тесты
- Легко мокать для тестирования

### ✅ Типобезопасность
- Полная поддержка TypeScript-style типов
- Четкие интерфейсы интеграции

## 🆘 Устранение неполадок

### Ошибка импорта пакета
```bash
# Переустановите пакет
pip uninstall fastapi-tst-id-auth
pip install git+https://github.com/TST-Services/fastapi-tst-id-auth.git
```

### Ошибки миграции базы данных
Убедитесь, что выполнили миграции для полей TST ID:
```bash
alembic upgrade head
```

### Проблемы с зависимостями
Проверьте, что все адаптеры правильно настроены в `app/api/dependencies/auth.py`.

## 📞 Поддержка

- 🐛 Issues: [GitHub Issues](https://github.com/TST-Services/fastapi-tst-id-auth/issues)
- 📖 Документация пакета: [README](https://github.com/TST-Services/fastapi-tst-id-auth#readme)
- 🌐 TST ID Service: [id.tstservice.tech](https://id.tstservice.tech)

---

**🎉 Интеграция завершена! Теперь вы используете современный подход к TST ID авторизации!**