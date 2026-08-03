from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

WEBAPP_URL = "https://perception-garcia-may-michelle.trycloudflare.com"

def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть Mini App",
                    web_app=WebAppInfo(url=WEBAPP_URL)  # <-- ИМЕННО web_app, НЕ url!
                )
            ]
        ]
    )