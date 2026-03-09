from pydantic import BaseModel
from datetime import datetime

class CustomerSignup(BaseModel):
    signedUp: datetime

class OrderAmount(BaseModel):
    orderDate: datetime