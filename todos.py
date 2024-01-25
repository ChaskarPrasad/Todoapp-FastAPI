from typing import Annotated
from fastapi import APIRouter, Depends, Request, Form
import models
from database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette import status

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[models.Users, Depends(get_current_user)]


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: db_dependency):
    todos = db.query(models.Todos).filter(models.Todos.owner_id == 1).all()
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    
    return templates.TemplateResponse("add-todo.html", {"request": request})

@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(request:Request,
                      db: db_dependency,
                      title:str=Form(...),
                      description: str=Form(...),
                      priority:int=Form(...),
                      ):
    todo_model = models.Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.completed = False
    todo_model.owner_id = 1
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    

@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_by_id(request: Request, 
                          todo_id: int,
                          db: db_dependency):
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo})

@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request:Request,
                    todo_id: int,
                    db: db_dependency,
                    title:str=Form(...),
                    description: str=Form(...),
                    priority:int=Form(...),
                    ):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    
@router.get("/delete/{todo_id}", response_class=HTMLResponse)
async def delete_todo(request:Request,
                      todo_id: int,
                      db: db_dependency):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == 1).first()
    if todo_model is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request:Request,
                        todo_id: int,
                        db: db_dependency,
                        ):
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    todo.complete = not todo.complete
    db.add(todo)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
