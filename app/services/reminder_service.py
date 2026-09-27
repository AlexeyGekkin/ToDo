from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo_model import ToDo


def build_reminder(
    todo: ToDo,
    reminder_type: str,
    remind_at: datetime,
    missed_after: datetime,
) -> dict:
    return {
        "todo": todo,
        "type": reminder_type,
        "remind_at": remind_at,
        "is_missed": remind_at < missed_after,
    }


async def get_due_reminders(
    db: AsyncSession,
) -> list[dict]:
    now = datetime.now(timezone.utc)
    missed_after = now - timedelta(minutes=5)

    query = (
        select(ToDo)
        .options(selectinload(ToDo.user))
        .where(
            ToDo.completed.is_(False),
            (
                    (
                            ToDo.morning_remind_at.is_not(None)
                            & (ToDo.morning_remind_at <= now)
                    )
                    |
                    (
                            ToDo.deadline_remind_at.is_not(None)
                            & (ToDo.deadline_remind_at <= now)
                    )
            ),
        )
    )

    result = await db.execute(query)
    todos = result.scalars().all()

    reminders = []

    for todo in todos:
        reminder_times = [
            ("morning", todo.morning_remind_at),
            ("deadline", todo.deadline_remind_at),
        ]

        for reminder_type, remind_at in reminder_times:
            if remind_at is not None:
                reminders.append(
                    build_reminder(
                        todo,
                        reminder_type,
                        remind_at,
                        missed_after,
                    )
                )

    reminders.sort(
        key=lambda reminder: reminder["remind_at"]
    )

    return reminders

async def complete_reminder(
    reminder: dict,
    db: AsyncSession,
) -> None:
    todo = reminder["todo"]

    if reminder["type"] == "morning":
        todo.morning_remind_at = None

    elif reminder["type"] == "deadline":
        todo.deadline_remind_at = None

    await db.commit()