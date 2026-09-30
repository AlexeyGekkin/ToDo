from datetime import UTC, datetime

from aiogram import F, Router, types
from aiogram.filters import CommandObject, CommandStart
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import get_main_keyboard
from app.models.user_model import User
from app.services.telegram_service import get_profile, get_user_by_telegram_id
from app.services.todo_service import get_today_todos, get_week_todos

router = Router()


def format_todos(todos) -> str:
    if not todos:
        return "Задач нет. 🎉"

    lines = []

    for todo in todos:
        status = "✅" if todo.completed else "⬜"

        line = f"{status} {todo.title}"

        if todo.deadline_time:
            line += f" — до {todo.deadline_time.strftime('%H:%M')}"

        if todo.target_date:
            line += f" ({todo.target_date.strftime('%d.%m')})"

        lines.append(line)

    return "\n".join(lines)


@router.message(CommandStart())
async def cmd_start(
    message: types.Message,
    command: CommandObject,
    db: AsyncSession,
):
    token = command.args

    if not token:
        await message.answer(
            f"Привет, {message.from_user.first_name}!\n\n"
            "Используй кнопки ниже:",
            reply_markup=get_main_keyboard(),
        )
        return

    result = await db.execute(
        select(User).where(User.telegram_link_token == token)
    )
    user = result.scalar_one_or_none()

    if not user:
        await message.answer(
            "Ссылка недействительна или уже использована.",
            reply_markup=get_main_keyboard(),
        )
        return

    if (
        user.telegram_link_expires_at is None
        or user.telegram_link_expires_at <= datetime.now(UTC)
    ):
        await message.answer(
            "Срок действия ссылки истёк. Создай новую ссылку в приложении.",
            reply_markup=get_main_keyboard(),
        )
        return

    user.telegram_id = message.from_user.id
    user.telegram_link_token = None
    user.telegram_link_expires_at = None

    await db.commit()

    await message.answer(
        f"**Отлично, {message.from_user.first_name}!**\n\n"
        f"Твой Telegram успешно привязан к аккаунту **{user.email}**.\n"
        f"Теперь ты можешь пользоваться приложением!",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(),
    )


@router.message(F.text == "📅 Сегодня")
async def today_tasks(
    message: types.Message,
    db: AsyncSession,
):
    user = await get_user_by_telegram_id(
        message.from_user.id,
        db,
    )

    todos = await get_today_todos(
        user,
        db,
    )

    await message.answer(
        f"📅 <b>Задачи на сегодня</b>\n\n"
        f"{format_todos(todos)}",
        parse_mode="HTML",
    )


@router.message(F.text == "📆 Неделя")
async def week_tasks(
    message: types.Message,
    db: AsyncSession,
):
    user = await get_user_by_telegram_id(
        message.from_user.id,
        db,
    )

    todos = await get_week_todos(
        user,
        db,
    )

    await message.answer(
        f"📆 <b>Задачи на неделю</b>\n\n"
        f"{format_todos(todos)}",
        parse_mode="HTML",
    )


@router.message(F.text == "👤 Профиль")
async def profile(
    message: types.Message,
    db: AsyncSession,
):
    profile_data = await get_profile(
        message.from_user.id,
        db,
    )

    await message.answer(
        "👤 <b>Профиль</b>\n\n"
        f"Email: {profile_data['email']}\n"
        f"Активных задач: {profile_data['active_count']}\n"
        f"Завершённых задач: {profile_data['completed_count']}",
        parse_mode="HTML",
    )
