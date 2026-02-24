from fastapi import HTTPException

from DataAnalysis.descriptive import CustomerSignup, EmployeeAmount, ProductsAmount, ProductsMostlyBought, RoutesAmount, OrdersAmount

from DataAnalysis.diagnostic import ProductOrdersCorrelation, ItemBoughtCorrelation

from DataAnalysis.predictive.PredictiveEngine.DataPredictor import DataPredictor

from api.auth import generate_jwt_token

from dotenv import load_dotenv
from os import getenv
import requests
from datetime import datetime, timedelta
load_dotenv()


####################### DESCRIPTIVE #######################

async def get_customers_signup(last_days: int = 0, month: bool = False, year: bool = False, showzeros: bool = False):
    return CustomerSignup.CustomerSignup().perform(last_days=last_days, month=month, year=year, showzeros=showzeros)

async def get_orders_amount(last_days: int = 0, month: bool = False, year: bool = False, showzeros: bool = False):
    return OrdersAmount.OrdersAmount().perform(last_days=last_days, month=month, year=year, showzeros=showzeros)

async def get_employees_amount():
    return EmployeeAmount.EmployeeAmount().perform()

async def get_products_amount(limit: int = 5, well_stocked: bool = False, out_of_stock: bool = False):
    return ProductsAmount.ProductsAmount().perform(limit=limit, well_stocked=well_stocked, out_of_stock=out_of_stock)

async def get_products_mostly_bought(last_days: int = 0, month: bool = False, year: bool = False, limit: int = 5):
    return ProductsMostlyBought.ProductsMostlyBought().perform(last_days=last_days, month=month, year=year, limit=limit)

async def get_routes_amount(limit: int = 5):
    return RoutesAmount.RoutesAmount().perform(limit=limit)


####################### DIAGNOSTIC #######################

async def get_products_orders_correlation():
    return ProductOrdersCorrelation.ProductOrdersCorrelation().perform()

async def get_changing_price_orders_correlation(price_percentage: float = 0.1, n_random: int = 0):
    return ProductOrdersCorrelation.ProductOrdersCorrelation().getChangingPriceOrdersCorrValue(price_percentage=price_percentage, n_random=n_random)

async def get_items_bought_correlation(productId: str, amount_combined_products: int):
    return ItemBoughtCorrelation.ItemBoughtCorrelation().perform(productId=productId, combination_product_amount=amount_combined_products)


####################### PREDICTIVE #######################

async def get_customers_growth(one_day: bool = False, seven_days: bool = False, month: bool = False, year: bool = False):
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
    
        return DataPredictor.DataPredictor("CustomerGrowth").predict("CustomerGrowth", option)
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

async def get_orders_growth(one_day: bool = False, seven_days: bool = False, month: bool = False, year: bool = False):
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
    
        return DataPredictor.DataPredictor("OrdersGrowth").predict("OrdersGrowth", option)
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
    try:
        response = requests.get(f"{getenv('APIURL')}/employees/?email={email}&password={password}&token={getenv('API_KEY')}")
        response = response.json()
        if len(response) == 0:
            raise HTTPException(status_code=401, detail="Wrong credentials")
    except ConnectionError as e:
        raise HTTPException(status_code=400, detail="Error connecting to the database")
    except KeyError as e:
        raise HTTPException(status_code=400, detail="Error connecting to the database")
    try:
        if response[0]['role'] == 'admin':
            return generate_jwt_token(email=email)
    except KeyError:
        response = requests.get(f"{getenv('APIURL')}/roles/name/ADMIN/?token={getenv('API_KEY')}")
        response = response.json()
        if len(response) == 0:
            raise HTTPException(status_code=401, detail="Not authorized")
        elif response['name'] == 'ADMIN':
            return generate_jwt_token(email=email)
