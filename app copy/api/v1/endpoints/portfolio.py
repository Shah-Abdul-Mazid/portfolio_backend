from fastapi import APIRouter, Depends, HTTPException, Body
from app.db import get_database
from datetime import datetime
from jose import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
import os

router = APIRouter()
security = HTTPBearer()

def get_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifies the JWT token from the Authorization header."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/")
async def get_portfolio(db=Depends(get_database)):
    doc = await db["portfolio_content"].find_one({})
    if doc:
        return doc.get("data", {})
    return None

@router.post("/")
async def save_portfolio(data: dict = Body(...), admin=Depends(get_admin_user), db=Depends(get_database)):
    """Saves updated portfolio data to MongoDB cluster."""
    result = await db["portfolio_content"].find_one_and_update(
        {},
        {"$set": {"data": data, "lastUpdated": datetime.utcnow()}},
        upsert=True,
        return_document=True
    )
    if result:
        # Future: Trigger file cleanup utilities
        return {"success": True, "message": "Updated successfully"}
    raise HTTPException(status_code=500, detail="Database update failed")
