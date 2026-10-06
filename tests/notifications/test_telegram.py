from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.notifications.telegram import send_reminder


@pytest.mark.asyncio
async def test_send_reminder_without_telegram_id():
    bot = SimpleNamespace(
        send_message=AsyncMock()
    )

    user = SimpleNamespace(
        telegram_id=None
    )

    todo = SimpleNamespace(
        title="Test todo",
        description=None,

    )

    result = await send_reminder(
        bot,
        user,
        todo,
        is_missed=False,
    )

    assert result is False
    bot.send_message.assert_not_awaited()

@pytest.mark.asyncio
async def test_send_reminder():
    bot = SimpleNamespace(
        send_message=AsyncMock()
    )

    user = SimpleNamespace(
        telegram_id=123456
    )

    todo = SimpleNamespace(
        title="Купить молоко",
        description=None,
    )

    result = await send_reminder(
        bot,
        user,
        todo,
        is_missed=False,
    )

    assert result is True

    bot.send_message.assert_awaited_once_with(
        chat_id=123456,
        text="Напоминание: «Купить молоко»",
    )

@pytest.mark.asyncio
async def test_send_missed_reminder():
    bot = SimpleNamespace(
        send_message=AsyncMock()
    )

    user = SimpleNamespace(
        telegram_id=123456
    )

    todo = SimpleNamespace(
        title="Оплатить интернет",
        description=None,
    )

    result = await send_reminder(
        bot,
        user,
        todo,
        is_missed=True,
    )

    assert result is True

    bot.send_message.assert_awaited_once_with(
        chat_id=123456,
        text="Извините, пропущена задача: «Оплатить интернет»",
    )

@pytest.mark.asyncio
async def test_send_reminder_with_description():
    bot = SimpleNamespace(
        send_message=AsyncMock()
    )

    user = SimpleNamespace(
        telegram_id=123456
    )

    todo = SimpleNamespace(
        title="Купить молоко",
        description="2 литра, 3.2%",
    )

    result = await send_reminder(
        bot,
        user,
        todo,
        is_missed=False,
    )

    assert result is True

    bot.send_message.assert_awaited_once_with(
        chat_id=123456,
        text=(
            "Напоминание: «Купить молоко»\n"
            "Описание: 2 литра, 3.2%"
        ),
    )