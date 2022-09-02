# This file is responsible for signing , encoding , decoding and returning JWTS
from os import access
import time
from typing import Dict
import jwt
from decouple import config
from src.schemas import schemas
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.crud import crud
from passlib.context import CryptContext

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(user):
    try:
        token_val_dict = {
            "email": user.email,
            "role": user.role.value,
            "expires": time.time() + 600,
        }

        token = jwt.encode(token_val_dict, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return dict(access_token=token, token_type="bearer")
    except Exception as ex:
        print(str(ex))
        raise ex


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if decoded_token["expires"] < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token Expired! Login again",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return decoded_token
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = decodeJWT(token)
        return payload
    except:
        raise Exception("Token not valid")


def check_admin(payload: dict = Depends(verify_token)):
    role = payload.get("role")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this route",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return payload


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(email: str, password: str, db):
    user = await crud.get_user_by_email(email=email, db=db)
    if (not user) or (not verify_password(password, user.hashed_password)):
        return False
    return user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
