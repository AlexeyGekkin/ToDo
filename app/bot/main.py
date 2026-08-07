from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from app.config import BOT_TOKEN, BOT_PROXY

from app.bot.handlers import router as bot_router
from app.bot.callbacks import router as callback_router


session = (
    AiohttpSession(proxy=BOT_PROXY)
    if BOT_PROXY
    else None
)


bot = Bot(
    token=BOT_TOKEN,
    session=session,
)


if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не найден в переменном окружения .env!"
    )


dp = Dispatcher()

dp.include_router(bot_router)
dp.include_router(callback_router)