from fastapi import APIRouter

from crud import crud
from api.constants import VERSION, DESCRIPTIVE


router = APIRouter()

@router.get(f"/{VERSION}/{DESCRIPTIVE}/customers-signup/", status_code=210)
async def get_customers_signup(last_days: int = None, month: bool = False, year: bool = False):
    data = await crud.get_customers_signup(last_days=last_days, month=month, year=year)
    return data
    

@router.get(f"/{VERSION}/{DESCRIPTIVE}/employees-amount/", status_code=210)
async def get_employees_amount():
    data = await crud.get_employees_amount()
    return data

@router.get(f"/{VERSION}/{DESCRIPTIVE}/products-amount/", status_code=210)
async def get_products_amount():
    data = await crud.get_products_amount()
    return data

@router.get(f"/{VERSION}/{DESCRIPTIVE}/products-mostly-bought/", status_code=210)
async def get_products_mostly_bought():
    data = await crud.get_products_mostly_bought()
    return data

@router.get(f"/{VERSION}/{DESCRIPTIVE}/routes-amount/", status_code=210)
async def get_routes_amount():
    data = await crud.get_routes_amount()
    return data