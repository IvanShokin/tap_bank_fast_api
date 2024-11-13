from typing import Annotated

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, status

from src.tap_bank.dependencies import get_order_service
from src.tap_bank.service import OrderService
from src.users.dependencies import get_user_service
from src.users.service import UserService
from src.utils.exceptions import CustomHTTPException
from src.users.models import User
from src.users.utils import CurrentUserChecker
from src.config import get_config
from src.tap_bank.schemas import OrderRequest as OrderRequestSchema

tap_bank_route = APIRouter()
config = get_config()

HEADERS = {'Authorization': 'Bearer ' + config.TAP_BANK_API_TOKEN}


@tap_bank_route.get('/trade-methods/payout', tags=['Trade methods'], status_code=status.HTTP_200_OK)
async def payout(
        current_user: Annotated[User, Depends(CurrentUserChecker())],
):
    url = f'{config.TAP_BANK_BASE_URL}/public/api/v1/shop/trade-methods/payout'
    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url, headers=HEADERS) as response:
                return await response.json()
    except CustomHTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=str(error)
        )


@tap_bank_route.get('/trade-methods/payin', tags=['Trade methods'], status_code=status.HTTP_200_OK)
async def payin(
        current_user: Annotated[User, Depends(CurrentUserChecker())],
):
    url = f'{config.TAP_BANK_BASE_URL}/public/api/v1/shop/trade-methods'
    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url, headers=HEADERS) as response:
                return await response.json()
    except CustomHTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=str(error)
        )


@tap_bank_route.post('/create_order', tags=['Orders'], status_code=status.HTTP_200_OK)
async def create_order(
        order: OrderRequestSchema,
        current_user: Annotated[User, Depends(CurrentUserChecker())],
        user_service: Annotated[UserService, Depends(get_user_service)],
        order_service: Annotated[OrderService, Depends(get_order_service)],

):
    await order_service.create_order(current_user=current_user, new_order=order, user_service=user_service)
    url = f'{config.TAP_BANK_BASE_URL}/public/api/v1/shop/orders/sync-requisites'
    data = {
      'amount': int(order.amount),
      'currency': order.currency,
      'customer': {
        'id': str(current_user.id),
        'phone': current_user.phone,
        'name': f'{current_user.last_name} {current_user.first_name}',
        'email': current_user.email
      },
      'integration': {
        'callbackUrl': '',  # f'https://{config.API_HOST}:{config.API_PORT}/order_callback',
        'callbackMethod': 'post',
        'returnUrl': 'https://your-shop.com'
      },
      'payment': {
        'type': order.payment.type,
        'bank': order.payment.bank
      }
    }
    try:
        async with aiohttp.ClientSession() as client:
            async with client.post(url, headers=HEADERS, json=data) as response:
                return await response.json()

    except CustomHTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=str(error)
        )


@tap_bank_route.post('/order_callback', tags=['Orders'], status_code=status.HTTP_200_OK)
async def callback(
        data: dict
):
    # делай с callback то что нужно
    return data
