from fastapi import FastAPI
from app.routers.user_router import router as user_router
from app.routers.todo_router import router as todo_router
app = FastAPI()

app.include_router(user_router)
app.include_router(todo_router)

@app.get("/")
async def root():
    return {"ok": True}