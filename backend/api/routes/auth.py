from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Depends
from backend.db.models import User
from backend.db.database import SessionLocal
from backend.core.security import hash_password, verify_password, create_access_token
from backend.api.deps import get_current_user, get_db
from backend.schemas.user import UserCreate, AuthResponse, UserResponse, UserBrief

router = APIRouter()

@router.post("/register")
def register(user_data: UserCreate, db = Depends(get_db)):
    """Register a new user."""
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = hash_password(user_data.password)
    new_user = User(username=user_data.username, email=user_data.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}


@router.post("/login", response_model=AuthResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"user_id": user.id})
    return AuthResponse(access_token=token, user=user)

@router.get("/me", response_model= UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user's information."""
    return current_user