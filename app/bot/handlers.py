from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User
from app.bot.keyboards import get_main_keyboard

from datetime import datetime, timezone
router = Router()


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
            "Нажми кнопку ниже, чтобы открыть Mini App:",
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
        or user.telegram_link_expires_at <= datetime.now(timezone.utc)
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
