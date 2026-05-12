from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime

class UnifiedCall(BaseModel):
    """
    Unified schema for calls across different voice providers.
    """
    provider_type: str = Field(..., description="The voice provider (e.g., 'retell', 'livekit')")
    provider_call_id: str = Field(..., description="The original call ID from the provider")
    status: str = Field(..., description="Current status of the call")
    duration: Optional[int] = Field(None, description="Duration of the call in seconds")
    transcript: Optional[str] = Field(None, description="Full transcript of the call")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Original JSON payload from the provider")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
