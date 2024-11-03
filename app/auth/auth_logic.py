from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .models import User
from .schemas import UserCreate
from .utils import verify_password, get_password_hash

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def register_user(db: Session, user: UserCreate):
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None
