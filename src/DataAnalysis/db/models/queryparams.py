from pydantic import BaseModel
from datetime import datetime

class CustomerSignup(BaseModel):
    signedUp: datetime