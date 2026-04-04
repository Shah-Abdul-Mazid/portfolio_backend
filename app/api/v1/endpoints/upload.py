from fastapi import APIRouter, File, UploadFile
import cloudinary
import cloudinary.uploader
import logging

router = APIRouter()
logger = logging.getLogger("portfolio-upload")

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Decide resource type based on extension if auto is causing issues
        ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ""
        res_type = "auto"
        
        # If it's a PDF, force resource_type to 'raw' to avoid image-bucket 401/404 errors in some Cloudinary accounts
        if ext == "pdf":
            res_type = "raw"
            logger.info(f"Forcing 'raw' resource_type for PDF upload: {file.filename}")

        result = cloudinary.uploader.upload(
            file.file,
            folder="portfolio_uploads",
            resource_type=res_type,
            use_filename=True,
            unique_filename=True
        )

        logger.info(f"Successfully uploaded {file.filename} as {result.get('resource_type')}")

        return {
            "success": True,
            "url": result.get("secure_url"),   # ✅ Added for Frontend compatibility
            "filename": result.get("original_filename"), # Added
            "file": {
                "url": result.get("secure_url"),
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
