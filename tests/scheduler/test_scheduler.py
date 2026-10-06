from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.scheduler.scheduler import process_reminders


@pytest.mark.asyncio
async def test_process_reminders_commits_each_sent_reminder():
    db = AsyncMock()

    session_context = MagicMock()
    session_context.__aenter__ = AsyncMock(return_value=db)
    session_context.__aexit__ = AsyncMock(return_value=None)

    reminder_1 = SimpleNamespace(
        todo=SimpleNamespace(
            id=1,
            user=object(),
            morning_remind_at=object(),
            deadline_remind_at=None,
        ),
        reminder_type="morning",
        is_missed=False,
    )

    reminder_2 = SimpleNamespace(
        todo=SimpleNamespace(
            id=2,
            user=object(),
            morning_remind_at=object(),
            deadline_remind_at=None,
        ),
        reminder_type="morning",
        is_missed=False,
    )

    with (
        patch(
            "app.scheduler.scheduler.AsyncSessionLocal",
            return_value=session_context,
        ),
        patch(
            "app.scheduler.scheduler.get_due_reminders",
            new=AsyncMock(return_value=[reminder_1, reminder_2]),
        ),
        patch(
            "app.scheduler.scheduler.send_reminder",
            new=AsyncMock(return_value=True),
        ),
    ):
        await process_reminders()

    assert db.commit.await_count == 2
@pytest.mark.asyncio
async def test_process_reminders_does_not_complete_unsent_reminder():
    db = AsyncMock()

    session_context = MagicMock()
    session_context.__aenter__ = AsyncMock(return_value=db)
    session_context.__aexit__ = AsyncMock(return_value=None)

    remind_at = object()

    reminder = SimpleNamespace(
        todo=SimpleNamespace(
            id=1,
            user=object(),
            morning_remind_at=remind_at,
            deadline_remind_at=None,
        ),
        reminder_type="morning",
        is_missed=False,
    )

    with (
        patch(
            "app.scheduler.scheduler.AsyncSessionLocal",
            return_value=session_context,
        ),
        patch(
            "app.scheduler.scheduler.get_due_reminders",
            new=AsyncMock(return_value=[reminder]),
        ),
        patch(
            "app.scheduler.scheduler.send_reminder",
            new=AsyncMock(return_value=False),
        ),
    ):
        await process_reminders()

    assert reminder.todo.morning_remind_at is remind_at
    assert db.commit.await_count == 0

@pytest.mark.asyncio
async def test_process_reminders_continues_after_send_error():
    db = AsyncMock()

    session_context = MagicMock()
    session_context.__aenter__ = AsyncMock(return_value=db)
    session_context.__aexit__ = AsyncMock(return_value=None)

    reminder_1 = SimpleNamespace(
        todo=SimpleNamespace(
            id=1,
            user=object(),
            morning_remind_at=object(),
            deadline_remind_at=None,
        ),
        reminder_type="morning",
        is_missed=False,
    )

    reminder_2 = SimpleNamespace(
        todo=SimpleNamespace(
            id=2,
            user=object(),
            morning_remind_at=object(),
            deadline_remind_at=None,
        ),
        reminder_type="morning",
        is_missed=False,
    )

    send_mock = AsyncMock(
        side_effect=[
            RuntimeError("Telegram error"),
            True,
        ]
    )

    with (
        patch(
            "app.scheduler.scheduler.AsyncSessionLocal",
            return_value=session_context,
        ),
        patch(
            "app.scheduler.scheduler.get_due_reminders",
            new=AsyncMock(
                return_value=[
                    reminder_1,
                    reminder_2,
                ]
            ),
        ),
        patch(
            "app.scheduler.scheduler.send_reminder",
            new=send_mock,
        ),
    ):
        await process_reminders()

    assert send_mock.await_count == 2

    assert reminder_1.todo.morning_remind_at is not None
    assert reminder_2.todo.morning_remind_at is None

    assert db.rollback.await_count == 0
    assert db.commit.await_count == 1

@pytest.mark.asyncio
async def test_process_reminders_stops_after_commit_error():
    db = AsyncMock()
    db.commit.side_effect = RuntimeError("Database error")

    session_context = MagicMock()
    session_context.__aenter__ = AsyncMock(return_value=db)
    session_context.__aexit__ = AsyncMock(return_value=None)

    reminder_1 = SimpleNamespace(
        todo=SimpleNamespace(
            id=1,
            user=object(),
            morning_remind_at=object(),
            deadline_remind_at=None,
        ),
        reminder_type="morning",
        is_missed=False,
    )

    reminder_2 = SimpleNamespace(
        todo=SimpleNamespace(
            id=2,
            user=object(),
            morning_remind_at=object(),
            deadline_remind_at=None,
        ),
        reminder_type="morning",
        is_missed=False,
    )

    send_mock = AsyncMock(return_value=True)

    with (
        patch(
            "app.scheduler.scheduler.AsyncSessionLocal",
            return_value=session_context,
        ),
        patch(
            "app.scheduler.scheduler.get_due_reminders",
            new=AsyncMock(
                return_value=[
                    reminder_1,
                    reminder_2,
                ]
            ),
        ),
        patch(
            "app.scheduler.scheduler.send_reminder",
            new=send_mock,
        ),
    ):
        await process_reminders()

    assert send_mock.await_count == 1
    assert db.commit.await_count == 1
    assert db.rollback.await_count == 1