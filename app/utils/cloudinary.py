import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
import os
from app.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

async def upload_avatar(file: UploadFile, user_id: int):
    if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
        raise ValueError("Cloudinary configuration is missing")
    
    public_id = f"contacts_api/avatars/user_{user_id}"
    
    contents = await file.read()
    
    result = cloudinary.uploader.upload(
        contents, 
        public_id=public_id,
        overwrite=True,
        folder="contacts_api/avatars",
        resource_type="image"
    )
    
    return result["secure_url"]