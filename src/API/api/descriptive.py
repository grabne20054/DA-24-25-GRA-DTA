from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated


from crud import crud
from api.constants import VERSION, DESCRIPTIVE

from api.auth import is_token_valid


router = APIRouter()

@router.get(f"/{VERSION}/{DESCRIPTIVE}/customers-signup/", status_code=210)
async def get_customers_signup(token: Annotated[str, Depends(is_token_valid)], last_days: int = 0, month: bool = False, year: bool = False, showzeros: bool = False):
    try:
        data = await crud.get_customers_signup(last_days=last_days, month=month, year=year, showzeros=showzeros)
        return data
    except Exception as e:
        if e == "No data found":
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
        
@router.get(f"/{VERSION}/{DESCRIPTIVE}/orders-amount/", status_code=210)
async def get_orders_amount(token: Annotated[str, Depends(is_token_valid)], last_days: int = 0, month: bool = False, year: bool = False, showzeros: bool = False):
    try:
        data = await crud.get_orders_amount(last_days=last_days, month=month, year=year, showzeros=showzeros)
        return data
    except Exception as e:
        if e == "No data found":
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))

@router.get(f"/{VERSION}/{DESCRIPTIVE}/employees-amount/", status_code=210)
async def get_employees_amount(token: Annotated[str, Depends(is_token_valid)]):
    try:
        data = await crud.get_employees_amount()
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get(f"/{VERSION}/{DESCRIPTIVE}/products-amount/", status_code=210)
async def get_products_amount(token: Annotated[str, Depends(is_token_valid) ], limit: int = 5):
    try:
        data = await crud.get_products_amount(limit=limit)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
# TODO: orderDate
@router.get(f"/{VERSION}/{DESCRIPTIVE}/products-mostly-bought/", status_code=210)
async def get_products_mostly_bought(token: Annotated[str, Depends(is_token_valid)], last_days: int = None, month: bool = False, year: bool = False, limit: int = 5):
    try:
        data = await crud.get_products_mostly_bought(last_days=last_days, month=month, year=year, limit=limit)
        return data
    except Exception as e:
        if e == "No data found":
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))

@router.get(f"/{VERSION}/{DESCRIPTIVE}/routes-amount/", status_code=210)
async def get_routes_amount(token: Annotated[str, Depends(is_token_valid)], limit: int = 5):
    try:
        data = await crud.get_routes_amount(limit=limit)
        return data
    except Exception as e:        
        raise HTTPException(status_code=404, detail=str(e))
    