from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime
from api.deps import get_db, get_current_user
from models.call import Call
from schemas.call import UnifiedCall

router = APIRouter()

@router.get("/", response_model=List[UnifiedCall])
async def list_calls(
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    outcome: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Paginated list of calls with filters.
    """
    query = select(Call).where(Call.client_id == current_user["client_id"])

    if agent_id:
        query = query.where(Call.agent_id == agent_id)
    if status:
        query = query.where(Call.status == status)
    if outcome:
        query = query.where(Call.outcome == outcome)
    if start_date:
        query = query.where(Call.created_at >= start_date)
    if end_date:
        query = query.where(Call.created_at <= end_date)

    # Pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Call.created_at.desc())
    
    result = await db.execute(query)
    calls = result.scalars().all()
    return calls

@router.get("/{id}", response_model=UnifiedCall)
async def get_call_details(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retrieve full call details.
    """
    query = select(Call).where(Call.id == id, Call.client_id == current_user["client_id"])
    result = await db.execute(query)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return call

@router.post("/sync")
async def sync_calls(
    current_user = Depends(get_current_user)
):
    """
    Manual trigger to force-sync data from providers.
    """
    # In a real app, this would trigger a Celery task
    return {"message": "Sync triggered successfully"}
