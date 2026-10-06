from aiogram import Bot

from app.models.todo_model import ToDo
from app.models.user_model import User


def build_reminder_message(
    todo: ToDo,
    is_missed: bool,
) -> str:
    if is_missed:
        message = f'Извините, пропущена задача: «{todo.title}»'
    else:
        message = f'Напоминание: «{todo.title}»'

    if todo.description:
        message += f"\nОписание: {todo.description}"

    return message


async def send_reminder(
    bot: Bot,
    user: User,
    todo: ToDo,
    is_missed: bool,
) -> bool:
    if user.telegram_id is None:
        return False

    message = build_reminder_message(
        todo,
        is_missed,
    )

    await bot.send_message(
        chat_id=user.telegram_id,
        text=message,
    )

    return True