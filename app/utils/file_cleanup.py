import re
from typing import Set, Dict, Any, Union, List
import cloudinary
import cloudinary.uploader
import os
import logging

logger = logging.getLogger("portfolio-cleanup")

def extract_upload_paths(obj: Any, paths: Set[tuple] = None) -> Set[tuple]:
    """
    Recursively extracts all unique Cloudinary and local upload paths from any JSON/Object.
    Returns a set of tuples (type, value) to be used with delete_upload_file.
    """
    if paths is None:
        paths = set()
    
    if not obj:
        return paths

    if isinstance(obj, str):
        # 1. Local Uploads
        if "/uploads/" in obj:
            file_name = obj.split("/uploads/").pop()
            paths.add(("local", file_name))
        
        # 2. GridFS / Legacy API uploads
        elif "/api/upload/" in obj:
            file_id = obj.split("/api/upload/").pop()
            paths.add(("gridfs", file_id))
            
        # 3. Cloudinary URLs (Smart extraction)
        elif "res.cloudinary.com" in obj:
            # Matches everything after /upload/ and before the file extension
            # Example: ...upload/v12345/portfolio_uploads/img_99.jpg -> portfolio_uploads/img_99
            parts = obj.split("/upload/")
            if len(parts) > 1:
                after_upload = parts[1].split("/")
                # Skip version tag (v12345) if it exists
                path_parts = after_upload[1:] if after_upload[0].startswith('v') else after_upload
                
                full_path = "/".join(path_parts)
                # Remove file extension (e.g., .jpg, .png)
                public_id = full_path.rsplit('.', 1)[0] if '.' in full_path else full_path
                paths.add(("cloudinary", public_id))
                
    elif isinstance(obj, list):
        for item in obj:
            extract_upload_paths(item, paths)
            
    elif isinstance(obj, dict):
        for val in obj.values():
            extract_upload_paths(val, paths)
            
    return paths

async def delete_upload_file(type: str, value: str):
    """Deletes redundant files from Cloudinary or local storage."""
    if not value:
        return

    if type == "cloudinary":
        try:
            result = cloudinary.uploader.destroy(value)
            logger.info(f"🗑️ Cloudinary item deleted ({value}): {result.get('result')}")
        except Exception as e:
            logger.error(f"❌ Cloudinary delete failed for {value}: {str(e)}")
            
    elif type == "local":
        file_path = os.path.join(os.getcwd(), 'uploads', value)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"🗑️ Deleted local file: {value}")
            except Exception as e:
                logger.error(f"❌ Failed to delete local file {value}: {str(e)}")
