from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database import SessionLocal
from app.services.telegram_service import delete_webapp_account
from app.bot.keyboards import get_final_confirmation_kb


router = Router()


@router.callback_query(F.data == "confirm_danger_zone")
async def process_danger_click(
    callback: CallbackQuery,
):
    await callback.answer(
        "Внимание! Это опасное действие!",
        show_alert=True,
    )

    await callback.message.edit_text(
        "**ВЫ ВСТУПАЕТЕ В ОПАСНУЮ ЗОНУ!** ️\n\n"
        "Вы действительно хотите навсегда удалить свой аккаунт и **ВСЕ** сохранённые задачи?\n"
        "Это действие **невозможно отменить**!",
        parse_mode="Markdown",
        reply_markup=get_final_confirmation_kb(),
    )


@router.callback_query(F.data == "cancel_deletion")
async def process_cancel_deletion(
    callback: CallbackQuery,
):
    await callback.answer("Уф... Пронесло!")

    await callback.message.edit_text(
        "Фух, отмена! Все ваши задачи остались в целости и сохранности. 😌"
    )


@router.callback_query(F.data == "execute_account_deletion")
async def process_execute_deletion(
    callback: CallbackQuery,
):
    telegram_id = callback.from_user.id

    async with SessionLocal() as db:
        await delete_webapp_account(
            telegram_id,
            db,
        )

    await callback.answer(
        "Аккаунт удален",
        show_alert=True,
    )

    await callback.message.edit_text(
        "**Ваш аккаунт и все задачи были успешно уничтожены.**\n\n"
        "Если захотите вернуться — просто нажмите /start."
    )