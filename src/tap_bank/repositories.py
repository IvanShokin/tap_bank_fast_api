from src.tap_bank import models
from src.base.repository import BaseRepository


class OrderRepository(BaseRepository[models.Order]):
    model = models.Order
