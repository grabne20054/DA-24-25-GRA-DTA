from fastapi import APIRouter, Depends
from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta
from crud import crud
from api.constants import VERSION
from os import getenv, environ
import secrets

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
ALGORITHM = "HS256"
router = APIRouter()
if getenv("JWT_SECRET_KEY") is None:
    secret = secrets.token_urlsafe(32)
    environ["JWT_SECRET_KEY"] = secret
    print(getenv("JWT_SECRET_KEY")) # not working properly (every time when reloading changing)




@router.get(f"/{VERSION}/authenticate", status_code=200)
async def authenticate(firstname: str, lastname:str, password: str):
    return await crud.authenticate(firstname=firstname, lastname=lastname, password=password)

def generate_jwt_token(firstname: str, lastname: str):
    expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"firstname": firstname, "lastname": lastname, "exp": expires_delta}, getenv("JWT_SECRET_KEY"), algorithm=ALGORITHM)

def decode_jwt_token(token: str, verify_expiration:bool):
    decoded_token = jwt.decode(token, getenv("JWT_SECRET_KEY"), algorithms=[ALGORITHM], options={"verify_exp": verify_expiration})
    return decoded_token

def is_token_valid(token: str):
    try:
        decode_jwt_token(token, verify_expiration=True)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token
