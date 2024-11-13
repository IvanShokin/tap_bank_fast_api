from src.base.service import BaseService
from src.tap_bank.repositories import OrderRepository
from src.tap_bank import models as tap_bank_models
from src.tap_bank.schemas import OrderRequest as NewOrder
from src.users.models import User
from src.users.service import UserService
from src.utils.exceptions import CustomHTTPException


class OrderService(BaseService[OrderRepository, tap_bank_models.Order]):

    async def create_order(self, current_user: User, new_order: NewOrder, user_service: UserService):
        if current_user.balance < new_order.amount:
            raise CustomHTTPException('User balance < order amount', status_code=400)
        order = await self.repository.create({
            'user_id': current_user.id,
            'amount': new_order.amount
        })
        user = await user_service.update(current_user, {'balance': current_user.balance - new_order.amount})
        return order
