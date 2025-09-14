from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from app.database.db import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.utils.auth import get_current_user
from app.utils.cloudinary import upload_avatar

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
        current_user: User = Depends(get_current_user),
        # Обмеження: 10 запитів за 1 хвилину
        limiter: RateLimiter = Depends(RateLimiter(times=10, seconds=60))
):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_user_info(
        user_update: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.patch("/me/avatar", response_model=UserResponse)
async def update_avatar(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл повинен бути зображенням"
        )

    try:
        avatar_url = await upload_avatar(file, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при завантаженні аватара: {str(e)}"
        )

    current_user.avatar = avatar_url
    db.commit()
    db.refresh(current_user)

    return current_user
