# ToDo API

Асинхронное backend-приложение для управления задачами на FastAPI с JWT-аутентификацией, PostgreSQL, Telegram Mini App и системой напоминаний.

Проект разработан как учебный и портфолио-проект с упором на практику backend-разработки: работа с асинхронным API и БД, миграциями, авторизацией, Telegram API, фоновыми задачами, Docker и CI/CD.

## Возможности

* регистрация и авторизация пользователей;
* JWT-аутентификация;
* хеширование паролей с Argon2id;
* CRUD для задач;
* пагинация, фильтрация и сортировка задач;
* указание даты и времени дедлайна;
* два независимых типа напоминаний:

  * утреннее;
  * в момент дедлайна;
* комбинированный режим напоминаний;
* Telegram-бот;
* Telegram Mini App;
* привязка Telegram-аккаунта к пользователю;
* удаление аккаунта вместе с задачами;
* отдельный процесс для обработки напоминаний.

## Стек

### Backend

* Python 3.12
* FastAPI
* SQLAlchemy 2.x
* Pydantic v2
* Python-JOSE
* pwdlib + Argon2
* APScheduler

### Database

* PostgreSQL 17
* Alembic
* asyncpg

### Telegram

* aiogram 3
* Telegram WebApp JavaScript SDK
* HMAC-SHA256 для проверки `init_data`

### Testing

* pytest
* pytest-asyncio
* aiosqlite
* unittest.mock

### Infrastructure

* Docker
* Docker Compose
* Nginx
* Certbot
* GitHub Actions
* GitHub Container Registry
* systemd
* SSH L3-туннель

## Архитектура

Приложение состоит из нескольких независимых процессов, запускаемых из одного Docker-образа:

```text
                    ┌──────────────┐
                    │    Nginx     │
                    │ Reverse Proxy│
                    │   + SSL      │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    │     app      │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  PostgreSQL  │
                    └──────────────┘

Telegram
    │
    ▼
┌──────────────┐
│     bot      │
│   aiogram    │
└──────┬───────┘
       │
       ▼
   PostgreSQL


┌──────────────┐
│  scheduler   │
│ APScheduler  │
└──────┬───────┘
       │
       ├── PostgreSQL
       │
       └── Telegram Bot API
```

`app`, `bot` и `scheduler` используют один Docker-образ, но запускаются с разными командами.

## Структура проекта

```text
app/
├── bot/
│   ├── callbacks.py
│   ├── handlers.py
│   ├── keyboards.py
│   ├── main.py
│   ├── middleware.py
│   └── run.py
│
├── models/
│   ├── todo_model.py
│   └── user_model.py
│
├── notifications/
│   └── telegram.py
│
├── routers/
│   ├── telegram_router.py
│   ├── todo_router.py
│   └── user_router.py
│
├── scheduler/
│   ├── run.py
│   └── scheduler.py
│
├── schemas/
│   ├── todo_schema.py
│   └── user_schema.py
│
├── services/
│   ├── auth_service.py
│   ├── reminder_service.py
│   ├── telegram_auth_service.py
│   ├── telegram_service.py
│   ├── todo_service.py
│   └── user_service.py
│
├── database.py
├── dependencies.py
├── config.py
├── lifespan.py
├── app_factory.py
└── main.py
```

В проекте используется разделение на:

* `routers` — HTTP-эндпоинты;
* `services` — бизнес-логика и работа с данными;
* `models` — модели SQLAlchemy;
* `schemas` — Pydantic-схемы;
* `bot` — Telegram-бот;
* `scheduler` — обработка напоминаний;
* `notifications` — отправка уведомлений.

## Аутентификация

Для API используется JWT.

Основные endpoints:

```text
POST /users/register
POST /users/login
GET  /users/me
```

Пароли не хранятся в исходном виде. Для хеширования используется Argon2id.

JWT содержит идентификатор пользователя и используется для авторизации защищённых endpoints.

## Telegram Mini App

Telegram Mini App использует стандартный механизм авторизации Telegram Web App.

Клиент передаёт `tg.initData` на backend:

```text
/api/telegram/...
```

Backend:

1. получает `init_data`;
2. проверяет цифровую подпись;
3. получает Telegram ID пользователя;
4. находит связанного пользователя;
5. выполняет операцию от его имени.

Для проверки используется HMAC-SHA256.

Дополнительно проверяется `auth_date`, чтобы не принимать устаревшие данные авторизации.

### Привязка Telegram

Для привязки аккаунта используется одноразовый токен.

Токен:

* генерируется сервером;
* хранится в БД;
* имеет ограниченный срок действия — 15 минут;
* после использования связывает Telegram ID с аккаунтом пользователя.

## Напоминания

Для задач можно выбрать один из режимов:

```text
NONE      — без напоминаний
MORNING   — только утреннее
DEADLINE  — только в момент дедлайна
BOTH      — оба напоминания
```

Утреннее напоминание создаётся на 08:00 локального времени пользователя.

Напоминание о дедлайне создаётся на указанное пользователем время.

## Scheduler

Обработка напоминаний вынесена в отдельный контейнер.

Scheduler запускает проверку один раз в минуту:

```text
APScheduler
     │
     ▼
get_due_reminders()
     │
     ▼
поиск наступивших напоминаний
     │
     ▼
отправка сообщения в Telegram
     │
     ▼
очистка отправленного напоминания
     │
     ▼
commit
```

