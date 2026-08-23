from uuid import uuid4

from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from app.database.repository import (
    get_role_by_name,
    get_user_by_username,
    get_user_by_email,
    create_user
)

from app.utils.logger import logger


password_hash = PasswordHash.recommended()


def hash_password(
    password: str
):
    return password_hash.hash(password)


def create_new_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    role_name: str
):
    existing_username = get_user_by_username(
        db=db,
        username=username
    )

    if existing_username is not None:
        return None, "Username already exists"

    existing_email = get_user_by_email(
        db=db,
        email=email
    )

    if existing_email is not None:
        return None, "Email already exists"

    role = get_role_by_name(
        db=db,
        role_name=role_name
    )

    if role is None:
        return None, "Role not found"

    password_hash_value = hash_password(password)

    user = create_user(
        db=db,
        user_id=str(uuid4()),
        username=username,
        email=email,
        password_hash=password_hash_value,
        role_id=role.id
    )

    logger.info(
        f"User created: "
        f"{user.username} | "
        f"Role: {role.name}"
    )

    return user, None