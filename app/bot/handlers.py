from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from sqlalchemy import select

from app.database import SessionLocal
from app.models.user_model import User
from app.bot.keyboards import get_main_keyboard


router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: types.Message,
    command: CommandObject,
):
    user_id_arg = command.args

    if not user_id_arg:
        await message.answer(
            f"Привет, {message.from_user.first_name}!\n\n"
            "Нажми кнопку ниже, чтобы открыть Mini App:",
            reply_markup=get_main_keyboard(),
        )
        return

    if not user_id_arg.isdigit():
        await message.answer(
            "Некорректная ссылка для привязки аккаунта.",
            reply_markup=get_main_keyboard(),
        )
        return

    user_id = int(user_id_arg)

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )

        user = result.scalars().first()

        if not user:
            await message.answer(
                "Ссылка устарела или пользователь не найден.",
                reply_markup=get_main_keyboard(),
            )
            return

        user.telegram_id = message.from_user.id

        await session.commit()

        await message.answer(
            f"**Отлично, {message.from_user.first_name}!**\n\n"
            f"Твой Telegram успешно привязан к аккаунту **{user.email}**.\n"
            f"Теперь ты можешь пользоваться приложением!",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(),
        )