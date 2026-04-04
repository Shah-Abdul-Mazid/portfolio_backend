# from fastapi import APIRouter, File, UploadFile
# import cloudinary
# import cloudinary.uploader
# import logging

# router = APIRouter()
# logger = logging.getLogger("portfolio-upload")

# @router.post("")
# async def upload_file(file: UploadFile = File(...)):
#     try:
#         result = cloudinary.uploader.upload(
#             file.file,
#             folder="portfolio_uploads",
#             resource_type="auto"
#         )

#         return {
#             "success": True,
#             "file": {
#                 "url": result.get("secure_url"),   # ✅ USE THIS ALWAYS
#                 "public_id": result.get("public_id"),
#                 "format": result.get("format"),
#                 "resource_type": result.get("resource_type")
#             }
#         }

#     except Exception as e:
#         logger.error(f"Upload error: {str(e)}")
#         return {
#             "success": False,
#             "message": f"Cloudinary upload failed: {str(e)}"
#         }


from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from app.db import get_database
from app.api.v1.endpoints.portfolio import get_admin_user
import cloudinary
import cloudinary.uploader
import logging
import os
from bson import ObjectId
from bson.errors import InvalidId

router = APIRouter()
logger = logging.getLogger("portfolio-upload")

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

ALLOWED_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/avif",
}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Query(..., description="MongoDB user id"),
    upload_type: str = Query(..., description="experience or work"),
    index: int = Query(..., description="Array index to update"),
    doc_kind: str = Query(..., description="certificate / appointment / experience"),
    db=Depends(get_database),
    current_user=Depends(get_admin_user),
):
    """
    Upload file to Cloudinary and update exact portfolio field.

    upload_type=experience:
      doc_kind=certificate -> experience.{index}.certificateUrl

    upload_type=work:
      doc_kind=appointment -> work.{index}.appointmentLetterUrl
      doc_kind=experience  -> work.{index}.experienceLetterUrl
    """
    try:
        if upload_type not in ["experience", "work"]:
            raise HTTPException(
                status_code=400,
                detail="upload_type must be 'experience' or 'work'"
            )

        if index < 0:
            raise HTTPException(status_code=400, detail="index must be >= 0")

        try:
            object_user_id = ObjectId(user_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid user_id")

        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}"
            )

        filename = (file.filename or "").lower()
        is_pdf = filename.endswith(".pdf")

        if upload_type == "experience":
            if doc_kind != "certificate":
                raise HTTPException(
                    status_code=400,
                    detail="For upload_type='experience', doc_kind must be 'certificate'"
                )
            field_path = f"experience.{index}.certificateUrl"

        else:  # work
            if doc_kind == "appointment":
                field_path = f"work.{index}.appointmentLetterUrl"
            elif doc_kind == "experience":
                field_path = f"work.{index}.experienceLetterUrl"
            else:
                raise HTTPException(
                    status_code=400,
                    detail="For upload_type='work', doc_kind must be 'appointment' or 'experience'"
                )

        result = cloudinary.uploader.upload(
            file.file,
            folder="portfolio_uploads",
            resource_type="raw" if is_pdf else "image",
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )

        secure_url = result.get("secure_url")
        public_id = result.get("public_id")
        resource_type = result.get("resource_type")
        file_format = result.get("format")

        if not secure_url:
            raise HTTPException(status_code=500, detail="Cloudinary did not return secure_url")

        existing_user = await db["users"].find_one({"_id": object_user_id}, {"_id": 1})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        update_result = await db["users"].update_one(
            {"_id": object_user_id},
            {"$set": {field_path: secure_url}}
        )

        if update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "success": True,
            "message": "File uploaded successfully",
            "file": {
                "url": secure_url,
                "public_id": public_id,
                "resource_type": resource_type,
                "format": file_format,
                "updated_field": field_path,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Upload error")
        raise HTTPException(status_code=500, detail=str(e))