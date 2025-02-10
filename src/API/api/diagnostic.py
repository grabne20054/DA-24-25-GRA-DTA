from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from crud import crud
from api.constants import VERSION, DIAGNOSTIC
from api.auth import is_token_valid


router = APIRouter()

@router.get(f"/{VERSION}/{DIAGNOSTIC}/products-orders-correlation/", status_code=210)
async def get_products_orders_correlation(token: Annotated[str, Depends(is_token_valid)]):
    try:
        data = await crud.get_products_orders_correlation()

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))    
    return data

@router.get(f"/{VERSION}/{DIAGNOSTIC}/products-orders-correlation/change-price", status_code=210)
async def get_changing_price_orders_correlation(token: Annotated[str, Depends(is_token_valid)], price_percentage: float = 0.1, n_random: int = 0):
    try:
        data = await crud.get_changing_price_orders_correlation(price_percentage=price_percentage, n_random=n_random)

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return data

@router.get(f"/{VERSION}/{DIAGNOSTIC}/items-bought-correlation/", status_code=210)
async def get_items_bought_correlation(token: Annotated[str, Depends(is_token_valid)], product_name: str, amount_combined_products: int):
    try:

        data = await crud.get_items_bought_correlation(product_name, amount_combined_products)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return data