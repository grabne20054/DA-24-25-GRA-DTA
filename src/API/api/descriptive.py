from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated


from crud import crud
from api.constants import VERSION, DESCRIPTIVE

from api.auth import is_token_valid


router = APIRouter()


@router.get(f"/{VERSION}/{DESCRIPTIVE}/customers-signup/", status_code=210)
async def get_customers_signup(token: Annotated[str, Depends(is_token_valid)], last_days: int = 0, month: bool = False, year: bool = False, showzeros: bool = False):
    """
    Get the amount of customers that signed up in the last days, month or year.

    **Args:**
    - token (str)
    - last_days (int, optional): The amount of days to look back. Defaults to 0.
    - month (bool, optional): If True, the data will be filtered by month. Defaults to False.
    - year (bool, optional): If True, the data will be filtered by year. Defaults to False.
    - showzeros (bool, optional): If True, the data will show the days/months/years with no customers. Defaults to False.

    **Raises:**
    - HTTPException: If no data is found, it will raise a 404 error.
    - HTTPException: If there is an error, it will raise a 400 error.

    **Returns:**
    - dict: The amount of customers that signed up in the last days, month or year.
    """
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
    """
    Get the amount of orders made in the last days, month or year.

    **Args:**
    - token (str)
    - last_days (int, optional): The amount of days to look back. Defaults to 0.
    - month (bool, optional): If True, the data will be filtered by month. Defaults to False.
    - year (bool, optional): If True, the data will be filtered by year. Defaults to False.
    - showzeros (bool, optional): If True, the data will show the days/months/years with no orders. Defaults to False.

    **Raises:**
    - HTTPException: If no data is found, it will raise a 404 error.
    - HTTPException: If there is an error, it will raise a 400 error.

    **Returns:**
    - dict: The amount of orders made in the last days, month or year.
    """
    try:
        data = await crud.get_orders_amount(last_days=last_days, month=month, year=year, showzeros=showzeros)
        return data
    except Exception as e:
        if e == "No data found":
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))

@router.get(f"/{VERSION}/{DESCRIPTIVE}/employees-amount/", status_code=210, deprecated=True)
async def get_employees_amount(token: Annotated[str, Depends(is_token_valid)]):
    """
    Get the amount of employees in the company.

    **Args:**
    - token (str)

    **Raises:**
    - HTTPException: If there is an error, it will raise a 404 error.

    **Returns:**
    - dict: The amount of employees in the company.
    """
    try:
        data = await crud.get_employees_amount()
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get(f"/{VERSION}/{DESCRIPTIVE}/products-amount/", status_code=210)
async def get_products_amount(token: Annotated[str, Depends(is_token_valid) ], limit: int = 5, well_stocked: bool = False, out_of_stock: bool = False):
    """
    Get the amount of products in the company. Default well and out of stock products are shown.

    **Args:**
    - token (str)
    - limit (int, optional): The amount of products to show. Defaults to 5.
    - well_stocked (bool, optional): If True, the data will show the well stocked products. Defaults to False.
    - out_of_stock (bool, optional): If True, the data will show the out of stock products. Defaults to False.

    **Raises:**
    - HTTPException: If there is an error, it will raise a 404 error.

    **Returns:**
    - dict: The amount of products in the company.

    """
    try:
        data = await crud.get_products_amount(limit=limit, well_stocked=well_stocked, out_of_stock=out_of_stock)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get(f"/{VERSION}/{DESCRIPTIVE}/products-mostly-bought/", status_code=210)
async def get_products_mostly_bought(token: Annotated[str, Depends(is_token_valid)], last_days: int = 0, month: bool = False, year: bool = False, limit: int = 5):
    """
    Get the products that are mostly bought in the last days, month or year.

    **Args:**
    - token (str)
    - last_days (int, optional): The amount of days to look back. Defaults to 0.
    - month (bool, optional): If True, the data will be filtered by month. Defaults to False.
    - year (bool, optional): If True, the data will be filtered by year. Defaults to False.

    **Raises:**
    - HTTPException: If no data is found, it will raise a 404 error.
    - HTTPException: If there is an error, it will raise a 400 error.

    **Returns:**
    - dict: The products that are mostly bought in the last days, month or year.

    """
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
    """
    Get the amount of routes in the company.

    **Args:**
    - token (str)
    - limit (int, optional): The amount of routes to show. Defaults to 5.

    **Raises:**
    - HTTPException: If there is an error, it will raise a 404 error.

    **Returns:**
    - dict: The amount of routes in the company.
    """

    try:
        data = await crud.get_routes_amount(limit=limit)
        return data
    except Exception as e:        
        raise HTTPException(status_code=404, detail=str(e))
    