import uvicorn
from fastapi import FastAPI, Body, Depends, Header, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

import jwt
import bcrypt
from app.model import userSchema, userLoginSchema, User
from app.auth.jwt_handler import signJWT, JWT_SECRET, JWT_ALGORITHM
from app.email_service import send_welcome_email
from database import SessionLocal, engine, Base
import requests, base64, io, os, json, subprocess, sys
from PIL import Image
import os
from ai_model import get_gemini_treatment


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    if len(password.encode('utf-8')) > 72:
        import hashlib
        password = hashlib.sha256(password.encode()).hexdigest()
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    if len(plain_password.encode('utf-8')) > 72:
        import hashlib
        plain_password = hashlib.sha256(plain_password.encode()).hexdigest()
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

app = FastAPI()


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")



origins = [
    "http://localhost:3000", 
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://frontend-three-mu-82.vercel.app",
]


if os.getenv("ENVIRONMENT") == "production":
    allowed_origins = origins
else:
    allowed_origins = origins 

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex="https://.*\.vercel\.app|https://.*\.railway\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        print(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        print(f"Request failed: {str(e)}")
        raise

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


@app.post("/detection/upload")
async def analyze_crop_image(image: UploadFile = File(...)):
    """Analyze uploaded crop image using external API"""
    print(f"\n=== UPLOAD ENDPOINT CALLED ===")
    print(f"Received upload request for file: {image.filename}")
    print(f"Content type: {image.content_type}")
    try:
        # Validate file type
        if not image.content_type.startswith("image/"):
            print("ERROR: File is not an image")
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read image bytes
        image_bytes = await image.read()
        print(f"Image bytes read: {len(image_bytes)} bytes")
        
        # External API URL
        api_url = "http://leaf-diseases-detect.vercel.app"
        
        # Prepare file for upload
        files = {
            "file": (image.filename, image_bytes, image.content_type)
        }
        
        print(f"Calling external API: {api_url}/disease-detection-file")
        # Call external API
        response = requests.post(f"{api_url}/disease-detection-file", files=files)
        
        print(f"External API response status: {response.status_code}")
        if response.status_code != 200:
             print(f"ERROR: External API returned {response.status_code}: {response.text}")
             raise HTTPException(status_code=response.status_code, detail=f"External API error: {response.text}")
        
        detection_result = response.json()
        print(f"External API Result: {detection_result}")
        
        # Finetune with Gemini
        print("Finetuning result with Gemini...")
        final_result = await get_gemini_treatment(detection_result)
        print("Gemini processing complete")
        
        return final_result

    except HTTPException as e:
        print(f"HTTP Exception: {e.detail}")
        raise
    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
