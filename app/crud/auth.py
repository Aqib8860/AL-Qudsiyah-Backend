import os
import jwt
import requests
from fastapi import HTTPException, Depends
from datetime import timedelta, datetime
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from dotenv import load_dotenv


load_dotenv()

# Initialize the password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get('AUTH_SECRET_KEY')
ALGORITHM = os.environ.get('AUTH_ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'))

# Initialize OAuth2PasswordBearer for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT token utility functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")    


# Get the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = verify_access_token(token)
    return payload



def verify_google_token(access_token: str):
    """Verify Google Access token and extract user info"""
    google_url = f"https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={access_token}"
    response = requests.get(google_url)
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid Google token")
    
    user_data = response.json()

    # Get Profile from google
    try:
        profile_url = "https://people.googleapis.com/v1/people/me?personFields=names"
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = requests.get(profile_url, headers=headers)

        if profile_response.status_code == 200:
            profile = profile_response.json()
            user_data["name"] = profile["names"][0]["displayName"]
    except Exception as e:
        pass

    
    return user_data 