Для загрузки пользователя вместе с задачей используется `selectinload`, что позволяет избежать проблемы N+1 при обращении к связанным пользователям.

У каждого типа напоминания своё поле в БД. Поэтому при режиме `BOTH` утреннее и дедлайновое напоминания обрабатываются независимо.

Если отправка прошла успешно, соответствующее напоминание удаляется из задачи.

Для просроченных напоминаний используется отдельное правило обработки: напоминание считается пропущенным, если его время старше 5 минут.

Scheduler настроен с:

```python
max_instances=1
coalesce=True
```

Это предотвращает одновременный запуск нескольких экземпляров одной задачи и объединяет пропущенные запуски.

## Alembic

Изменения структуры базы данных выполняются через Alembic.

Основные команды:

```powershell
uv run alembic upgrade head
```

Создание новой миграции:

```powershell
uv run alembic revision --autogenerate -m "description"
```

## Тестирование

Тесты разделены на API и сервисный слой:

```text
tests/
├── api/
│   ├── test_auth.py
│   └── test_todo.py
│
└── services/
    ├── test_todo_services.py
    └── test_user_service.py
```

Для тестов используется отдельная SQLite-база в памяти.

Запуск:

```powershell
uv run pytest
```

Проверка качества кода:

```powershell
uv run ruff check .
```

Ruff используется как локальный инструмент проверки кода. В CI он не является обязательным этапом деплоя.

## Docker

Docker Compose запускает четыре основных сервиса:

```text
db
app
bot
scheduler
```

`app`, `bot` и `scheduler` используют один Docker-образ с разными командами запуска.

Пример:

```yaml
app:
  image: ghcr.io/alexeygekkin/todo:latest

bot:
  image: ghcr.io/alexeygekkin/todo:latest
  command: ["python", "-m", "app.bot.run"]

scheduler:
  image: ghcr.io/alexeygekkin/todo:latest
  command: ["python", "-m", "app.scheduler.run"]
```

Для Telegram-бота и scheduler используется отдельная Docker-сеть.

## Сетевая инфраструктура

На сервере используется отдельная Docker-сеть для Telegram-бота и scheduler.

На уровне хоста настроен SSH L3-туннель до NAT VPS.

Туннель поддерживается systemd-сервисом:

```text
natvps-tunnel.service
```

Сервис запускает:

```text
/usr/local/sbin/natvps-tunnel.sh
```

и автоматически перезапускает туннель при завершении процесса:

```ini
Restart=always
RestartSec=5
```

Для туннеля используется интерфейс:

```text
tun0
```

Nginx используется как reverse proxy и отвечает за HTTPS.

## CI/CD

Для проекта настроен GitHub Actions.

Pipeline состоит из трёх этапов:

```text
tests
  │
  ▼
build
  │
  ▼
deploy
```

### Tests

GitHub Actions запускает PostgreSQL 17 как service container, устанавливает зависимости и выполняет:

```powershell
uv run pytest
```

### Build

После успешного прохождения тестов собирается Docker-образ и отправляется в GitHub Container Registry.

```text
GitHub Actions
      │
      ▼
Docker build
      │
      ▼
GHCR
```

### Deploy

После успешной сборки GitHub Actions подключается к серверу по SSH и выполняет:

```text
git fetch origin main
git reset --hard origin/main
docker pull ...
docker compose up -d
```

Таким образом, изменение в `main` запускает тестирование, сборку Docker-образа и последующий деплой.

## Переменные окружения

Основные переменные:

```env
DATABASE_URL=postgresql+asyncpg://todo_user:password@db:5432/todo

BOT_TOKEN=...

SECRET_KEY=...

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Секретные значения не хранятся в исходном коде.

Для GitHub Actions используются GitHub Secrets.

## Что реализовано в проекте

В рамках проекта реализованы и изучены:

* асинхронный FastAPI;
* асинхронная работа с PostgreSQL через SQLAlchemy;
* Pydantic-схемы;
* JWT-аутентификация;
* безопасное хранение паролей с Argon2id;
* Alembic и миграции БД;
* Telegram Bot API через aiogram;
* Telegram Mini App;
* проверка Telegram `init_data`;
* APScheduler;
* Docker Compose;
* отдельные процессы для API, бота и scheduler;
* автоматическое тестирование;
* GitHub Actions;
* сборка и публикация Docker-образов в GHCR;
* автоматический деплой на VPS;
* настройка Nginx и HTTPS;
* SSH L3-туннель через `tun0`.

<details>
<summary>Примеры API</summary>

### Регистрация

```http
POST /users/register
```

### Авторизация

```http
POST /users/login
```

### Текущий пользователь

```http
GET /users/me
```

### Задачи

```http
GET    /todos
POST   /todos
PATCH  /todos/{todo_id}
DELETE /todos/{todo_id}
```

### Telegram Mini App

```http
GET    /api/telegram/profile
GET    /api/telegram/todos
POST   /api/telegram/todos
PATCH  /api/telegram/todos/{todo_id}
DELETE /api/telegram/account
```

</details>

<details>
<summary>Запуск локально</summary>

Установить зависимости:

```powershell
uv sync
```

Настроить переменные окружения в `.env`.

Запустить миграции:

```powershell
uv run alembic upgrade head
```

Запустить приложение:

```powershell
uv run uvicorn app.main:app --reload
```

Запустить тесты:

```powershell
uv run pytest
```

Проверить код:

```powershell
uv run ruff check .
```

</details>
