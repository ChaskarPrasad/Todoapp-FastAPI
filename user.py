from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Path
from pydantic import BaseModel, Field
import models
from database import SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .auth import get_current_user

router = APIRouter(
    prefix='/user',
    tags=['user']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserVerification(BaseModel):
    password: str 
    new_password: str = Field(min_length=3)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[models.Users, Depends(get_current_user)]

# This endpoint should return all info about the user
@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid authentication credentials')
    return db.query(models.Users).filter(models.Users.id == user.get("user_id")).first()

# Change password endpoint

@router.put("/change_password", status_code=status.HTTP_200_OK)
async def change_password(user: user_dependency,
                          db: db_dependency,
                          user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid authentication credentials')
    user_model = db.query(models.Users).filter(models.Users.id == user.get("user_id")).first()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid old password')
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    return {'detail': 'Password changed successfully'}

# route to update phone number
@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_200_OK)
async def update_phone_number(user: user_dependency,
                              db: db_dependency,
                              phone_number: str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid authentication credentials')
    user_model = db.query(models.Users).filter(models.Users.id == user.get("user_id")).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()
    return {'detail': 'Phone number updated successfully'}
