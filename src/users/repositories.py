from typing import Optional

from sqlalchemy import select

from src.users import models
from src.base.repository import BaseRepository


class UserRepository(BaseRepository[models.User]):
    model = models.User

    async def set_superuser_status_by_username(self, username, status: bool) -> Optional[models.User]:
        query = select(self.model).where(self.model.username == username)
        user = await self.session.scalar(query)
        if user:
            user.is_superuser = status
            return user

    async def set_superuser_status_by_id(self, id, status: bool) -> Optional[models.User]:
        query = select(self.model).where(self.model.id == id)
        user = await self.session.scalar(query)
        if user:
            user.is_superuser = status
            return user

    async def get_one(self, pk, *args, **kwargs):
        query = select(self.model).where(self.model.id == pk)
        result = await self.session.scalar(query)
        return result

    async def get_one_by_username(self, username, *args, **kwargs):
        query = select(self.model).where(self.model.username == username)
        result = await self.session.scalar(query)
        return result

    async def update(self, user: models.User, data: dict):
        for key, value in data.items():
            setattr(user, key, value)
        return user
