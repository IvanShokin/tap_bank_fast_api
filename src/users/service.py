from datetime import datetime, timedelta
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.base.service import BaseService
from src.config import Config, get_config
from src.users import models
from src.users.repositories import UserRepository
from src.users.schemas import UserRegister
from src.utils.exceptions import CustomHTTPException

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserService(BaseService[UserRepository, models.User]):

    async def registration(self, new_user: UserRegister):
        exist_user = await self.repository.get_one_by_username(new_user.username)
        if exist_user:
            raise CustomHTTPException(
                message='Username is already exist',
                status_code=401,
            )

        new_user = await self.create({
            **new_user.model_dump(exclude={'password'}),
            'hashed_password': pwd_context.hash(new_user.password)
        })
        return new_user

    async def authorization(self, credentials: OAuth2PasswordRequestForm, token_service):
        user = await self.repository.get_one_by_username(credentials.username)
        if not (user and pwd_context.verify(credentials.password, user.hashed_password)):
            raise CustomHTTPException(
                message='Incorrect username or password',
                status_code=401,
            )

        access_token = await token_service.create_access_token(data={"id": str(user.id)})
        refresh_token = await token_service.create_refresh_token(data={"id": str(user.id)})

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }

    async def set_superuser_status_by_username(self, username, status: bool):
        return await self.repository.set_superuser_status_by_username(username, status)

    async def set_superuser_status_by_id(self, current_user: models.User, id: UUID, status: bool):
        if current_user.id == id:
            raise CustomHTTPException(
                message='You cannot change superuser status for yourself.',
                status_code=403
            )
        return await self.repository.set_superuser_status_by_id(id, status)

    async def update(self, *args, **kwargs):
        return await self.repository.update(*args, **kwargs)


class TokenService:
    def __init__(self, config: Config = Depends(get_config)):
        self.config = config

    async def create_access_token(self, data: dict) -> str:
        return await self._create_token(
            expire_minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES,
            data=data
        )

    async def create_refresh_token(self, data: dict) -> str:
        return await self._create_token(
            expire_minutes=self.config.REFRESH_TOKEN_EXPIRE_MINUTES,
            data=data
        )

    async def _create_token(
            self,
            expire_minutes: int,
            data: dict,
    ):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            payload=to_encode,
            key=self.config.JWT_PRIVATE_KEY.get_secret_value(),
            algorithm=self.config.JWT_ALGORITHM,
        )
        return encoded_jwt

    async def decode_token(self, token: str) -> dict:
        payload = jwt.decode(
            jwt=token,
            key=self.config.JWT_PUBLIC_KEY.get_secret_value(),
            algorithms=[self.config.JWT_ALGORITHM]
        )
        return payload

    async def get_user_id_from_token(self, token: str, token_service: 'TokenService') -> str:
        try:
            payload = await token_service.decode_token(token)
            user_id = payload.get("id")
            if user_id is None:
                raise CustomHTTPException(
                    status_code=401,
                    message='Token is not valid'
                )
        except jwt.DecodeError:
            raise CustomHTTPException(
                status_code=401,
                message='Token is not valid'
            )
        except jwt.ExpiredSignatureError:
            raise CustomHTTPException(
                status_code=401,
                message='Token is expired'
            )
        return user_id
