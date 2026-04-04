from fastapi import APIRouter, Depends, HTTPException, Body, File, UploadFile
from app.db import get_database
from app.api.v1.endpoints.portfolio import get_admin_user
import cloudinary
import cloudinary.uploader
import logging

router = APIRouter()
logger = logging.getLogger("portfolio-upload")

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """
    Cloudinary direct-buffer upload.
    Replicates the logic from Node's uploadRoutes.js using FastAPI streams.
    """
    try:
        # Uploads directly from the incoming stream to Cloudinary
        result = cloudinary.uploader.upload(
            file.file, 
            folder="portfolio_uploads",
            resource_type="auto"
        )
        return {
            "success": True, 
            "url": result.get("secure_url"),
            "public_id": result.get("public_id")
        }
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        # Returning 400 with the exact error so the frontend alert(result.message) displays it
        return {
            "success": False,
            "message": f"Cloudinary upload failed: {str(e)}"
        }
