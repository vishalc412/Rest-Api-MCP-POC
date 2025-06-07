import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import sessionmaker
Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"
    # Fixed: String type for UUID primary key instead of Integer
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    age = Column(Integer)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))

class UserBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    age: Optional[int] = Field(None, ge=18, le=100)

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    age: Optional[int] = Field(None, ge=18, le=100)
    email: Optional[EmailStr] = Field(None)  # Removed 'unique=True' as it's not valid for Pydantic fields


class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Fixed: Use regular sqlite instead of aiosqlite for synchronous operations
engine = create_engine("sqlite:///./users.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the database
Base.metadata.create_all(bind=engine)