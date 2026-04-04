from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from app.db import get_database
from app.api.v1.endpoints.portfolio import get_admin_user
import cloudinary
import cloudinary.uploader
import logging
from bson import ObjectId

router = APIRouter()
logger = logging.getLogger("portfolio-upload")

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Query(..., description="User ID to update"),
    type: str = Query(..., description="Type of upload: 'experience' or 'work'"),
    index: int = Query(..., description="Index of experience/work item to update"),
    db=Depends(get_database),
    current_user=Depends(get_admin_user)
):
    """
    Upload a file to Cloudinary and update user's experience/work array with the file URL.
    """

    try:
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file.file,
            folder="portfolio_uploads",
            resource_type="auto"
        )

        secure_url = result.get("secure_url")
        public_id = result.get("public_id")
        resource_type = result.get("resource_type")
        file_format = result.get("format")

        logger.info(f"Uploaded file: {public_id} ({resource_type}.{file_format})")

        # Determine field to update
        if type not in ["experience", "work"]:
            raise HTTPException(status_code=400, detail="type must be 'experience' or 'work'")

        # Build update query
        field_path = f"{type}.{index}.certificateUrl" if type == "experience" else f"{type}.{index}.workUrl"

        update_result = await db["users"].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {field_path: secure_url}}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User or index not found")

        return {
            "success": True,
            "file": {
                "url": secure_url,
                "public_id": public_id,
                "resource_type": resource_type,
                "format": file_format,
                "updated_field": field_path
            }
        }

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")