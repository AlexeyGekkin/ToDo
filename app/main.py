from fastapi import FastAPI
from app.routers.user_router import router as user_router
from app.routers.todo_router import router as todo_router
app = FastAPI()

app.include_router(user_router)
app.include_router(todo_router)
print(app.openapi()["paths"].keys())
print([route.path for route in app.routes])
for route in app.routes:
    print(route.path, getattr(route, "include_in_schema", None))
@app.get("/")
async def root():
    return {"ok": True}