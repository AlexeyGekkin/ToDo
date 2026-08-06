from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.lifespan import lifespan
from app.routers import (
    user_router,
    todo_router,
    telegram_router,
)

templates = Jinja2Templates(directory="app/templates")


def create_app(with_bot: bool = True) -> FastAPI:
    app = FastAPI(
        title="TODO App",
        lifespan=lifespan if with_bot else None,
    )

    app.include_router(user_router)
    app.include_router(todo_router)
    app.include_router(telegram_router)

    @app.get("/", response_class=HTMLResponse)
    async def root(request):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
        )

    @app.get("/webapp", response_class=HTMLResponse)
    async def webapp(request):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
        )

    return app