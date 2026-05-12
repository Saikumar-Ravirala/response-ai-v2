from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Dict, Any
from pydantic import BaseModel
from api.deps import get_current_user
from services.voice_provider.retell import RetellProvider
from services.voice_provider.livekit import LiveKitProvider
from core.config import settings

router = APIRouter()

class SessionRequest(BaseModel):
    agent_id: str
    metadata: Optional[Dict[str, Any]] = None

@router.post("/web-call")
async def create_retell_session(
    request: SessionRequest,
    current_user = Depends(get_current_user)
):
    """
    Calls RetellProvider to generate an access token for the frontend SDK.
    """
    provider = RetellProvider(api_key=settings.RETELL_API_KEY)
    try:
        session = await provider.create_session(
            agent_id=request.agent_id,
            metadata={**(request.metadata or {}), "client_id": current_user["client_id"]}
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Retell session: {str(e)}")

@router.post("/livekit-room")
async def create_livekit_session(
    request: SessionRequest,
    current_user = Depends(get_current_user)
):
    """
    Calls LiveKitProvider to create a room and return a participant token.
    """
    provider = LiveKitProvider(
        api_key=settings.LIVEKIT_API_KEY,
        api_secret=settings.LIVEKIT_API_SECRET,
        url=settings.LIVEKIT_URL
    )
    try:
        session = await provider.create_session(
            agent_id=request.agent_id,
            metadata={**(request.metadata or {}), "client_id": current_user["client_id"]}
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create LiveKit session: {str(e)}")
