import jwt
import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from app.models.user import User
from app.config import Config
from app.database import engine  # assumes you have `engine` set up

# Create a session factory
def get_session():
    return Session(bind=engine)


def create_user(email, name, password):
    with get_session() as session:
        user_id = str(uuid.uuid4())
        created_at = datetime.datetime.utcnow()

        user = User(
            user_id=user_id,
            email=email,
            name=name,
            password_hash=generate_password_hash(password),
            created_at=created_at,
            updated_at=created_at,
        )

        session.add(user)
        session.commit()
        session.refresh(user)  # refresh to get updated values from DB
        
        return user


def get_user_by_email(email: str) -> User | None:
    with get_session() as session:
        return session.query(User).filter(User.email == email).first()


def get_user_by_id(user_id: str) -> User | None:
    with get_session() as session:
        return session.query(User).filter(User.user_id == user_id).first()


def verify_password(user: User, password: str) -> bool:
    return check_password_hash(user.password_hash, password)


def generate_token(user: User, secret_key: str) -> str:
    payload = {
        "user_id": user.user_id,
        "email": user.email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")
