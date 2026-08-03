import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routers.user_router import router as user_router
from app.routers.todo_router import router as todo_router
from app.bot.main import bot, dp


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Проверяем связь с Telegram при старте
    try:
        me = await bot.get_me()
        print(f"✅ Успешное подключение к Telegram! Бот: @{me.username}")
    except Exception as e:
        print(f"❌ Ошибка подключения к Telegram: {e}")
        print("💡 Подсказка: Проверь VPN / TUN-режим или интернет-соединение.")

    # 2. Запускаем поллинг бота в фоновой задаче
    bot_task = asyncio.create_task(dp.start_polling(bot))

    yield

    # 3. Корректно останавливаем бота и закрываем сессию
    bot_task.cancel()
    try:
        await bot.session.close()
    except Exception:
        pass
    print("🛑 Telegram-бот остановлен.")


app = FastAPI(title="TODO App", lifespan=lifespan)

app.include_router(user_router)
app.include_router(todo_router)


@app.get("/")
async def root():
    return {"ok": True}