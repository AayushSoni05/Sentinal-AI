from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):

    username: str
    email: EmailStr
    password: str
    role: str


class UserResponse(BaseModel):

    id: str
    username: str
    email: str
    role: str
    status: str