from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from app.config import BOT_TOKEN

from app.bot.handlers import router as bot_router

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменном окружения .env!")
session = AiohttpSession(proxy="http://127.0.0.1:10808")
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()

dp.include_router(bot_router)