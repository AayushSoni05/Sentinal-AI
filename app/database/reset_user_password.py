from app.database.connection import SessionLocal
from app.database.models import User
from pwdlib import PasswordHash


USERNAME = "aayush_maker"
NEW_PASSWORD = "Maker@12345"

password_hash = PasswordHash.recommended()


db = SessionLocal()

try:
    user = (
        db.query(User)
        .filter(User.username == USERNAME)
        .first()
    )

    if user is None:
        print("User not found")
    else:
        user.password_hash = password_hash.hash(
            NEW_PASSWORD
        )

        db.commit()

        print(
            f"Password reset successfully for {USERNAME}"
        )

finally:
    db.close()