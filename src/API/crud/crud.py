from fastapi import HTTPException

from DataAnalysis.descriptive import CustomerSignup, EmployeeAmount, ProductsAmount, ProductsMostlyBought, RoutesAmount, OrdersAmount, InvoicesAmount

from DataAnalysis.diagnostic import ProductOrdersCorrelation, ItemBoughtCorrelation

from DataAnalysis.predictive.PredictiveEngine.DataPredictor import DataPredictor

from DataAnalysis.db.models.Auth import AuthRepository
from DataAnalysis.dependencies import get_db

from api.auth import generate_jwt_token

from dotenv import load_dotenv
from os import getenv
import requests
from datetime import datetime, timedelta
load_dotenv()


####################### DESCRIPTIVE #######################

async def get_customers_signup(last_days: int = 0, month: bool = False, year: bool = False, showzeros: bool = False, percentage: bool = False, cumulative: bool = False):
    if month and year:
        raise HTTPException(status_code=400, detail="Invalid parameters: month and year cannot be True at the same time")
    if last_days < 0:
        raise HTTPException(status_code=400, detail="Invalid parameters: last_days cannot be negative")
    if month and last_days > 0:
        raise HTTPException(status_code=400, detail="Invalid parameters: month cannot be True if last_days is greater than 0")
    if year and last_days > 0:
        raise HTTPException(status_code=400, detail="Invalid parameters: year cannot be True if last_days is greater than 0")
    return CustomerSignup.CustomerSignup().perform(last_days=last_days, month=month, year=year, showzeros=showzeros, percentage=percentage, cumulative=cumulative)

async def get_orders_amount(last_days: int = 0, month: bool = False, year: bool = False, showzeros: bool = False, percentage: bool = False, cumulative: bool = False):
    if month and year:
        raise HTTPException(status_code=400, detail="Invalid parameters: month and year cannot be True at the same time")
    if last_days < 0:
        raise HTTPException(status_code=400, detail="Invalid parameters: last_days cannot be negative")
    if month and last_days > 0:
        raise HTTPException(status_code=400, detail="Invalid parameters: month cannot be True if last_days is greater than 0")
    if year and last_days > 0:
        raise HTTPException(status_code=400, detail="Invalid parameters: year cannot be True if last_days is greater than 0")
    return OrdersAmount.OrdersAmount().perform(last_days=last_days, month=month, year=year, showzeros=showzeros, percentage=percentage, cumulative=cumulative)

async def get_employees_amount(limit: int = 5):
    if limit < 0:
        raise HTTPException(status_code=400, detail="Invalid parameters: limit cannot be negative")
    return EmployeeAmount.EmployeeAmount().perform(limit=limit)

async def get_products_amount(limit: int = 5, well_stocked: bool = False, out_of_stock: bool = False):
    return ProductsAmount.ProductsAmount().perform(limit=limit, well_stocked=well_stocked, out_of_stock=out_of_stock)

async def get_products_mostly_bought(last_days: int = 0, month: bool = False, year: bool = False, limit: int = 5):
    return ProductsMostlyBought.ProductsMostlyBought().perform(last_days=last_days, month=month, year=year, limit=limit)

async def get_routes_amount(limit: int = 5):
    return RoutesAmount.RoutesAmount().perform(limit=limit)

async def get_invoices_amount(last_days: int = 0, month: bool = False, year: bool = False, showzeros: bool = False, percentage: bool = False, cumulative: bool = False):
    if month and year:
        raise HTTPException(status_code=400, detail="Invalid parameters: month and year cannot be True at the same time")
    if last_days < 0:
        raise HTTPException(status_code=400, detail="Invalid parameters: last_days cannot be negative")
    if month and last_days > 0:
        raise HTTPException(status_code=400, detail="Invalid parameters: month cannot be True if last_days is greater than 0")
    if year and last_days > 0:
        raise HTTPException(status_code=400, detail="Invalid parameters: year cannot be True if last_days is greater than 0")
    return InvoicesAmount.InvoicesAmount().perform(last_days=last_days, month=month, year=year, showzeros=showzeros, percentage=percentage, cumulative=cumulative)

####################### DIAGNOSTIC #######################

async def get_products_orders_correlation():
    return ProductOrdersCorrelation.ProductOrdersCorrelation().perform()

async def get_changing_price_orders_correlation(price_percentage: float = 0.1, n_random: int = 0):
    return ProductOrdersCorrelation.ProductOrdersCorrelation().getChangingPriceOrdersCorrValue(price_percentage=price_percentage, n_random=n_random)

async def get_items_bought_correlation(productId: str, amount_combined_products: int):
    return ItemBoughtCorrelation.ItemBoughtCorrelation().perform(productId=productId, combination_product_amount=amount_combined_products)


####################### PREDICTIVE #######################

async def get_customers_growth():
    try:

        return DataPredictor.DataPredictor("CustomerGrowth").predict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def get_customers_growth_month():
    try:
        return DataPredictor.DataPredictor("CustomerGrowthMonthly", month=True).predict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def get_cumulative_customers_growth(one_day: bool = False, seven_days: bool = False, month: bool = False, year: bool = False):
    try:
        option = None
        if one_day is True:
            option = "one_day"
        elif seven_days is True:
            option = "seven_days"
        elif month is True:
            option = "month"
        elif year is True:
            option = "year"
        else: 
            raise HTTPException(status_code=400, detail="Invalid parameters")
    
        return DataPredictor.DataPredictor("CumulativeCustomerGrowth").predict("CumulativeCustomerGrowth", option)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def get_orders_growth():
    try:

        return DataPredictor.DataPredictor("OrdersGrowth").predict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def get_orders_growth_month():
    try:
        return DataPredictor.DataPredictor("OrdersGrowthMonthly", month=True).predict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def get_cumulative_orders_growth(one_day: bool = False, seven_days: bool = False, month: bool = False, year: bool = False):
    try:
        option = None
        if one_day is True:
            option = "one_day"
        elif seven_days is True:
            option = "seven_days"
        elif month is True:
            option = "month"
        elif year is True:
            option = "year"
        else: 
            raise HTTPException(status_code=400, detail="Invalid parameters")
    
        return DataPredictor.DataPredictor("CumulativeOrdersGrowth").predict("CumulativeOrdersGrowth", option)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def authenticate(email:str, password: str):
    res = AuthRepository(session=next(get_db()), email=email, password=password).get()
    if res is None:
        raise HTTPException(status_code=401, detail="Wrong credentials")
    if len(res) == 0:
        raise HTTPException(status_code=401, detail="Wrong credentials")
    elif str(res[1]).strip().lower() == "admin":
        return generate_jwt_token(email=email)
    else:
        raise HTTPException(status_code=401, detail="Not authorized")
