from typing import Annotated

from fastapi import Depends

from src.base.repository import get_repository
from src.users.service import UserService

from src.users.repositories import UserRepository


def get_user_service(
        repository: Annotated[UserRepository, Depends(get_repository(UserRepository))]
):
    return UserService(repository)
