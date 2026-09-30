from aiogram import Bot, Dispatcher

from app.bot.callbacks import router as callback_router
from app.bot.handlers import router as bot_router
from app.bot.middleware import DbSessionMiddleware
from app.config import BOT_TOKEN

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменной окружения .env!")

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

dp.message.middleware(DbSessionMiddleware())
dp.callback_query.middleware(DbSessionMiddleware())

dp.include_router(bot_router)
dp.include_router(callback_router)

