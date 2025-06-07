from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import SessionLocal, User, UserCreate, UserDB

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/users", response_model=User)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Fixed: Changed 'disct()' to 'dict()'
    db_user = UserDB(**user.dict())
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users", response_model=List[User])  # Fixed: Changed "/user" to "/users"
async def list_users(skip: int=0, limit: int=100, db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(UserDB).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=User)  # Fixed: Changed "/user" to "/users"
async def get_user_byid(user_id: str, db: Session = Depends(get_db)):
    """Get a user by ID"""
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user