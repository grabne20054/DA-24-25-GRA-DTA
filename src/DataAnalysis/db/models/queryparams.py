from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4

class CustomerSignup(BaseModel):
    signedUp: datetime

class OrderAmount(BaseModel):
    orderDate: datetime

class EmployeeAmount(BaseModel):
    name: str
    employee_count: int

class ProductsAmount(BaseModel):
    name: str
    stock: int

class ProductsMostlyBought(BaseModel):
    productId: uuid4
    name: str

class OrdersProducts(BaseModel):
    orderDate: datetime
    productId: str
    productAmount: int

class RoutesAmount(BaseModel):
    name: str
    order_count: int

# ItemBought Correlation

class OrdersParam(BaseModel):
    orderId: uuid4

class ProductsParam(BaseModel):
    productId: uuid4

class OrdersProductsParam(BaseModel):
    orderId: uuid4
    productId: uuid4


# AUTH

class AuthParams(BaseModel):
    email: str
    password: str