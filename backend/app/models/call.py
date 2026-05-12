from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase
import uuid
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Call(Base):
    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), index=True, nullable=False) # In a real app, this would be a ForeignKey
    agent_id = Column(String, index=True)
    provider_type = Column(String, index=True) # 'retell', 'livekit'
    provider_call_id = Column(String, unique=True, index=True)
    status = Column(String, index=True)
    outcome = Column(String, index=True)
    duration = Column(Integer)
    transcript = Column(String)
    analysis = Column(JSONB)
    recording_url = Column(String)
    raw_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
