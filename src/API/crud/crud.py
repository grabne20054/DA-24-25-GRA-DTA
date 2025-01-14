from fastapi import HTTPException

from DataAnalysis.descriptive import CustomerSignup, EmployeeAmount, ProductsAmount, ProductsMostlyBought, RoutesAmount


async def get_customers_signup(last_days: int = None, month: bool = False, year: bool = False):
    if last_days is None:
        last_days = 0
    return CustomerSignup.CustomerSignup().perform(last_days=last_days, month=month, year=year)

async def get_employees_amount():
    return EmployeeAmount.EmployeeAmount().perform()

async def get_products_amount():
    return ProductsAmount.ProductsAmount().perform()

async def get_products_mostly_bought(last_days: int = None, month: bool = False, year: bool = False):
    if last_days is None:
        last_days = 0
    return ProductsMostlyBought.ProductsMostlyBought().perform(last_days=last_days, month=month, year=year)

async def get_routes_amount():
    return RoutesAmount.RoutesAmount().perform()

async def get_products_orders_correlation():
    raise HTTPException(status_code=501, detail="Not implemented")

async def get_items_bought_correlation():
    raise HTTPException(status_code=501, detail="Not implemented")

async def get_customers_growth():
    raise HTTPException(status_code=501, detail="Not implemented")

async def get_cumulative_customers_growth():
    raise HTTPException(status_code=501, detail="Not implemented")

async def get_orders_growth():
    raise HTTPException(status_code=501, detail="Not implemented")

async def get_cumulative_orders_growth():
    raise HTTPException(status_code=501, detail="Not implemented")