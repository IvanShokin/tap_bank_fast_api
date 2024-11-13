from typing import TypeVar, Iterable, Optional, Generic

from src.base.repository import BaseRepository
from src.database.base_models import Base


RepositoryType = TypeVar('RepositoryType', bound=BaseRepository)
MainModel = TypeVar('MainModel', bound=Base)


class BaseService(Generic[RepositoryType, MainModel]):
    def __init__(self, repository: RepositoryType):
        self.repository = repository

    async def get_all(self, *args, **kwargs) -> Iterable[MainModel]:
        return await self.repository.get_all(*args, **kwargs)

    async def get_one(self, *args, **kwargs) -> Optional[MainModel]:
        return await self.repository.get_one(*args, **kwargs)

    async def create(self, *args, **kwargs) -> Optional[MainModel]:
        return await self.repository.create(*args, **kwargs)

    async def delete(self, *args, **kwargs) -> bool:
        return await self.repository.delete(*args, **kwargs)
