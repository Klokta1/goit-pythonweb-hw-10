import redis.asyncio as redis
from fastapi import Depends, HTTPException, Request, status
from fastapi_limiter import FastAPILimiter
from app.config import REDIS_HOST, REDIS_PORT

async def setup_limiter():
    redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    redis_instance = redis.from_url(redis_url)
    await FastAPILimiter.init(redis_instance)