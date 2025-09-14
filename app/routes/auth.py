from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import jwt, JWTError

from app.database.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, EmailSchema
from app.utils.auth import authenticate_user, create_access_token, get_password_hash, get_current_user
from app.utils.email import create_email_verification_token, send_verification_email
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
        user: UserCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з такою електронною адресою вже існує"
        )

    hashed_password = get_password_hash(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        confirmed=False
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    verification_token = create_email_verification_token(db_user.email)

    await send_verification_email(
        email=db_user.email,
        username=db_user.username,
        token=verification_token,
        background_tasks=background_tasks
    )

    return db_user


@router.post("/login", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний email або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify-email")
async def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        scope = payload.get("scope")

        if scope != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Недійсний токен верифікації"
            )

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Користувача не знайдено"
            )

        if user.confirmed:
            return {"message": "Електронна пошта вже підтверджена"}

        user.confirmed = True
        db.commit()

        return {"message": "Електронна пошта успішно підтверджена"}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недійсний або прострочений токен"
        )


@router.post("/request-email-verification")
async def request_email_verification(
        email_schema: EmailSchema,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email_schema.email).first()
    if not user:
        return {"message": "Якщо ця електронна адреса зареєстрована, лист з інструкціями буде надіслано"}

    if user.confirmed:
        return {"message": "Електронна пошта вже підтверджена"}

    verification_token = create_email_verification_token(user.email)

    await send_verification_email(
        email=user.email,
        username=user.username,
        token=verification_token,
        background_tasks=background_tasks
    )

    return {"message": "Лист з інструкціями надіслано"}
