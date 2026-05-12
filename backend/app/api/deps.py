from typing import Generator, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import SessionLocal
from fastapi import Depends, HTTPException, status
from core.security import SECRET_KEY # Assuming it exists in security.py
from core.config import settings

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

# Placeholder for Auth Dependency
async def get_current_user(db: AsyncSession = Depends(get_db)):
    # In a real app, this would validate JWT and return the user
    # For now, we'll return a mock user/client context
    return {"id": "mock-user-uuid", "client_id": "mock-client-uuid", "role": "admin"}
