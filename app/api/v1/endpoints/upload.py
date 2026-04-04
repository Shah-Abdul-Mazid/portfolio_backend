from fastapi import APIRouter, File, UploadFile
import cloudinary
import cloudinary.uploader
import logging

router = APIRouter()
logger = logging.getLogger("portfolio-upload")

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            folder="portfolio_uploads",
            resource_type="auto"
        )

        return {
            "success": True,
            "file": {
                "url": result.get("secure_url"),   # ✅ USE THIS ALWAYS
                "public_id": result.get("public_id"),
                "format": result.get("format"),
                "resource_type": result.get("resource_type")
            }
        }

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return {
            "success": False,
            "message": f"Cloudinary upload failed: {str(e)}"
        }