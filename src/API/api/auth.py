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

@router.get(f"/{VERSION}/authenticate", status_code=200)
async def authenticate(email:str, password: str):
    """
    Authenticate the user.
    
    **Args:**
    - email (str): The email of the user.
    - password (str): The password of the user.
    
    **Raises:**
    - HTTPException: If the user is not authenticated, it will raise a 401 error.
    
    **Returns:**
    - str: The token of the user.
    """
    return await crud.authenticate(email, password=password)

@router.get(f"/{VERSION}/authenticate/isTokenValid", status_code=200)
async def authenticate_token(token: str):
    """
    Check if the token is valid.

    **Args:**
    - token (str): The token of the user.

    **Raises:**
    - HTTPException: If the token is invalid, it will raise a 401 error.

    **Returns:**
    - str: The token of the user.
    """
    
    return is_token_valid(token)

def generate_jwt_token(email:str):
    if getenv("JWT_SECRET_KEY") is None:
        secret = secrets.token_urlsafe(32)
        environ["JWT_SECRET_KEY"] = secret
    expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"email":email, "exp": expires_delta}, getenv("JWT_SECRET_KEY"), algorithm=ALGORITHM)

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
