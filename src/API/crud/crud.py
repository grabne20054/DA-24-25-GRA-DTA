from fastapi import HTTPException

from DataAnalysis.descriptive import CustomerSignup, EmployeeAmount, ProductsAmount, ProductsMostlyBought, RoutesAmount

from DataAnalysis.diagnostic import ProductOrdersCorrelation, ItemBoughtCorrelation

from DataAnalysis.predictive.PredictiveEngine.DataPredictor import DataPredictor

from api.auth import generate_jwt_token

from dotenv import load_dotenv
from os import getenv
import requests
from datetime import datetime, timedelta
load_dotenv()


####################### DESCRIPTIVE #######################

async def get_customers_signup(last_days: int = 0, month: bool = False, year: bool = False):
    return CustomerSignup.CustomerSignup().perform(last_days=last_days, month=month, year=year)

async def get_employees_amount():
    return EmployeeAmount.EmployeeAmount().perform()

async def get_products_amount(limit: int = 5):
    return ProductsAmount.ProductsAmount().perform(limit=limit)

async def get_products_mostly_bought(last_days: int = 0, month: bool = False, year: bool = False, limit: int = 5):
    return ProductsMostlyBought.ProductsMostlyBought().perform(last_days=last_days, month=month, year=year, limit=limit)

async def get_routes_amount(limit: int = 5):
    return RoutesAmount.RoutesAmount().perform(limit=limit)


####################### DIAGNOSTIC #######################

async def get_products_orders_correlation():
    if ProductOrdersCorrelation.ProductOrdersCorrelation().perform() is None:
        pass
    return ProductOrdersCorrelation.ProductOrdersCorrelation().perform()

async def get_changing_price_orders_correlation(price_percentage: float = 0.1, n_random: int = 0):
    return ProductOrdersCorrelation.ProductOrdersCorrelation().getChangingPriceOrdersCorrValue(price_percentage=price_percentage, n_random=n_random)

async def get_items_bought_correlation(productId: str, amount_combined_products: int):
    return ItemBoughtCorrelation.ItemBoughtCorrelation().perform(productId=productId, combination_product_amount=amount_combined_products)


####################### PREDICTIVE #######################

async def get_customers_growth(one_day: bool = False, seven_days: bool = False, month: bool = False, year: bool = False):
    option = None
    if one_day is True:
        X_data = {datetime.now() + timedelta(days=1): 0}
        option = "one_day"
    elif seven_days is True:
        X_data = {datetime.now() + timedelta(days=i): 0 for i in range(1,8)}
        option = "seven_days"
    elif month is True:
        X_data = {datetime.now() + timedelta(days=i): 0 for i in range(30)}
        option = "month"
    elif year is True:
        X_data = [datetime.now().year]
        option = "year"
    else: 
        raise HTTPException(status_code=400, detail="Invalid parameters")
   
    return DataPredictor.DataPredictor("CustomerGrowth").predict(X_data, "CustomerGrowth", option)


async def get_cumulative_customers_growth(one_day: bool = False, seven_days: bool = False, month: bool = False, year: bool = False):
    option = None
    if one_day is True:
        X_data = {datetime.now() + timedelta(days=1): 0}
        option = "one_day"
    elif seven_days is True:
        X_data = {datetime.now() + timedelta(days=i): 0 for i in range(1,8)}
        option = "seven_days"
    elif month is True:
        X_data = {datetime.now() + timedelta(days=i): 0 for i in range(30)}
        option = "month"
    elif year is True:
        X_data = [datetime.now().year]
        option = "year"
    else: 
        raise HTTPException(status_code=400, detail="Invalid parameters")
   
    return DataPredictor.DataPredictor("CumulativeCustomerGrowth").predict(X_data, "CumulativeCustomerGrowth", option)

async def get_orders_growth(one_day: bool = False, seven_days: bool = False, month: bool = False, year: bool = False):
    option = None
    if one_day is True:
        X_data = {datetime.now() + timedelta(days=1): 0}
        option = "one_day"
    elif seven_days is True:
        X_data = {datetime.now() + timedelta(days=i): 0 for i in range(1,8)}
        option = "seven_days"
    elif month is True:
        X_data = {datetime.now() + timedelta(days=i): 0 for i in range(30)}
        option = "month"
    elif year is True:
        X_data = [datetime.now().year]
        option = "year"
    else: 
        raise HTTPException(status_code=400, detail="Invalid parameters")
   
    return DataPredictor.DataPredictor("OrdersGrowth").predict(X_data, "OrdersGrowth", option)

async def get_cumulative_orders_growth(one_day: bool = False, seven_days: bool = False, month: bool = False, year: bool = False):
    option = None
    if one_day is True:
        X_data = {datetime.now() + timedelta(days=1): 0}
        option = "one_day"
    elif seven_days is True:
        X_data = {datetime.now() + timedelta(days=i): 0 for i in range(1,8)}
        option = "seven_days"
    elif month is True:
        X_data = {datetime.now() + timedelta(days=i): 0 for i in range(30)}
        option = "month"
    elif year is True:
        X_data = [datetime.now().year]
        option = "year"
    else: 
        raise HTTPException(status_code=400, detail="Invalid parameters")
   
    return DataPredictor.DataPredictor("CumulativeOrdersGrowth").predict(X_data, "CumulativeOrdersGrowth", option)

async def authenticate(email:str, password: str):
    response = requests.get(f"{getenv('APIURL')}/employees?email={email}&password={password}")
    response = response.json()
    if len(response) == 0:
        raise HTTPException(status_code=401, detail="Wrong credentials")
    if response[0]['role'] == 'admin':
        return generate_jwt_token(email=email)
    else:
        raise HTTPException(status_code=401, detail="Not authorized")
