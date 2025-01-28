from fastapi import APIRouter, Depends
from typing import Annotated


from crud import crud
from api.constants import VERSION, DESCRIPTIVE

from api.auth import is_token_valid


router = APIRouter()

@router.get(f"/{VERSION}/{DESCRIPTIVE}/customers-signup/", status_code=210)
async def get_customers_signup(token: Annotated[str, Depends(is_token_valid)], last_days: int = None, month: bool = False, year: bool = False):
    data = await crud.get_customers_signup(last_days=last_days, month=month, year=year)
    return data
    

@router.get(f"/{VERSION}/{DESCRIPTIVE}/employees-amount/", status_code=210)
async def get_employees_amount(token: Annotated[str, Depends(is_token_valid)]):
    data = await crud.get_employees_amount()
    return data

@router.get(f"/{VERSION}/{DESCRIPTIVE}/products-amount/", status_code=210)
async def get_products_amount(token: Annotated[str, Depends(is_token_valid)]):
    data = await crud.get_products_amount()
    return data

@router.get(f"/{VERSION}/{DESCRIPTIVE}/products-mostly-bought/", status_code=210)
async def get_products_mostly_bought(token: Annotated[str, Depends(is_token_valid)]):
    data = await crud.get_products_mostly_bought()
    return data

@router.get(f"/{VERSION}/{DESCRIPTIVE}/routes-amount/", status_code=210)
async def get_routes_amount(token: Annotated[str, Depends(is_token_valid)]):
    data = await crud.get_routes_amount()
    return data