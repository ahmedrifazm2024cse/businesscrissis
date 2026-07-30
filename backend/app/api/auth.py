from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta
import os

from app.schemas.domain import UserLogin, Token, UserResponse, UserCreate
from app.models.domain import User
from app.auth.jwt import create_access_token, verify_password, get_password_hash

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = await User.find_one({"email": user_credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    existing_user = await User.find_one({"email": user_data.email})
    if existing_user:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role
    )
    await user.insert()
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        created_at=user.created_at
    )
