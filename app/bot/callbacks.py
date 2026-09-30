from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.telegram_service import (
    delete_webapp_account,
    get_user_by_telegram_id,
    get_profile,
)
from app.services.todo_service import (
    get_today_todos,
    get_week_todos,
)
from app.bot.keyboards import get_final_confirmation_kb

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


@router.callback_query(F.data == "today_tasks")
async def process_today_tasks(
    callback: CallbackQuery,
    db: AsyncSession,
):
    user = await get_user_by_telegram_id(
        callback.from_user.id,
        db,
    )

    todos = await get_today_todos(
        user,
        db,
    )

    await callback.answer()

    await callback.message.edit_text(
        f"📅 <b>Задачи на сегодня</b>\n\n"
        f"{format_todos(todos)}",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "week_tasks")
async def process_week_tasks(
    callback: CallbackQuery,
    db: AsyncSession,
):
    user = await get_user_by_telegram_id(
        callback.from_user.id,
        db,
    )

    todos = await get_week_todos(
        user,
        db,
    )

    await callback.answer()

    await callback.message.edit_text(
        f"📆 <b>Задачи на неделю</b>\n\n"
        f"{format_todos(todos)}",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "profile")
async def process_profile(
    callback: CallbackQuery,
    db: AsyncSession,
):
    profile = await get_profile(
        callback.from_user.id,
        db,
    )

    await callback.answer()

    await callback.message.edit_text(
        "👤 <b>Профиль</b>\n\n"
        f"Email: {profile['email']}\n"
        f"Активных задач: {profile['active_count']}\n"
        f"Завершённых задач: {profile['completed_count']}",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "confirm_danger_zone")
async def process_danger_click(callback: CallbackQuery):
    await callback.answer(
        "Внимание! Это опасное действие!",
        show_alert=True,
    )

    await callback.message.edit_text(
        "**ВЫ ВСТУПАЕТЕ В ОПАСНУЮ ЗОНУ!** ⚠️\n\n"
        "Вы действительно хотите навсегда удалить свой аккаунт и **ВСЕ** сохранённые задачи?\n"
        "Это действие **невозможно отменить**!",
        parse_mode="Markdown",
        reply_markup=get_final_confirmation_kb(),
    )


@router.callback_query(F.data == "cancel_deletion")
async def process_cancel_deletion(callback: CallbackQuery):
    await callback.answer("Уф... Пронесло!")

    await callback.message.edit_text(
        "Фух, отмена! Все ваши задачи остались в целости и сохранности. 😌"
    )


@router.callback_query(F.data == "execute_account_deletion")
async def process_execute_deletion(
    callback: CallbackQuery,
    db: AsyncSession,
):
    telegram_id = callback.from_user.id

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
