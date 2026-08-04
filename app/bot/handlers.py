from aiogram import Router, types, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal
from app.models.user_model import User
from app.bot.keyboards import get_main_keyboard, get_final_confirmation_kb
from app.services.user_service import delete_user_account

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject):
    user_id_arg = command.args

    if not user_id_arg:
        await message.answer(
            f"Привет, {message.from_user.first_name}!\n\n"
            "Нажми кнопку ниже, чтобы открыть Mini App:",
            reply_markup=get_main_keyboard(),  # <-- Обязательно со скобками ()
        )
        return

    # Проверка ссылки привязки аккаунта
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
            reply_markup=get_main_keyboard(),  # <-- Обязательно со скобками ()
        )

        @router.callback_query(F.data == "confirm_danger_zone")
        async def process_danger_click(callback: CallbackQuery):
            """Первое предупреждение."""
            await callback.answer("⚠️ Внимание! Это опасное действие!", show_alert=True)
            await callback.message.edit_text(
                "🧟‍♂️ **ВЫ ВСТУПАЕТЕ В ОПАСНУЮ ЗОНУ!** 🧟‍♂️\n\n"
                "Вы действительно хотите навсегда удалить свой аккаунт и **ВСЕ** сохранённые задачи?\n"
                "Это действие **невозможно отменить**!",
                parse_mode="Markdown",
                reply_markup=get_final_confirmation_kb(),
            )

        @router.callback_query(F.data == "cancel_deletion")
        async def process_cancel_deletion(callback: CallbackQuery):
            """Побег с поля боя."""
            await callback.answer("Уф... Пронесло!")
            await callback.message.edit_text("Фух, отмена! Все ваши задачи остались в целости и сохранности. 😌")

        @router.callback_query(F.data == "execute_account_deletion")
        async def process_execute_deletion(
                callback: CallbackQuery,
                db: AsyncSession,
                current_user: User,
        ):
            """Окончательное удаление."""
            await delete_user_account(current_user, db)
            await callback.answer("Аккаунт удален", show_alert=True)
            await callback.message.edit_text(
                "**Ваш аккаунт и все задачи были успешно уничтожены.**\n\n"
                "Если захотите вернуться — просто нажмите /start."
            )