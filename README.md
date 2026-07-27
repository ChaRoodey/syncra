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