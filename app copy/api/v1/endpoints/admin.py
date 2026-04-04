from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.db import get_database
from app.config import settings
from .portfolio import get_admin_user

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/login")
async def login(credentials: dict = Body(...), db=Depends(get_database)):
    email = credentials.get("email")
    password = credentials.get("password")
    
    admin = await db["admins"].find_one({"email": email})
    if not admin or not pwd_context.verify(password, admin.get("password")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = jwt.encode(
        {"id": str(admin["_id"]), "email": admin["email"], "role": admin.get("role")},
        settings.JWT_SECRET,
        algorithm="HS256"
    )
    
    return {
        "success": True, 
        "token": token, 
        "admin": {"email": admin["email"], "role": admin.get("role")}
    }

@router.post("/register")
async def register(data: dict = Body(...), db=Depends(get_database)):
    email = data.get("email")
    password = data.get("password")
    
    if await db["admins"].find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Admin already exists")
        
    hashed = pwd_context.hash(password)
    await db["admins"].insert_one({
        "email": email, 
        "password": hashed, 
        "role": "admin",
        "created_at": datetime.utcnow()
    })
    return {"success": True, "message": "Admin created successfully"}

@router.get("/list")
async def list_admins(admin=Depends(get_admin_user), db=Depends(get_database)):
    cursor = db["admins"].find({}, {"password": 0}).sort("created_at", -1)
    admins = []
    async for a in cursor:
        a["_id"] = str(a["_id"])
        admins.append(a)
    return {"success": True, "data": admins}
