from fastapi import APIRouter, HTTPException, status, Path, Body, Request
from fastapi import Depends
from sqlalchemy.orm import Session
from src.models import models
from src.crud import crud
from src.db.database import SessionLocal, engine
from uvicorn.logging import logging
from src.schemas import schemas
from src.auth import auth_handler
import email_validator
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/user",
    tags=["Users"],
    responses={404: {"Error": "Not found"}},
)

logger = logging.getLogger("uvicorn.info")
models.Base.metadata.create_all(bind=engine)

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup")
async def create_user(db: Session = Depends(get_db), user: schemas.UserSchema = Body(...)):
    try:
        valid = email_validator.validate_email(email=user.email)
    except email_validator.EmailNotValidError:
        raise HTTPException(
            status_code=404, detail="Please enter a valid email")

    db_user = await crud.get_user_by_email(db, valid.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="User with that email already exists"
        )
    new_user = await crud.add_user(db, user)
    return auth_handler.create_token(new_user)


@router.post("/login")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await auth_handler.authenticate_user(email=form_data.username, password=form_data.password, db=db)

    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid Credentials")

    return auth_handler.create_token(user=user)
