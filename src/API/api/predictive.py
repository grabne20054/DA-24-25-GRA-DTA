from fastapi import APIRouter, Depends
from typing import Annotated

from api.auth import is_token_valid

from crud import crud
from api.constants import VERSION, PREDICTIVE

router = APIRouter()

@router.get(f"/{VERSION}/{PREDICTIVE}/customers-growth/", status_code=212)
async def get_customers_growth(token: Annotated[str, Depends(is_token_valid)]):
    """
    Get the customers growth prediction.

    **Args:**
    - token (str)

    **Raises:**
    - HTTPException: If there is an error, it will raise a 400 error.

    **Returns:**
    - dict: containing the customers growth in 4 different time frames (one day, seven days, fourteen days and thirty days).
    - Example response:
    {
        "predictions": {
            "2026-03-04": 2.0544991493225098,
            "2026-03-10": 1.9897998571395874,
            "2026-03-17": 1.8611266613006592,
            "2026-04-02": 1.8638324737548828
        }
    }
    """
    data = await crud.get_customers_growth()
    return data

@router.get(f"/{VERSION}/{PREDICTIVE}/customers-growth/month/", status_code=212)
async def get_customers_growth_month(token: Annotated[str, Depends(is_token_valid)]):
    """
    Get the customers growth prediction.

    **Args:**
    - token (str)

    **Raises:**
    - HTTPException: If there is an error, it will raise a 400 error.

    **Returns:**
    - dict: containing the customers growth in one month time frame.
    - Example response:
    {
        "predictions": {
            "2026-04": 2.0544991493225098,
        }
    }
    """
    data = await crud.get_customers_growth_month()
    return data

@router.get(f"/{VERSION}/{PREDICTIVE}/cumulative-customers-growth/", status_code=212, deprecated=True)
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
async def get_orders_growth(token: Annotated[str, Depends(is_token_valid)]):
    """
    Get the orders growth prediction.

    **Args:**
    - token (str)

    **Raises:**
    - HTTPException: If there is an error, it will raise a 400 error.

    **Returns:**
    - dict: containing the customers growth in 4 different time frames (one day, seven days, fourteen days and thirty days).
    - Example response:
    {
        "predictions": {
            "2026-03-04": 2.0544991493225098,
            "2026-03-10": 1.9897998571395874,
            "2026-03-17": 1.8611266613006592,
            "2026-04-02": 1.8638324737548828
        }
    }

    """
    
    data = await crud.get_orders_growth()
    return data

@router.get(f"/{VERSION}/{PREDICTIVE}/orders-growth/month/", status_code=212)
async def get_orders_growth_month(token: Annotated[str, Depends(is_token_valid)]):
    """
    Get the orders growth prediction.

    **Args:**
    - token (str)

    **Raises:**
    - HTTPException: If there is an error, it will raise a 400 error.

    **Returns:**
    - dict: containing the orders growth in one month time frame.
    - Example response:
    {
        "predictions": {
            "2026-04": 2.0544991493225098,
        }
    }
    """
    data = await crud.get_orders_growth_month()
    return data

@router.get(f"/{VERSION}/{PREDICTIVE}/cumulative-orders-growth/", status_code=212, deprecated=True)
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

@router.get(f"/{VERSION}/{PREDICTIVE}/route-classifier/", status_code=212)
async def get_route_classifier(token: Annotated[str, Depends(is_token_valid)], latitude: float, longitude: float):
    """
    Get the route classifier data.

    **Args:**
    - token (str)

    **Raises:**
    - HTTPException: If there is an error, it will raise a 400 error.

    **Returns:**
    - dict: The route classifier data.

    """
    data = await crud.get_routes_classifier(latitude, longitude)
    return data