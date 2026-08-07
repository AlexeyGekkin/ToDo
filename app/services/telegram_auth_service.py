import hashlib
import hmac
import json
from urllib.parse import parse_qs

from fastapi import HTTPException

from app.config import BOT_TOKEN


def validate_init_data(init_data: str) -> int:

    parsed = parse_qs(
        init_data,
        keep_blank_values=True
    )

    telegram_hash = parsed.pop(
        "hash",
        [None]
    )[0]

    if telegram_hash is None:
        raise HTTPException(
            status_code=401,
            detail="Missing hash"
        )

    data_check_string = "\n".join(
        f"{key}={value[0]}"
        for key, value in sorted(parsed.items())
    )

    secret_key = hmac.new(
        b"WebAppData",
        BOT_TOKEN.encode(),
        hashlib.sha256,
    ).digest()

    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        telegram_hash,
        calculated_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid init_data signature"
        )

    try:
        user = json.loads(
            parsed["user"][0]
        )

        return int(user["id"])

    except (KeyError, ValueError, json.JSONDecodeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid user data"
        )