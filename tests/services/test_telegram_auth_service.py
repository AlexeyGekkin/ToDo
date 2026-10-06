import hashlib
import hmac
import json
import time
from unittest.mock import patch
from urllib.parse import parse_qs, urlencode

import pytest
from fastapi import HTTPException

from app.services.telegram_auth_service import validate_init_data

TEST_BOT_TOKEN = "test_bot_token"


def build_init_data(
    auth_date: int,
    user_id: int = 123456,
) -> str:
    data = {
        "auth_date": str(auth_date),
        "user": json.dumps({"id": user_id}),
    }

    data_check_string = "\n".join(
        f"{key}={value}"
        for key, value in sorted(data.items())
    )

    secret_key = hmac.new(
        b"WebAppData",
        TEST_BOT_TOKEN.encode(),
        hashlib.sha256,
    ).digest()

    telegram_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    data["hash"] = telegram_hash

    return urlencode(data)

def test_validate_init_data_rejects_future_auth_date():
    init_data = build_init_data(
        auth_date=int(time.time()) + 3600
    )

    with patch(
        "app.services.telegram_auth_service.BOT_TOKEN",
        TEST_BOT_TOKEN,
    ), pytest.raises(HTTPException) as exc:
        validate_init_data(init_data)

    assert exc.value.status_code == 401

def test_validate_init_data_returns_user_id():
    init_data = build_init_data(
        auth_date=int(time.time()),
        user_id=123456,
    )

    with patch(
        "app.services.telegram_auth_service.BOT_TOKEN",
        TEST_BOT_TOKEN,
    ):
        telegram_id = validate_init_data(init_data)

    assert telegram_id == 123456

def test_validate_init_data_rejects_invalid_signature():
    init_data = build_init_data(
        auth_date=int(time.time()),
        user_id=123456,
    )

    params = parse_qs(init_data)
    params["hash"] = ["0" * 64]

    invalid_init_data = urlencode(
        {key: value[0] for key, value in params.items()}
    )

    with patch(
        "app.services.telegram_auth_service.BOT_TOKEN",
        TEST_BOT_TOKEN,
    ), pytest.raises(HTTPException) as exc:
        validate_init_data(invalid_init_data)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid init_data signature"

def test_validate_init_data_rejects_expired_auth_date():
    init_data = build_init_data(
        auth_date=int(time.time()) - 86401,
        user_id=123456,
    )

    with patch(
        "app.services.telegram_auth_service.BOT_TOKEN",
        TEST_BOT_TOKEN,
    ), pytest.raises(HTTPException) as exc:
        validate_init_data(init_data)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Init data has expired"