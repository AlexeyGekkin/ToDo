from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from sqlalchemy import select

from app.database import SessionLocal
from app.models.user_model import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject):
    user_id_arg = command.args

    if not user_id_arg:
        await message.answer(
            f"Привет, {message.from_user.first_name}! 👋\n\n"
            "Зайди в приложение и перейди по ссылке подключения, чтобы связать аккаунт с Telegram.",
        )
        return

    if not user_id_arg.isdigit():
        await message.answer("❌ Некорректная ссылка для привязки аккаунта.")
        return

    user_id = int(user_id_arg)

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalars().first()

        if not user:
            await message.answer("❌ Ссылка устарела или пользователь не найден.")
            return

        user.telegram_id = message.from_user.id
        await session.commit()

        await message.answer(
            f"🎉 **Отлично, {message.from_user.first_name}!**\n\n"
            f"Твой Telegram успешно привязан к аккаунту **{user.email}**.\n"
            f"Теперь сюда будут приходить уведомления о твоих задачах!",
            parse_mode="Markdown",
        )