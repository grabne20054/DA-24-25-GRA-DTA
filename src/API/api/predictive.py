from fastapi import APIRouter, Depends
from typing import Annotated

from api.auth import is_token_valid

from crud import crud
from api.constants import VERSION, PREDICTIVE

router = APIRouter()

@router.get(f"/{VERSION}/{PREDICTIVE}/customers-growth/", status_code=212)
async def get_customers_growth(token: Annotated[str, Depends(is_token_valid)], one_day: bool = False ,seven_days: bool = False, month: bool = False, year: bool = False):
    data = await crud.get_customers_growth(one_day=one_day, seven_days=seven_days ,month=month, year=year)
    return data

@router.get(f"/{VERSION}/{PREDICTIVE}/cumulative-customers-growth/", status_code=212)
async def get_cumulative_customers_growth(token: Annotated[str, Depends(is_token_valid)], one_day: bool = False ,seven_days: bool = False, month: bool = False, year: bool = False):
    data = await crud.get_cumulative_customers_growth(one_day=one_day, seven_days=seven_days ,month=month, year=year)
    return data

@router.get(f"/{VERSION}/{PREDICTIVE}/orders-growth/", status_code=212)
async def get_orders_growth(token: Annotated[str, Depends(is_token_valid)], one_day: bool = False ,seven_days: bool = False, month: bool = False, year: bool = False):
    data = await crud.get_orders_growth(one_day=one_day, seven_days=seven_days ,month=month, year=year)
    return data

@router.get(f"/{VERSION}/{PREDICTIVE}/cumulative-orders-growth/", status_code=212)
async def get_cumulative_orders_growth(token: Annotated[str, Depends(is_token_valid)], one_day: bool = False ,seven_days: bool = False, month: bool = False, year: bool = False):
    data = await crud.get_cumulative_orders_growth(one_day=one_day, seven_days=seven_days ,month=month, year=year)
    return data