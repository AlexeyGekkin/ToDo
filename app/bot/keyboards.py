from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

WEBAPP_URL = "https://gekkin.ru/webapp"


def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📅 Сегодня"),
                KeyboardButton(text="📆 Неделя"),
            ],
            [
                KeyboardButton(text="👤 Профиль"),
                KeyboardButton(
                    text="📱 Открыть Mini App",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                ),
            ],
        ],
        resize_keyboard=True,
    )


def get_danger_zone_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Удалить аккаунт и все данные",
                    callback_data="confirm_danger_zone",
                )
            ]
        ]
    )


def get_final_confirmation_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да, всё удалить",
                    callback_data="execute_account_deletion",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Упс, отмена",
                    callback_data="cancel_deletion",
                )
            ],
        ]
    )
