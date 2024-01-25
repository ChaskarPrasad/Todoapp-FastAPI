from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos, admin, user
from starlette.staticfiles import StaticFiles

app = FastAPI()

models.Base.metadata.create_all(engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(todos.router) 
app.include_router(admin.router)
app.include_router(user.router)