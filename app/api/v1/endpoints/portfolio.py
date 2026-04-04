from fastapi import APIRouter, Depends, HTTPException, Body, BackgroundTasks
from app.db import get_database
from jose import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from datetime import datetime
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

from app.utils.file_cleanup import extract_upload_paths, delete_upload_file
import asyncio

@router.get("")
async def get_portfolio(db=Depends(get_database)):
    doc = await db["portfolio_content"].find_one({"key": "main"})
    if doc:
        return doc.get("data", {})
    return None

@router.post("")
async def save_portfolio(
    background_tasks: BackgroundTasks,
    data: dict = Body(...), 
    admin=Depends(get_admin_user), 
    db=Depends(get_database)
):
    """Saves portfolio data and triggers Smart Cleanup for redundancy."""
    # 1. Fetch old data before update
    old_doc = await db["portfolio_content"].find_one({"key": "main"})
    old_data = old_doc.get("data", {}) if old_doc else {}

    # 2. Update with new data
    result = await db["portfolio_content"].find_one_and_update(
        {"key": "main"},
        {"$set": {"data": data, "updated_at": datetime.utcnow()}},
        upsert=True,
        return_document=True
    )
    
    # 3. Smart File Cleanup (Background)
    old_paths = extract_upload_paths(old_data)
    new_paths = extract_upload_paths(data)
    
    # Identify deleted paths: exists in old but NOT in new
    deleted_paths = [p for p in old_paths if p not in new_paths]
    
    if deleted_paths:
        for p_type, p_value in deleted_paths:
            background_tasks.add_task(delete_upload_file, p_type, p_value)
            
    return {
        "success": True, 
        "message": "Portfolio saved and cleanup triggered!", 
        "cleaned": len(deleted_paths)
    }
