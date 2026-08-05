import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.routers import (user_router,
                         todo_router,
                         telegram_router)
from app.bot.main import bot, dp

templates = Jinja2Templates(directory="app/templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        me = await bot.get_me()
        print(f"Успешное подключение к Telegram! Бот: @{me.username}")
    except Exception as exc:
        print(f"Ошибка подключения к Telegram: {exc}")
        print("Подсказка: Проверь VPN / TUN-режим или интернет-соединение.")

    bot_task = asyncio.create_task(dp.start_polling(bot))

    yield

    bot_task.cancel()
    try:
        await bot.session.close()
    except Exception:
        pass
    print("Telegram-бот остановлен.")


app = FastAPI(title="TODO App", lifespan=lifespan)
app.include_router(user_router)
app.include_router(todo_router)
app.include_router(telegram_router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/webapp", response_class=HTMLResponse)
async def get_webapp(request: Request):
    return templates.TemplateResponse(request, "index.html")
