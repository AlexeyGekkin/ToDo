from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot.main import bot
from app.database import AsyncSessionLocal
from app.notifications.telegram import send_reminder
from app.services.reminder_service import (
    complete_reminder,
    get_due_reminders,
)


async def process_reminders():
    async with AsyncSessionLocal() as db:
        reminders = await get_due_reminders(db)

        for reminder in reminders:
            todo = reminder.todo

            try:
                sent = await send_reminder(
                    bot,
                    todo.user,
                    todo,
                    reminder.is_missed,
                )

                if sent:
                    complete_reminder(reminder)
                    await db.commit()

            except Exception as exc:
                await db.rollback()

                print(
                    f"Ошибка отправки напоминания "
                    f"для задачи {todo.id}: {exc}"
                )


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        process_reminders,
        "interval",
        minutes=1,
        id="process_reminders",
        max_instances=1,
        coalesce=True,
    )

    return scheduler
