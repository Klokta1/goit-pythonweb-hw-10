from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
import redis.asyncio as redis
import uvicorn

from app.config import APP_NAME, APP_DESCRIPTION, API_PREFIX, ORIGINS
from app.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
from app.database.db import engine, Base
from app.routes import contacts, auth, users
from app.utils.rate_limiter import setup_limiter

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version="0.1.0",
)

# Додавання CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True
    )

app.include_router(
    auth.router,
    prefix=f"{API_PREFIX}/auth",
    tags=["authentication"],
)

app.include_router(
    users.router,
    prefix=f"{API_PREFIX}/users",
    tags=["users"],
)

app.include_router(
    contacts.router,
    prefix=f"{API_PREFIX}/contacts",
    tags=["contacts"],
)


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Ласкаво просимо до Contacts API!"}


# Ендпоінт для перевірки стану API
@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


# Ініціалізація обмежувача частоти запитів
@app.on_event("startup")
async def startup():
    await setup_limiter()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
