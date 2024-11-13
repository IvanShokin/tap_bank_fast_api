from dataclasses import dataclass
from typing import Annotated, Optional
from enum import Enum

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.users.models import User
from src.users.service import UserService, TokenService
from src.users.dependencies import get_user_service


security = HTTPBearer()


async def get_current_user(
    token_service: Annotated[TokenService, Depends()],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    token = credentials.credentials
    try:
        payload = await token_service.decode_token(token)
        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token is not valid'
            )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token is not valid'
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token is expired'
        )
    user = await user_service.get_one(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User {user_id} not found.'
        )
    return user


@dataclass(frozen=True)  # https://stackoverflow.com/questions/75829870/fast-api-override-dependency-as-a-class
class CurrentUserChecker:

    allowed_permissions: Optional[tuple[Enum]] = None

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not await self._has_permissions(current_user):
            raise HTTPException(status_code=403, detail='Forbidden')
        return current_user

    async def _has_permissions(self, current_user: User) -> bool:
        if current_user.is_superuser or not self.allowed_permissions:
            return True
        for role in current_user.roles:
            for permission in role.permissions:
                if permission.name in self.allowed_permissions:
                    return True
        return False
