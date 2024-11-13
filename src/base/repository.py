from typing import Callable, Generic, Iterable, Optional, Type, TypeVar, Union

from fastapi import Depends
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from src.database import session as session_module, base_models


Model = TypeVar('Model', bound=base_models.Base)


class BaseRepository(Generic[Model]):
    model: Type[Model]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, *args, **kwargs) -> Iterable[Model]:
        result = await self.session.scalars(select(self.model))
        return result.all()

    async def get_one(self, pk, *args, **kwargs) -> Optional[Model]:
        pk_column = inspect(self.model).primary_key[0]
        query = select(self.model).where(pk_column == pk)
        result = await self.session.scalar(query)
        if result:
            return result

    async def delete(self, pk, *args, **kwargs) -> bool:
        instance = await self.get_one(pk, *args, **kwargs)
        if not instance:
            return False
        await self.session.delete(instance)
        return True

    async def create(self, data: dict) -> Optional[Model]:
        instance = self.model(**data)
        self.session.add(instance)

        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            return None
        return instance

    def pagination(self, query: Select, page: int, limit: int) -> Select:
        offset = (page - 1) * limit
        return query.limit(limit).offset(offset)

    def order_by(self, query: Select, descending: bool, column_name: str) -> Select:
        order_column = getattr(self.model, column_name)
        order_column = order_column.desc() if descending else order_column.asc()
        return query.order_by(order_column)


def get_repository(
        repository_type: Type[BaseRepository],
) -> Callable[[AsyncSession], BaseRepository]:
    def func(session: AsyncSession = Depends(session_module.get_async_session)) -> BaseRepository:
        return repository_type(session)

    return func
