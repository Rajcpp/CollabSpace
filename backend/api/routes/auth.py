from fastapi import APIRouter, HTTPException, Depends
from backend.db.models import User
from backend.db.database import SessionLocal
from backend.core.security import hash_password, verify_password, create_access_token
from backend.api.deps import get_current_user, get_db

router = APIRouter()

@router.post("/register")
def register(username: str, email: str, password: str, db = Depends(get_db)):
    """Register a new user."""
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = hash_password(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@router.post("/login")
def login(username: str, password: str, db = Depends(get_db)):
    """Authenticate a user and return a JWT token."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"user_id": user.id})
    return {"access_token": token}

@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user's information."""
    return {"username": current_user.username, "id": current_user.id}