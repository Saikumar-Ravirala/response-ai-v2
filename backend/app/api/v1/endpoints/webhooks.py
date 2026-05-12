from fastapi import APIRouter, Request, Header, HTTPException, BackgroundTasks, Depends
from typing import Optional
from core.config import settings
from services.voice_provider.retell import RetellProvider
from services.voice_provider.livekit import LiveKitProvider
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db
from models.call import Call
import json

router = APIRouter()

async def process_webhook_task(provider_type: str, payload: dict, db_session: AsyncSession):
    """
    Background task to normalize and save webhook data.
    """
    # This would typically be a more complex process including transcript analysis
    print(f"Processing {provider_type} webhook in background...")
    
    if provider_type == "retell":
        provider = RetellProvider(api_key=settings.RETELL_API_KEY)
    else:
        provider = LiveKitProvider(
            api_key=settings.LIVEKIT_API_KEY,
            api_secret=settings.LIVEKIT_API_SECRET,
            url=settings.LIVEKIT_URL
        )
    
    try:
        unified_call = await provider.normalize_call_data(payload)
        
        # In a real app, we would update or create the call record in DB
        # new_call = Call(...)
        # db_session.add(new_call)
        # await db_session.commit()
        print(f"Normalized call ID: {unified_call.provider_call_id}")
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")

@router.post("/retell")
async def retell_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_retell_signature: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook receiver for Retell AI.
    """
    body = await request.body()
    payload = await request.json()
    
    provider = RetellProvider(api_key=settings.RETELL_API_KEY)
    
    # Validate Signature
    is_valid = await provider.validate_webhook(
        headers={"x-retell-signature": x_retell_signature} if x_retell_signature else {},
        body=body,
        secret=settings.RETELL_WEBHOOK_SECRET
    )
    
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Hand off to background task
    background_tasks.add_task(process_webhook_task, "retell", payload, db)
    
    return {"status": "ok"}

@router.post("/livekit")
async def livekit_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook receiver for LiveKit.
    """
    body = await request.body()
    payload = await request.json()
    
    provider = LiveKitProvider(
        api_key=settings.LIVEKIT_API_KEY,
        api_secret=settings.LIVEKIT_API_SECRET,
        url=settings.LIVEKIT_URL
    )
    
    # Validate Signature (placeholder in LiveKitProvider for now)
    is_valid = await provider.validate_webhook(
        headers={"Authorization": authorization} if authorization else {},
        body=body,
        secret=settings.LIVEKIT_API_SECRET
    )
    
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Hand off to background task
    background_tasks.add_task(process_webhook_task, "livekit", payload, db)
    
    return {"status": "ok"}
