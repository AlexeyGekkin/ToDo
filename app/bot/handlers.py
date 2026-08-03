from datetime import datetime, timedelta

from aiogram import Router, types, F
from aiogram.filters import CommandStart, CommandObject
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import SessionLocal
from app.models.user_model import User
from app.bot.keyboards import get_main_keyboard  # Подключаем клавиатуру

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject):
    user_id_arg = command.args

    if not user_id_arg:
        await message.answer(
            f"Привет, {message.from_user.first_name}! 👋\n\n"
            "Зайди в приложение и перейди по ссылке подключения, чтобы связать аккаунт с Telegram.",
            reply_markup=get_main_keyboard,
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
            reply_markup=get_main_keyboard,  # Прикрепляем кнопки при успешной привязке
        )


@router.message(F.text == "📋 Задачи на сегодня")
async def get_today_tasks(message: types.Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User)
            .where(User.telegram_id == message.from_user.id)
            .options(selectinload(User.todos))
        )
        user = result.scalars().first()

        if not user:
            await message.answer("❌ Аккаунт не привязан.")
            return

        active_todos = [t for t in user.todos if not t.completed]

        if not active_todos:
            await message.answer("🥳 Задач нет, отдыхай!")
            return

        tasks_text = "\n".join([f"▫️ {t.title}" for t in active_todos])
        await message.answer(f"📋 **Твои активные задачи:**\n\n{tasks_text}", parse_mode="Markdown")


@router.message(F.text == "📅 Список на неделю")
async def get_weekly_tasks(message: types.Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User)
            .where(User.telegram_id == message.from_user.id)
            .options(selectinload(User.todos))
        )
        user = result.scalars().first()

        if not user:
            await message.answer("❌ Аккаунт не привязан.")
            return

        now = datetime.now()
        start_of_week = now - timedelta(days=now.weekday())
        end_of_week = start_of_week + timedelta(days=7)

        weekly_todos = [
            t for t in user.todos
            if not t.completed
            and t.due_date
            and start_of_week <= (t.due_date.replace(tzinfo=None) if t.due_date.tzinfo else t.due_date) <= end_of_week
        ]

        if not weekly_todos:
            await message.answer("📅 На эту неделю задач с дедлайнами нет!")
            return

        # Безопасная сортировка по дате
        weekly_todos.sort(key=lambda x: x.due_date.replace(tzinfo=None) if x.due_date.tzinfo else x.due_date)

        lines = ["📅 **Задачи на эту неделю:**\n"]
        for todo in weekly_todos:
            date_str = todo.due_date.strftime("%d.%m (%a) %H:%M")
            lines.append(f"🗓 `{date_str}` — **{todo.title}**")

        await message.answer("\n".join(lines), parse_mode="Markdown")


@router.message(F.text == "🎉 Статус и профиль")
async def get_profile_info(message: types.Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User)
            .where(User.telegram_id == message.from_user.id)
            .options(selectinload(User.todos))
        )
        user = result.scalars().first()

        if not user:
            await message.answer("❌ Аккаунт не привязан.")
            return

        total_todos = len(user.todos)
        active_todos = len([t for t in user.todos if not t.completed])
        completed_todos = total_todos - active_todos

        text = (
            f"👤 **Твой профиль**\n\n"
            f"📧 Email: `{user.email}`\n"
            f"🆔 Telegram ID: `{user.telegram_id}`\n\n"
            f"📊 **Статистика задач:**\n"
            f"▫️ В работе: **{active_todos}**\n"
            f"▫️ Выполнено: **{completed_todos}**\n"
            f"▫️ Всего: **{total_todos}**\n\n"
            f"🔔 **Утренний дайджест:** Активен (09:00)"
        )

        await message.answer(text, parse_mode="Markdown")