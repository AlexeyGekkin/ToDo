import hashlib
import hmac
import json
import time
from urllib.parse import parse_qs

from fastapi import HTTPException

from app.config import BOT_TOKEN


def validate_init_data(init_data: str) -> int:
    parsed = parse_qs(init_data, keep_blank_values=True)
    telegram_hash = parsed.pop("hash", [None])[0]

    if telegram_hash is None:
        raise HTTPException(status_code=401, detail="Missing hash")

    auth_date_list = parsed.get("auth_date", [None])
    if not auth_date_list or not auth_date_list[0].isdigit():
        raise HTTPException(status_code=401, detail="Missing or invalid auth_date")

    auth_date = int(auth_date_list[0])
    now = time.time()

    if auth_date > now + 600:
        raise HTTPException(
            status_code=401,
            detail="Invalid auth_date",
        )

    if now - auth_date > 86400:
        raise HTTPException(
            status_code=401,
            detail="Init data has expired",
        )

    data_check_string = "\n".join(
        f"{key}={value[0]}" for key, value in sorted(parsed.items())
    )

    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(telegram_hash, calculated_hash):
        raise HTTPException(status_code=401, detail="Invalid init_data signature")

    try:
        user = json.loads(parsed["user"][0])
        return int(user["id"])
    except (KeyError, ValueError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Invalid user data")
