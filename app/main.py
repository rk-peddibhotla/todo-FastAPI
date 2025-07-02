from fastapi import FastAPI
from app.routes import router as todo_router
from app.auth import router as auth_router

app = FastAPI()

app.include_router(todo_router, tags=["Todos"])
app.include_router(auth_router, tags=["Auth"])



@app.get("/")
def read_root():
    return {"msg": "Todo API is running"}
