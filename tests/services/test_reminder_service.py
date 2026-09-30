from datetime import UTC, datetime

from app.models.todo_model import ReminderType, ToDo
from app.services.reminder_service import (
    build_reminder,
    complete_reminder,
)


def test_build_reminder_not_missed():

    todo = ToDo(
        title="Test",
        reminder_type=ReminderType.MORNING,
        morning_remind_at=datetime(
            2026,
            8,
            10,
            4,
            0,
            tzinfo=UTC,
        ),
    )

    reminder = build_reminder(
        todo,
        "morning",
        todo.morning_remind_at,
        datetime(
            2026,
            8,
            10,
            3,
            55,
            tzinfo=UTC,
        ),
    )

    assert reminder.todo is todo
    assert reminder.reminder_type == "morning"
    assert reminder.remind_at == todo.morning_remind_at
    assert reminder.is_missed is False


def test_build_reminder_missed():

    todo = ToDo(
        title="Test",
        reminder_type=ReminderType.MORNING,
    )

    remind_at = datetime(
        2026,
        8,
        10,
        4,
        0,
        tzinfo=UTC,
    )

    reminder = build_reminder(
        todo,
        "morning",
        remind_at,
        datetime(
            2026,
            8,
            10,
            4,
            5,
            tzinfo=UTC,
        ),
    )

    assert reminder.is_missed is True


def test_complete_morning_reminder():

    todo = ToDo(
        title="Test",
        morning_remind_at=datetime(
            2026,
            8,
            10,
            4,
            0,
            tzinfo=UTC,
        ),
        deadline_remind_at=datetime(
            2026,
            8,
            10,
            14,
            30,
            tzinfo=UTC,
        ),
        reminder_type=ReminderType.BOTH,
    )

    reminder = build_reminder(
        todo,
        "morning",
        todo.morning_remind_at,
        datetime.now(UTC),
    )

    complete_reminder(reminder)

    assert todo.morning_remind_at is None
    assert todo.deadline_remind_at is not None


def test_complete_deadline_reminder():

    todo = ToDo(
        title="Test",
        morning_remind_at=datetime(
            2026,
            8,
            10,
            4,
            0,
            tzinfo=UTC,
        ),
        deadline_remind_at=datetime(
            2026,
            8,
            10,
            14,
            30,
            tzinfo=UTC,
        ),
        reminder_type=ReminderType.BOTH,
    )

    reminder = build_reminder(
        todo,
        "deadline",
        todo.deadline_remind_at,
        datetime.now(UTC),
    )

    complete_reminder(reminder)

    assert todo.morning_remind_at is not None
    assert todo.deadline_remind_at is None
