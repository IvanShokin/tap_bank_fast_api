from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.users.dependencies import get_user_service
from src.users.schemas import (
    Token as TokenSchema,
    User as UserSchema,
    UserRegister as UserRegisterSchema
)
from src.users.service import TokenService, UserService

from src.utils.exceptions import CustomHTTPException

users_router = APIRouter()


@users_router.post("/auth/registration", tags=['Authorization'], status_code=status.HTTP_200_OK, response_model=UserSchema)
async def registration(
        new_user: Annotated[UserRegisterSchema, Depends()],
        user_service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        new_user = await user_service.registration(new_user)
    except CustomHTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=str(error)
        )
    return new_user


@users_router.post("/auth/authorization", tags=["Authorization"], status_code=status.HTTP_200_OK, response_model=TokenSchema)
async def authorization(
        credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_service: Annotated[UserService, Depends(get_user_service)],
        token_service: Annotated[TokenService, Depends()]
):
    try:
        tokens = await user_service.authorization(credentials, token_service)
    except CustomHTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=str(error)
        )
    return tokens
