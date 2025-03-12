from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from schemas.user import UserCreate, UserOut
from crud.user import create_user, get_all_users

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/user/")
async def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    return await create_user(db=db, user=user)


@router.get("/users/", response_model=list[UserOut])
async def get_users(db: Session = Depends(get_db)):
    return await get_all_users(db=db)
