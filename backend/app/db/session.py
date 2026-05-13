# # from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# # from core.config import settings

# # engine = create_async_engine(
# #     settings.DATABASE_URL,
# #     echo=False,
# #     future=True,
# #     pool_pre_ping=True,
# # )

# # SessionLocal = async_sessionmaker(
# #     autocommit=False,
# #     autoflush=False,
# #     bind=engine,
# #     class_=AsyncSession,
# #     expire_on_commit=False,
# # )

# # async def get_db():
# #     async with SessionLocal() as session:
# #         yield session


# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker, declarative_base
# from app.core.config import settings

# # Creates the async DB engine using the URL from config
# engine = create_async_engine(settings.DATABASE_URL, echo=True)

# # Session factory — every request gets its own session
# AsyncSessionLocal = sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
# )

# Base = declarative_base()

# # FastAPI dependency — use this in route functions
# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# ONE shared Base — all models import from here
class Base(DeclarativeBase):
    pass

# Async engine for FastAPI
engine = create_async_engine(settings.DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# FastAPI dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session