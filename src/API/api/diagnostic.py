from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from crud import crud
from api.constants import VERSION, DIAGNOSTIC
from api.auth import is_token_valid


router = APIRouter()

@router.get(f"/{VERSION}/{DIAGNOSTIC}/products-orders-correlation/", status_code=211)
async def get_products_orders_correlation(token: Annotated[str, Depends(is_token_valid)]):
    try:
        data = await crud.get_products_orders_correlation()
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))    


@router.get(f"/{VERSION}/{DIAGNOSTIC}/products-orders-correlation/change-price", status_code=211)
async def get_changing_price_orders_correlation(token: Annotated[str, Depends(is_token_valid)], price_percentage: float = 0.1, n_random: int = 0):
    try:
        data = await crud.get_changing_price_orders_correlation(price_percentage=price_percentage, n_random=n_random)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@router.get(f"/{VERSION}/{DIAGNOSTIC}/items-bought-correlation/", status_code=211)
async def get_items_bought_correlation(productId: str, amount_combined_products: int):
    try:
        data = await crud.get_items_bought_correlation(productId, amount_combined_products)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    