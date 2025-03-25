import os
from datetime import datetime, timedelta
from typing import Optional, List
import uuid
import secrets

import cv2
import numpy as np
import torch
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
import httpx
from sqlalchemy import create_engine, Column, String, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from databases import Database
from RRDBNet_arch import RRDBNet

# ====================== DATABASE SETUP ======================
DATABASE_URL = "postgresql://esrgan_user:thisIsFardin77@localhost:5432/esrgan_db"  # Update with your credentials

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)

try:
    with engine.connect() as conn:
        print("Database connection successful!")
except Exception as e:
    print(f"Database connection failed: {e}")

# Databases setup (async)
database = Database(DATABASE_URL)

# ====================== DATABASE MODELS ======================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    google_id = Column(String, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# ====================== CONFIGURATION ======================
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Google OAuth Config
GOOGLE_CLIENT_ID = "your-google-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-google-client-secret"
GOOGLE_REDIRECT_URI = "http://localhost:8001/auth/google/callback"

# ====================== PYDANTIC MODELS ======================
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, min_length=2, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=50)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: int
    disabled: bool = False
    google_id: Optional[str] = None
    hashed_password: str  # Make sure to include this if you need it

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# ====================== AUTH UTILITIES ======================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_user(db: Session, email: str) -> Optional[UserInDB]:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return UserInDB.from_orm(user)
    return None

async def authenticate_user(db: Session, email: str, password: str) -> Optional[UserInDB]:
    user = await get_user(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user(db, email)
    if user is None:
        raise credentials_exception
    return user

# ====================== APP SETUP ======================
app = FastAPI(title="ESRGAN API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ESRGAN model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = RRDBNet(3, 3, 64, 23, gc=32)
model.load_state_dict(torch.load('models/RRDB_ESRGAN_x4.pth', map_location=device))
model.eval()
model = model.to(device)

# Database connection events
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ====================== ROUTES ======================
@app.post("/register", response_model=UserInDB)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = await get_user(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=Token)
async def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    authenticated_user = await authenticate_user(db, user.email, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/google")
async def google_login():
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20email%20profile&access_type=offline",
        status_code=302
    )

@app.get("/auth/google/callback")
async def google_callback(
    code: str,
    db: Session = Depends(get_db)
):
    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
        )
        tokens = token_response.json()
        
        # Get user info
        userinfo = await client.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        userinfo = userinfo.json()
        
        # Create or update user
        user = db.query(User).filter(User.email == userinfo["email"]).first()
        if not user:
            user = User(
                email=userinfo["email"],
                full_name=userinfo.get("name"),
                hashed_password="",  # No password for Google users
                google_id=userinfo["id"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Generate JWT
        access_token = create_access_token(
            data={"sub": userinfo["email"]},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return JSONResponse(
            content={"access_token": access_token, "token_type": "bearer"}
        )

@app.post("/enhance/")
async def enhance_image(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    temp_path = f"temp_{uuid.uuid4()}.jpg"
    result_path = f"enhanced_{uuid.uuid4()}.png"
    
    try:
        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Process image
        img = cv2.imread(temp_path, cv2.IMREAD_COLOR)
        img = img * 1.0 / 255
        img = torch.from_numpy(np.transpose(img[:, :, [2, 1, 0]], (2, 0, 1))).float()
        img_LR = img.unsqueeze(0).to(device)
        
        with torch.no_grad():
            output = model(img_LR).data.squeeze().float().cpu().clamp_(0, 1).numpy()
        
        output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
        output = (output * 255.0).round().astype(np.uint8)
        cv2.imwrite(result_path, output)
        
        return FileResponse(result_path, media_type="image/png")
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(result_path):
            os.remove(result_path)

@app.get("/me", response_model=UserInDB)
async def read_current_user(current_user: UserInDB = Depends(get_current_user)):
    return current_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)