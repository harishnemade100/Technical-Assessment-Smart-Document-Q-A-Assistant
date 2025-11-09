from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app.utils.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from backend.app.models.user_model import User
from backend.app.schema.auth_schema import RegisterRequest, TokenResponse
from backend.app.utils.jwt_handler import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(username=request.username, password_hash=hash_password(request.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully"}

@router.post("/login", response_model=TokenResponse)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}