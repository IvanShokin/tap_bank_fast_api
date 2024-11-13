from uuid import uuid4, UUID

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from src.database.base_models import Base
from src.database.field_typing import str_255
from src.tap_bank.models import Order


class User(Base):
    __tablename__ = 'user'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str_255] = mapped_column(unique=True)
    hashed_password: Mapped[str_255]
    is_superuser: Mapped[bool] = mapped_column(default=False)

    first_name: Mapped[str_255]
    last_name: Mapped[str_255]
    phone: Mapped[str_255]
    email: Mapped[str_255]

    balance: Mapped[float] = mapped_column(default=0.0, server_default='0.0')

    orders: Mapped[Order] = relationship(uselist=True, backref=backref('user', uselist=True, cascade='all'))

    __table_args__ = (
        CheckConstraint('balance >= 0.0', name='check_balance_minimum'),
    )
