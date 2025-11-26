
import uvicorn
from fastapi import FastAPI, Body, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import jwt
import bcrypt
from app.model import userSchema, userLoginSchema, User
from app.auth.jwt_handler import signJWT, JWT_SECRET, JWT_ALGORITHM
from app.email_service import send_welcome_email
from database import SessionLocal, engine, Base
import os

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Handle long passwords by hashing with sha256 first
    if len(password.encode('utf-8')) > 72:
        import hashlib
        password = hashlib.sha256(password.encode()).hexdigest()
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Handle long passwords the same way
    if len(plain_password.encode('utf-8')) > 72:
        import hashlib
        plain_password = hashlib.sha256(plain_password.encode()).hexdigest()
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def home():
    return "App is running"

@app.post("/auth/signup", tags=["user"])
def user_signup(user: userSchema = Body(default=None), db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        return {"error": "Email already registered"}
    hashed_pw = hash_password(user.password)
    new_user = User(fullname=user.fullname, email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send welcome email
    send_welcome_email(new_user.email, new_user.fullname)
    
    return signJWT(new_user.email)

@app.post("/auth/login", tags=["user"])
def user_login(data: userLoginSchema = Body(default=None), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user and verify_password(data.password, user.password):
        return signJWT(user.email)
    return {"error": "Invalid login details!"}

@app.get("/auth/user", tags=["user"])
def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        return {"error": "No token provided"}
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_email = payload.get("userID")
        
        if not user_email:
            return {"error": "Invalid token"}
        
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            return {"error": "User not found"}
        
        return {
            "id": user.id,
            "email": user.email,
            "fullname": user.fullname
        }
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}

@app.post("/auth/logout", tags=["user"])
def user_logout():
    """Logout endpoint - token invalidation is handled on the frontend by clearing the token"""
    return {"message": "Successfully logged out"}