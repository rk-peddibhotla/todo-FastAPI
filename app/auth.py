from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.models import UserSignup, UserLogin, UserInDB
from app.database import user_collection
from bson import ObjectId
import os
from dotenv import load_dotenv


from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm

load_dotenv()

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/signup")
async def signup(user: UserSignup):
    existing = await user_collection.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = get_password_hash(user.password)
    user_dict = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password
    }
    await user_collection.insert_one(user_dict)
    return {"msg": "User created successfully"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    found = await user_collection.find_one({"username": form_data.username})
    if not found or not verify_password(form_data.password, found["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {"sub": form_data.username}
    token = create_access_token(token_data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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
    except JWTError:
        raise credentials_exception
    
    user = await user_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user
