# Syncra

Syncra — MVP система управления командами.

Возможности:

- JWT аутентификация
- Пользователи и роли
- Создание команд
- Вступление в команды по invite code
- Управление участниками
- Задачи команды
- Комментарии к задачам
- Оценка выполненных задач
- Встречи команды
- Общий календарь задач и встреч

## Stack

### Backend

- Python 3.13
- FastAPI
- SQLAlchemy 2.0 Async
- PostgreSQL 16
- Alembic
- Pydantic v2
- JWT (RS256)
- uv

### Frontend

- Nuxt 4.5
- Vue 3
- TypeScript
- Pinia
- Ant Design Vue

### Infrastructure

- Docker
- Docker Compose

# Запуск проекта

## Требования

Установленные:

- Docker
- Docker Compose

## Структура проекта

```text
syncra
├── backend
├── frontend
├── certs
├── docker-compose.yml
└── .env
```

## Тестовый пользователь

После первого запуска автоматически создается пользователь с ролью **manager**.

```
Логин: manager
Пароль: manager123
```

Этот пользователь может протестировать весь функционал приложения:

- создание команд;
- создание задач;
- проведение встреч;
- оценку задач;
- управление участниками команды.

## Доступ к ресурсам после запуска

Frontend:
http://localhost:3000

Backend API:
http://localhost:8000/api/v1

Swagger:
http://localhost:8000/docs

# Первый запуск

Склонировать проект:

```bash
git clone <repository_url>
cd syncra
```

Создать файл окружения:

```bash
cp .env.example .env
```

Создать ключи для jwt

```bash
mkdir certs

openssl genrsa -out certs/jwt-private.pem 2048

openssl rsa -in certs/jwt-private.pem -pubout -out certs/jwt-public.pem
```

Запустить проект:

```bash
docker compose up --build
```

# Запуск тестов

Для запуска интеграционных тестов необходимо поднять только тестовую базу PostgreSQL.

1. Создать и заполнить файл `.env.test` в корне проекта.

Пример:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5533
POSTGRES_DB=syncra_test_db
POSTGRES_USER=syncra_test_user
POSTGRES_PASSWORD=syncra_test_password
```

2. Запустить контейнер:

```bash
docker compose up -d postgres_test
```

3. Перейти в директорию backend:

```bash
cd backend
```

4. Запустить тесты:

```bash
uv run pytest
```

Перед запуском тестов автоматически выполняются миграции Alembic в тестовую базу данных.