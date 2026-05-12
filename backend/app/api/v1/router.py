from fastapi import APIRouter
from api.v1.endpoints import calls, sessions, webhooks

api_router = APIRouter()

api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
