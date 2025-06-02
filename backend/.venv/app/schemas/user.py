# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    fullname: Optional[str] = None

class UserRead(UserBase):
    id: int
    full_name: Optional[str]
    is_active: bool

    class Config:
        orm_mode = True
        
class UserLogin(UserBase):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
