from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate
from fastapi.responses import JSONResponse

async def create_user(db: Session, user: UserCreate):
    try:
        is_exists = db.query(User).filter(User.email == user.email).first()
        if is_exists:
            return JSONResponse({"error": "Email already exists"}, status_code=400)
        
        db_user = User(name=user.name, email=user.email)
        
        db.add(db_user)    
        db.commit()
        db.refresh(db_user)
        
        return db_user
    except Exception as e:
        db.rollback()
        return JSONResponse({"error": str(e)}, status_code=400)

async def get_all_users(db: Session):
    return db.query(User).all()

