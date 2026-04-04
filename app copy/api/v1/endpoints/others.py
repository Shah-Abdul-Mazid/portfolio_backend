from fastapi import APIRouter, Depends, HTTPException, Body, File, UploadFile
from app.db import get_database
from app.api.v1.endpoints.portfolio import get_admin_user
from datetime import datetime
import cloudinary
import cloudinary.uploader
import os

analytics_router = APIRouter()
messages_router = APIRouter()
upload_router = APIRouter()

# ── ANALYTICS ─────────────────────────────────────────────
@analytics_router.get("/")
async def get_analytics(db=Depends(get_database)):
    doc = await db["visitors"].find_one({"_id": "total_visitors"})
    if not doc:
        # Create it if it doesn't exist
        await db["visitors"].insert_one({"_id": "total_visitors", "count": 0})
        return {"count": 0}
    return {"count": doc.get("count", 0)}

@analytics_router.post("/")
async def increment_analytics(db=Depends(get_database)):
    result = await db["visitors"].find_one_and_update(
        {"_id": "total_visitors"},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=True
    )
    return {"success": True, "count": result.get("count", 0)}

# ── MESSAGES ──────────────────────────────────────────────
@messages_router.get("/")
async def get_messages(auth=Depends(get_admin_user), db=Depends(get_database)):
    cursor = db["messages"].find({}).sort("created_at", -1).limit(50)
    messages = []
    async for msg in cursor:
        msg["_id"] = str(msg["_id"])
        messages.append(msg)
    return messages

@messages_router.post("/")
async def create_message(msg: dict = Body(...), db=Depends(get_database)):
    msg["created_at"] = datetime.utcnow().isoformat()
    await db["messages"].insert_one(msg)
    return {"success": True, "message": "Your message was sent!"}

# ── UPLOADS ──────────────────────────────────────────────
@upload_router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """Cloudinary direct-buffer upload."""
    try:
        result = cloudinary.uploader.upload(
            file.file, 
            folder="portfolio_uploads",
            resource_type="auto"
        )
        return {"success": True, "url": result.get("secure_url")}
    except Exception:
        raise HTTPException(status_code=500, detail="Upload failed")
