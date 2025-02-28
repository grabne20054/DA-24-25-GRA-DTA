from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from crud import crud
from api.constants import VERSION, DIAGNOSTIC
from api.auth import is_token_valid


router = APIRouter()

@router.get(f"/{VERSION}/{DIAGNOSTIC}/products-orders-correlation/", status_code=211)
async def get_products_orders_correlation(token: Annotated[str, Depends(is_token_valid)]):
    """
    Get the correlation between products and orders.

    **Args:**
    - token (str)

    **Raises:**
    - HTTPException: If there is an error, it will raise a 400 error.

    **Returns:**
    - dict: The correlation between products and orders
    """
    try:
        data = await crud.get_products_orders_correlation()
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))    


@router.get(f"/{VERSION}/{DIAGNOSTIC}/products-orders-correlation/change-price", status_code=211)
async def get_changing_price_orders_correlation(token: Annotated[str, Depends(is_token_valid)], price_percentage: float = 0.1, n_random: int = 0):
    """
    Get the correlation between products and orders when the price changes.

    **Args:**
    - token (str)
    - price_percentage (float, optional): The percentage of price change. Defaults to 0.1. Values lower than 1 will lead to a decrease in price. Values higher than 1 will lead to an increase in price.
    - n_random (int, optional): The amount of random products to show. Defaults to 0.

    **Raises:**
    - HTTPException: If there is an error, it will raise a 404 error.

    **Returns:**
    - dict: The correlation between products and orders when the price changes.
    """
    try:
        data = await crud.get_changing_price_orders_correlation(price_percentage=price_percentage, n_random=n_random)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@router.get(f"/{VERSION}/{DIAGNOSTIC}/items-bought-correlation/", status_code=211)
async def get_items_bought_correlation(productId: str, amount_combined_products: int):
    """
    Get the items which are bought together.

    **Args:**
    - productId (str)
    - amount_combined_products (int)

    **Raises:**
    - HTTPException: If there is an error, it will raise a 404 error.

    **Returns:**
    - dict: The items which are bought together.
    """
    try:
        data = await crud.get_items_bought_correlation(productId, amount_combined_products)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    