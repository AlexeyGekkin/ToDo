import asyncio
import json
from datetime import date, datetime, time
from typing import Optional
from urllib.parse import parse_qs
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette import status

from app.database import SessionLocal
from app.models.user_model import User
from app.models.todo_model import ToDo, ReminderType
from app.routers.user_router import router as user_router
from app.routers.todo_router import router as todo_router
from app.bot.main import bot, dp

templates = Jinja2Templates(directory="app/templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        me = await bot.get_me()
        print(f"Успешное подключение к Telegram! Бот: @{me.username}")
    except Exception as e:
        print(f"Ошибка подключения к Telegram: {e}")
        print("Подсказка: Проверь VPN / TUN-режим или интернет-соединение.")

    bot_task = asyncio.create_task(dp.start_polling(bot))

    yield

    bot_task.cancel()
    try:
        await bot.session.close()
    except Exception:
        pass
    print("Telegram-бот остановлен.")


app = FastAPI(title="TODO App", lifespan=lifespan)

app.include_router(user_router)
app.include_router(todo_router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/webapp", response_class=HTMLResponse)
async def get_webapp(request: Request):
    return templates.TemplateResponse(request, "index.html")


def get_telegram_id(init_data: str) -> int:
    try:
        parsed = parse_qs(init_data)
        user_data = json.loads(parsed["user"][0])
        return user_data["id"]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid init_data")


class MiniAppToDoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_date: Optional[date] = None
    deadline_time: Optional[time] = None
    reminder_type: ReminderType = ReminderType.NONE
    init_data: str


class TaskStatusUpdate(BaseModel):
    completed: bool


@app.get("/api/telegram/todos")
async def get_todos_for_webapp(init_data: str):
    telegram_id = get_telegram_id(init_data)
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id).options(selectinload(User.todos))
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user.todos


@app.post("/api/telegram/todos")
async def create_todo_webapp(data: MiniAppToDoCreate):
    telegram_id = get_telegram_id(data.init_data)
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        remind_at = None
        if data.target_date:
            if data.reminder_type in (ReminderType.DEADLINE, ReminderType.BOTH) and data.deadline_time:
                remind_at = datetime.combine(data.target_date, data.deadline_time)
            elif data.reminder_type == ReminderType.MORNING:
                remind_at = datetime.combine(data.target_date, time(9, 0))

        todo = ToDo(
            title=data.title,
            description=data.description,
            target_date=data.target_date,
            deadline_time=data.deadline_time,
            remind_at=remind_at,
            reminder_type=data.reminder_type,
            user_id=user.id,
        )
        session.add(todo)
        await session.commit()
        await session.refresh(todo)
        return {"status": "ok", "id": todo.id}


@app.patch("/api/telegram/todos/{todo_id}")
async def update_todo_status(todo_id: int, status: TaskStatusUpdate, init_data: str):
    telegram_id = get_telegram_id(init_data)
    async with SessionLocal() as session:
        result = await session.execute(
            select(ToDo).join(User).where(ToDo.id == todo_id, User.telegram_id == telegram_id)
        )
        todo = result.scalars().first()
        if not todo:
            raise HTTPException(status_code=404, detail="Task not found")

        todo.completed = status.completed
        await session.commit()
        return {"status": "ok"}


@app.get("/api/telegram/profile")
async def get_profile_webapp(init_data: str):
    telegram_id = get_telegram_id(init_data)
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id).options(selectinload(User.todos))
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        total = len(user.todos)
        active = len([t for t in user.todos if not t.completed])

        return {
            "email": user.email,
            "active_count": active,
            "completed_count": total - active,
        }

@app.delete("/api/telegram/account")
async def delete_account_webapp(init_data: str):
    telegram_id = get_telegram_id(init_data)
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await session.delete(user)
        await session.commit()
        return {"status": "ok", "message": "Account deleted"}

