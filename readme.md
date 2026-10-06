# ToDo

Асинхронное приложение для управления задачами на FastAPI с PostgreSQL, Telegram Mini App и системой напоминаний.

Проект развёрнут на VPS и доступен по HTTPS.

**Demo:** https://gekkin.ru  
**API:** https://gekkin.ru/docs

## Возможности

- регистрация и авторизация пользователей;
- создание, редактирование и удаление задач;
- фильтрация, сортировка и пагинация;
- дедлайны и напоминания;
- поддержка часовых поясов;
- Telegram-бот и Telegram Mini App;
- привязка Telegram-аккаунта к пользователю.

## Архитектура

```text
                 Nginx
                   │
                   ▼
               FastAPI
                   │
                   ▼
              PostgreSQL

Telegram ─────► Bot ─────► PostgreSQL

Scheduler ───────────────► PostgreSQL
    │
    └────────────────────► Telegram API
```

API, Telegram-бот и scheduler работают как отдельные Docker-сервисы, собранные из одного образа.

Напоминания обрабатываются отдельным scheduler-процессом раз в минуту.

Время напоминаний рассчитывается в часовом поясе пользователя и хранится в PostgreSQL в UTC.

## Telegram

Mini App использует стандартную авторизацию Telegram Web App.

Backend проверяет подпись `init_data` через HMAC-SHA256 и контролирует срок её действия.

Для привязки Telegram используется одноразовый токен с ограниченным временем жизни.

## Стек

**Backend:** Python 3.12, FastAPI, SQLAlchemy 2, Pydantic  
**Database:** PostgreSQL 17, asyncpg, Alembic  
**Auth:** JWT, Argon2id  
**Telegram:** aiogram 3, Telegram Mini Apps  
**Background jobs:** APScheduler  
**Testing:** pytest, pytest-asyncio  
**Infrastructure:** Docker, Docker Compose, Nginx, GitHub Actions, GHCR

## Тестирование

В проекте 80 автоматических тестов.

Проверяются:

- API и авторизация;
- CRUD и доступ пользователей к своим задачам;
- валидация данных;
- расчёт напоминаний и часовых поясов;
- Telegram `init_data`;
- scheduler и отправка уведомлений;
- сервисный слой.

## CI/CD

Push в `main` запускает:

```text
Alembic migrations on PostgreSQL
        ↓
      pytest
        ↓
   Docker build
        ↓
       GHCR
        ↓
  deploy to VPS
```

Перед запуском приложения применяются актуальные Alembic-миграции.

PostgreSQL и FastAPI имеют healthcheck.

## Безопасность

- пароли хранятся в виде Argon2id-хешей;
- защищённые запросы ограничены данными текущего пользователя;
- Telegram `init_data` проверяется по подписи и времени создания;
- пользовательские данные экранируются перед HTML-рендерингом;
- login и регистрация имеют базовую защиту от brute force и abuse;
- секреты передаются через переменные окружения и GitHub Secrets;
- FastAPI доступен снаружи только через Nginx;
- PostgreSQL не публикуется во внешнюю сеть.
