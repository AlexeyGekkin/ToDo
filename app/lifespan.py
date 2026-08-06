import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.bot.main import bot, dp


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