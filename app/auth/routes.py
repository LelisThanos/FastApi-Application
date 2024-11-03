from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import schemas
from .auth_logic import authenticate_user, register_user
from .schemas import Token
from ..dependencies import get_db
from .utils import create_access_token

router = APIRouter()


@router.post("/register", response_model=schemas.UserOut)
def register_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user)


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")
