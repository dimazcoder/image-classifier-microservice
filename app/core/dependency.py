from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.controllers.property_controller import PropertyController
from app.schemas.user_schema import UserSchema
from app.services.jwt_service import JWTService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_property_controller():
    return PropertyController()


async def get_current_user(token: str = Depends(oauth2_scheme), service: JWTService = Depends(JWTService)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = service.get_user(token)
    except JWTError:
        raise credentials_exception

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: UserSchema = Depends(get_current_user)):
    return current_user
