from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.dependencies import get_db
from app.routers import (
    telegram_router,
    todo_router,
    user_router,
)

templates = Jinja2Templates(directory="app/templates")


def create_app(with_bot: bool = True) -> FastAPI:
    if with_bot:
        from app.lifespan import lifespan

    app = FastAPI(
        title="TODO App",
        lifespan=lifespan if with_bot else None,
    )

    app.include_router(user_router)
    app.include_router(todo_router)
    app.include_router(telegram_router)

    @app.get("/health", include_in_schema=False)
    async def health(db=Depends(get_db)):
        await db.execute(text("SELECT 1"))
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="browser.html",
        )

    @app.get("/webapp", response_class=HTMLResponse)
    async def webapp(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
        )

    return app

