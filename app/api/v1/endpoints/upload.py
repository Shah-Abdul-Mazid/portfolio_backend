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
    Upload file (PDF or Image) to Cloudinary using stream.
    Supports:
    - PDF
    - JPG / PNG / WEBP
    """

    try:
        # 🔥 Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file.file,
            folder="portfolio_uploads",
            resource_type="auto"   # ✅ auto-detect (PDF or image)
        )

        # ✅ Extract important fields
        secure_url = result.get("secure_url")
        public_id = result.get("public_id")
        resource_type = result.get("resource_type")
        file_format = result.get("format")

        # 🔍 Logging (optional but useful)
        logger.info(f"Uploaded file: {public_id} ({resource_type}.{file_format})")

        # ✅ Final response (frontend-friendly)
        return {
            "success": True,
            "file": {
                "url": secure_url,              # ✅ ALWAYS USE THIS IN FRONTEND
                "public_id": public_id,
                "resource_type": resource_type,
                "format": file_format
            }
        }

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")

        return {
            "success": False,
            "message": f"Cloudinary upload failed: {str(e)}"
        }