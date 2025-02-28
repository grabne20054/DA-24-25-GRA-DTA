from fastapi import APIRouter, Depends
from typing import Annotated

from api.auth import is_token_valid

from crud import crud
from api.constants import VERSION, PREDICTIVE

router = APIRouter()

@router.get(f"/{VERSION}/{PREDICTIVE}/customers-growth/", status_code=212)
async def get_customers_growth(token: Annotated[str, Depends(is_token_valid)], one_day: bool = False ,seven_days: bool = False, month: bool = False, year: bool = False):
    """
    Get the customers growth prediction.

    **Args:**
    - token (str)
    - one_day (bool, optional): If True, the data will be predicted by one day. Defaults to False.
    - seven_days (bool, optional): If True, the data will be predicted by seven days. Defaults to False.
    - month (bool, optional): If True, the data will be predicted by month. Defaults to False.
    - year (bool, optional): If True, the data will be predicted by year. Defaults to False.

    **Raises:**
    - HTTPException: If there is an error, it will raise a 400 error.

    **Returns:**
    - dict: The customers growth.

    """
    data = await crud.get_customers_growth(one_day=one_day, seven_days=seven_days ,month=month, year=year)
    return data

@router.get(f"/{VERSION}/{PREDICTIVE}/cumulative-customers-growth/", status_code=212)
async def get_cumulative_customers_growth(token: Annotated[str, Depends(is_token_valid)], one_day: bool = False ,seven_days: bool = False, month: bool = False, year: bool = False):
    """
    Get the cumulative customers growth prediction.

    **Args:**
    - token (str)
    - one_day (bool, optional): If True, the data will be predicted by one day. Defaults to False.
    - seven_days (bool, optional): If True, the data will be predicted by seven days. Defaults to False.
    - month (bool, optional): If True, the data will be predicted by month. Defaults to False.
    - year (bool, optional): If True, the data will be predicted by year. Defaults to False.

    **Raises:**
    - HTTPException: If there is an error, it will raise a 400 error.

    **Returns:**
    - dict: The cumulative customers growth.

    """

    data = await crud.get_cumulative_customers_growth(one_day=one_day, seven_days=seven_days ,month=month, year=year)
    return data

@router.get(f"/{VERSION}/{PREDICTIVE}/orders-growth/", status_code=212)
async def get_orders_growth(token: Annotated[str, Depends(is_token_valid)], one_day: bool = False ,seven_days: bool = False, month: bool = False, year: bool = False):
    """
    Get the orders growth prediction.

    **Args:**
    - token (str)
    - one_day (bool, optional): If True, the data will be predicted by one day. Defaults to False.
    - seven_days (bool, optional): If True, the data will be predicted by seven days. Defaults to False.
    - month (bool, optional): If True, the data will be predicted by month. Defaults to False.
    - year (bool, optional): If True, the data will be predicted by year. Defaults to False.

    **Raises:**
    - HTTPException: If there is an error, it will raise a 400 error.

    **Returns:**
    - dict: The orders growth.

    """
    
    data = await crud.get_orders_growth(one_day=one_day, seven_days=seven_days ,month=month, year=year)
    return data

@router.get(f"/{VERSION}/{PREDICTIVE}/cumulative-orders-growth/", status_code=212)
async def get_cumulative_orders_growth(token: Annotated[str, Depends(is_token_valid)], one_day: bool = False ,seven_days: bool = False, month: bool = False, year: bool = False):
    """
    Get the cumulative orders growth prediction.

    **Args:**
    - token (str)
    - one_day (bool, optional): If True, the data will be predicted by one day. Defaults to False.
    - seven_days (bool, optional): If True, the data will be predicted by seven days. Defaults to False.
    - month (bool, optional): If True, the data will be predicted by month. Defaults to False.
    - year (bool, optional): If True, the data will be predicted by year. Defaults to False.

    **Raises:**
    - HTTPException: If there is an error, it will raise a 400 error.

    **Returns:**
    - dict: The cumulative orders growth.

    """
    
    data = await crud.get_cumulative_orders_growth(one_day=one_day, seven_days=seven_days ,month=month, year=year)
    return data