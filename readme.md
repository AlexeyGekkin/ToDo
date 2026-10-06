# ToDo

![Deploy](https://github.com/AlexeyGekkin/ToDo/actions/workflows/deploy.yml/badge.svg)

Backend-oriented task manager built with FastAPI, PostgreSQL and Telegram integration.

The project is deployed and used as a production-style portfolio project: the API, Telegram bot and reminder scheduler run as separate processes in Docker, database migrations are managed with Alembic, and every push to `main` goes through tests, image build and automated deployment.

**Live:** https://gekkin.ru  
**Swagger:** https://gekkin.ru/docs

## What the project does

- user registration and JWT authentication;
- password hashing with Argon2id;
- CRUD for tasks with pagination, filtering and sorting;
- deadlines and user time zones;
- morning and deadline reminders;
- Telegram bot with task lists and account linking;
- Telegram Mini App;
- secure Telegram `init_data` validation with HMAC-SHA256;
- one-time Telegram linking tokens with a 15-minute lifetime;
- account deletion together with user tasks;
- rate limiting for login and registration;
- health checks for the API and PostgreSQL;
- automated Docker build and deployment through GitHub Actions.

## Architecture

```text
                    Internet
                       │
                       ▼
                 ┌───────────┐
                 │   Nginx   │
                 │ HTTPS/TLS │
                 └─────┬─────┘
                       │
                       ▼
                 ┌───────────┐
                 │  FastAPI  │
                 │    app    │
                 └─────┬─────┘
                       │
                       ▼
                 ┌───────────┐
                 │PostgreSQL │
                 └───────────┘

Telegram ───────► bot ─────────────► PostgreSQL
                    │
                    └──────────────► Telegram Bot API

scheduler ──────► PostgreSQL
    │
    └────────────► Telegram Bot API
```

`app`, `bot` and `scheduler` are built from the same Docker image but run with different commands.

The API is exposed only through Nginx. The application port is bound to localhost on the host, and PostgreSQL is available only inside Docker networks.

Telegram-related processes use a separate Docker network for outbound Telegram traffic.

## Backend structure

```text
app/
├── bot/                # aiogram handlers, callbacks and middleware
├── models/             # SQLAlchemy models
├── notifications/      # Telegram notifications
├── routers/            # FastAPI endpoints
├── scheduler/          # APScheduler process
├── schemas/            # Pydantic schemas
├── services/           # business logic
├── templates/          # browser UI and Telegram Mini App
├── app_factory.py
├── config.py
├── database.py
├── dependencies.py
└── main.py
```

The HTTP layer is kept in `routers`; application logic lives in `services`; database models and API schemas are separated.

## Authentication and security

The REST API uses JWT access tokens. Passwords are never stored in plain text and are hashed with Argon2id.

Protected task queries always include the current user ID, so a user cannot access another user's task by changing an object ID.

Telegram Mini App requests are authenticated by validating Telegram `init_data`:

1. verify the HMAC-SHA256 signature;
2. validate `auth_date`;
3. extract the Telegram user ID;
4. resolve the linked application user.

Telegram account linking uses a cryptographically random, single-use token that expires after 15 minutes.

Authentication endpoints also include application-level rate limiting. Nginx forwards the real client address to Uvicorn, while direct access to the application port is blocked.

Secrets are supplied through environment variables and GitHub Secrets and are not committed to the repository.

## Reminders and time zones

A task supports four reminder modes:

```text
none
morning
deadline
both
```

The user stores an IANA time zone such as `Europe/Samara`.

Reminder timestamps are calculated in the user's time zone and stored as UTC moments in PostgreSQL:

```text
user local time
      │
      ▼
ZoneInfo conversion
      │
      ▼
UTC timestamp in DB
      │
      ▼
scheduler
      │
      ▼
Telegram notification
```

Morning reminders are scheduled for 08:00 local time. Deadline reminders use the task date and deadline time.

The scheduler runs once per minute. Morning and deadline reminders have separate database fields, so the `both` mode is processed independently. Successfully sent reminders are cleared only after the Telegram message has been sent and the database transaction is committed.

If a reminder is more than five minutes late, the notification is marked as missed.

## Main API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/users/register` | Register user |
| POST | `/users/login` | Get JWT |
| GET | `/users/me` | Current user |
| PATCH | `/users/me` | Update time zone |
| DELETE | `/users/me` | Delete account |
| GET | `/users/telegram/link-url` | Create Telegram linking URL |
| GET | `/todos/` | List tasks |
| POST | `/todos/` | Create task |
| GET | `/todos/{id}` | Get task |
| PATCH | `/todos/{id}` | Update task |
| DELETE | `/todos/{id}` | Delete task |
| GET | `/api/telegram/profile` | Mini App profile |
| GET | `/api/telegram/todos` | Mini App tasks |
| POST | `/api/telegram/todos` | Create task from Mini App |
| PATCH | `/api/telegram/todos/{id}` | Update task from Mini App |
| DELETE | `/api/telegram/account` | Delete account from Mini App |
| GET | `/health` | Application/database health |

## Testing

The test suite currently contains **70 automated tests**.

Tests cover:

- registration, authentication and protected endpoints;
- task CRUD and ownership isolation;
- validation and reminder calculations;
- Telegram `init_data` signature and expiration;
- Telegram service logic;
- scheduler success and failure scenarios;
- notification formatting;
- registration rate limiting.

Run locally:

```bash
uv run pytest
```

Static checks:

```bash
uv run ruff check .
```

## Docker

Docker Compose runs four services:

```text
db
app
bot
scheduler
```

PostgreSQL and FastAPI have health checks. `app`, `bot` and `scheduler` wait until PostgreSQL is healthy before starting.

The application container runs Alembic migrations before starting Uvicorn.

## CI/CD

The GitHub Actions pipeline is:

```text
push to main
     │
     ▼
   tests
     │
     ▼
Docker build
     │
     ▼
    GHCR
     │
     ▼
SSH deploy
     │
     ▼
Docker Compose
```

The image is published to GitHub Container Registry and then pulled by the VPS during deployment.

## Local development

Requirements:

- Python 3.12+
- PostgreSQL
- `uv`

Install dependencies:

```bash
uv sync --dev
```

Create `.env` from `.env.example` and configure:

```env
DATABASE_URL=postgresql+asyncpg://todo_user:password@127.0.0.1:5432/todo
BOT_TOKEN=your_bot_token
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Start the API:

```bash
uv run uvicorn app.main:app --reload
```

Run tests:

```bash
uv run pytest
```

## Technology stack

**Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, asyncpg  
**Database:** PostgreSQL 17, Alembic  
**Authentication:** JWT, Argon2id  
**Telegram:** aiogram 3, Telegram Mini Apps, HMAC-SHA256  
**Background jobs:** APScheduler  
**Testing:** pytest, pytest-asyncio  
**Infrastructure:** Docker, Docker Compose, Nginx, GitHub Actions, GHCR

## Scaling notes

The current rate limiter is intentionally in-memory and matches the current single API process. With multiple API replicas it should be moved to a shared store such as Redis.

The scheduler is also designed to run as a single instance. Horizontal scaling would require distributed locking or a queue-based worker model.

These trade-offs keep the deployed project small while preserving clear upgrade paths for a larger system.
