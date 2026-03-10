from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4

class CustomerSignup(BaseModel):
    signedUp: datetime

class OrderAmount(BaseModel):
    orderDate: datetime

class EmployeeAmount(BaseModel):
    roleId: uuid4

class Roles(BaseModel):
    id: uuid4
    name: str

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
