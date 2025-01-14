from fastapi import APIRouter

from crud import crud
from api.constants import VERSION, DIAGNOSTIC

router = APIRouter()

@router.get(f"/{VERSION}/{DIAGNOSTIC}/products-orders-correlation/", status_code=210)
async def get_products_orders_correlation():
    data = await crud.get_products_orders_correlation()
    return data

@router.get(f"/{VERSION}/{DIAGNOSTIC}/itemss-bought-correlation/", status_code=210)
async def get_items_bought_correlation():
    data = await crud.get_items_bought_correlation()
    return data