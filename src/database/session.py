import contextlib
from typing import AsyncIterator, Optional

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncConnection
)
from fastapi import Depends

from src.config import get_config, Config


class DataBaseSessionManager:
    _instance: Optional['DataBaseSessionManager'] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config: Config):
        self.config = config
        if not self._initialized:
            self.engine = create_async_engine(self.config.DATABASE_URL)
            self.session_maker = async_sessionmaker(self.engine, expire_on_commit=False)
        self._initialized = True

    async def close(self) -> None:
        if not self.engine:
            raise Exception("DatabaseSessionManager is not initialized")
        await self.engine.dispose()
        self.engine = None
        self.session_maker = None
        self._instance = None
        self._initialized = False

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if not self.session_maker:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self.session_maker() as session:
            try:
                yield session
                await session.commit()
            except exc.SQLAlchemyError:
                await session.rollback()
                raise

    @contextlib.asynccontextmanager
    async def connect_api_db(self) -> AsyncIterator[AsyncConnection]:
        if self.engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self.engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def connect_salt_db(self) -> AsyncIterator[AsyncConnection]:
        if self.engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self.engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    async def _create_all(self, connection: AsyncConnection, base_model_class):
        await connection.run_sync(base_model_class.metadata.create_all)  # type: ignore

    async def _drop_all(self, connection: AsyncConnection, base_model_class):
        await connection.run_sync(base_model_class.metadata.drop_all)  # type: ignore


async def get_session_manager(config: Config = Depends(get_config)):
    sessionmanager = DataBaseSessionManager(config)
    return sessionmanager


async def get_async_session(session_manager: DataBaseSessionManager = Depends(get_session_manager)):
    async with session_manager.session() as session:
        yield session
