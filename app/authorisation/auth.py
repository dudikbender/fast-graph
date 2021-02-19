# General packages and modules
from neo4j import GraphDatabase
import json
from datetime import datetime, timedelta
from typing import Optional

# FastAPI modules for authorisation
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Modules for encryption and security
from jose import JWTError, jwt
from passlib.context import CryptContext

# Import utilities functions and schemas
from app.utils.db import neo4j_driver
from app.utils.schema import Token, TokenData, User, UserInDB

# Packages and functions for loading environment variables
import os
from dotenv import load_dotenv
load_dotenv('.env')

# Settings for encryption
SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES')
ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)

# Set the API Router
router = APIRouter()

# Generate password hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def create_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)

# Search the database for user with specified username
def get_user(username: str):
    query = f'MATCH (a:User) WHERE a.username = \'{username}\' RETURN a'

    with neo4j_driver.session() as session:
        user_in_db = session.run(query)
        user_data = user_in_db.data()[0]['a']
        return UserInDB(**user_data)

# Authenticate user by checking they exist and that the password is correct
def authenticate_user(username, password):
    # First, retrieve the user by the email provided
    user = get_user(username)
    if not user:
        return False
    
    # If present, verify password against password hash in database
    password_hash = user.hashed_password
    username = user.username
    
    if not verify_password(password, password_hash):
        return False
    #print(user)
    return user

# Create access token, required for OAuth2 flow
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Decrypt the token and retrieve the username from payload
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Confirm that user is not disabled as a user
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Endpoint for token authorisation
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}