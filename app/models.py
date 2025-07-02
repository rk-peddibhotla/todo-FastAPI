from pydantic import BaseModel
from typing import Optional
from pydantic import EmailStr

class TodoModel(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    owner: Optional[str] = None


class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserInDB(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str

