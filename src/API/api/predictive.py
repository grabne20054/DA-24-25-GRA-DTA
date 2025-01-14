from fastapi import APIRouter

from crud import crud
from api.constants import VERSION, PREDICTIVE

router = APIRouter()

@router.get(f"/{VERSION}/{PREDICTIVE}/customers-growth/", status_code=212)
async def get_customers_growth():
    data = await crud.get_customers_growth()
    return data

@router.get(f"/{VERSION}/{PREDICTIVE}/cumulative-customers-growth/", status_code=212)
async def get_cumulative_customers_growth():
    data = await crud.get_cumulative_customers_growth()
    return data

@router.get(f"/{VERSION}/{PREDICTIVE}/orders-growth/", status_code=212)
async def get_orders_growth():
    data = await crud.get_orders_growth()
    return data

@router.get(f"/{VERSION}/{PREDICTIVE}/cumulative-orders-growth/", status_code=212)
async def get_cumulative_orders_growth():
    data = await crud.get_cumulative_orders_growth()
    return data