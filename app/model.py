
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import Column, Integer, String
from database import Base

# SQLAlchemy User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

# Pydantic schemas
class userSchema(BaseModel):
    fullname: str = Field(default=None)
    email: EmailStr = Field(default=None)
    password: str = Field(default=None, min_length=6, max_length=20)
    model_config = {"from_attributes": True}

class userLoginSchema(BaseModel):
    email: EmailStr = Field(default=None)
    password: str = Field(default=None, min_length=6, max_length=20)
    model_config = {"from_attributes": True}

