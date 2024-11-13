from typing import Annotated

from fastapi import Depends

from src.base.repository import get_repository
from src.tap_bank.service import OrderService

from src.tap_bank.repositories import OrderRepository


def get_order_service(
        repository: Annotated[OrderRepository, Depends(get_repository(OrderRepository))]
):
    return OrderService(repository)
