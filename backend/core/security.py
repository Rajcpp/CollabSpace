import bcrypt
from jose import jwt, JWTError
from backend.core.config import settings
from fastapi import HTTPException
from datetime import datetime, timedelta

secret_key = settings.JWT_SECRET_KEY
algorithm = settings.JWT_ALGORITHM
access_token_expire_mins = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

def hash_password(password):
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain, hashed) -> bool:
    """Verify a password against a hashed version."""
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=access_token_expire_mins)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)

def verify_token(token: str):
    """Verify a JWT token and return the decoded data."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
