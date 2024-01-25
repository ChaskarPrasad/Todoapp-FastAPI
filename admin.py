from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Path
from pydantic import BaseModel, Field
import models
from database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[models.Users, Depends(get_current_user)]

@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Only admin can access this route')
    return db.query(models.Todos).all()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo(user:user_dependency,
                      db: db_dependency,
                      todo_id: int = Path(gt=0)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Only admin can access this route')
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo:
        db.delete(todo)
        db.commit()
        return {'message': 'Todo deleted successfully'}
    raise HTTPException(status_code=404, detail="Todo not found")
