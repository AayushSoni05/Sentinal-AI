from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal

from app.schemas.user import UserCreate

from app.services.user_service import (
    create_new_user
)


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/users")
def create_user(
    request: UserCreate,
    db: Session = Depends(get_db)
):
    user, error = create_new_user(
        db=db,
        username=request.username,
        email=request.email,
        password=request.password,
        role_name=request.role
    )

    if user is None:
        raise HTTPException(
            status_code=400,
            detail=error
        )

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.name,
        "status": user.status,
        "message": "User created successfully"
    }