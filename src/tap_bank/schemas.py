from pydantic import BaseModel as BaseScheme


class Payment(BaseScheme):
    type: str
    bank: str


class OrderRequest(BaseScheme):
    amount: float
    currency: str
    payment: Payment
