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


async def get_customers_signup(last_days: int = 0, month: bool = False, year: bool = False):
    return CustomerSignup.CustomerSignup().perform(last_days=last_days, month=month, year=year)

async def get_employees_amount():
    return EmployeeAmount.EmployeeAmount().perform()

async def get_products_amount():
    return ProductsAmount.ProductsAmount().perform()

async def get_products_mostly_bought(last_days: int = 0, month: bool = False, year: bool = False):
    return ProductsMostlyBought.ProductsMostlyBought().perform(last_days=last_days, month=month, year=year)

async def get_routes_amount(n_amount: int = 0):
    return RoutesAmount.RoutesAmount().perform(n_amount=n_amount)

async def get_products_orders_correlation():
    if ProductOrdersCorrelation.ProductOrdersCorrelation().perform() is None:
        pass
    return ProductOrdersCorrelation.ProductOrdersCorrelation().perform()

async def get_changing_price_orders_correlation(price_percentage: float = 0.1, n_random: int = 0):
    return ProductOrdersCorrelation.ProductOrdersCorrelation().getChangingPriceOrdersCorrValue(price_percentage=price_percentage, n_random=n_random)

async def get_items_bought_correlation(product_name: str, amount_combined_products: int):
    return ItemBoughtCorrelation.ItemBoughtCorrelation().perform(product_name=product_name, combination_product_amount=amount_combined_products)

async def get_customers_growth(last_days: int = None, month: bool = False, year: bool = False):
    if year is True:
        X_data = datetime.now().year
    elif month is True:
        X_data = [i for i in range(1, 13)]
    elif last_days is not None:
        X_data = [datetime.now() - timedelta(days=i) for i in range(last_days)]
        print(X_data)
    else: 
        raise HTTPException(status_code=400, detail="Invalid parameters")
   
    return DataPredictor.DataPredictor("CustomerGrowth").predict(X_data, "CustomerGrowth")


async def get_cumulative_customers_growth():
    raise HTTPException(status_code=501, detail="Not implemented")

async def get_orders_growth():
    raise HTTPException(status_code=501, detail="Not implemented")

async def get_cumulative_orders_growth():
    raise HTTPException(status_code=501, detail="Not implemented")

async def authenticate(email:str, password: str):
    response = requests.get(f"{getenv('APIURL')}/employees?email={email}&password={password}")
    response = response.json()
    if len(response) == 0:
        raise HTTPException(status_code=401, detail="Wrong credentials")
    if response[0]['role'] == 'admin':
        return generate_jwt_token(email=email)
    else:
        raise HTTPException(status_code=401, detail="Not authorized")
