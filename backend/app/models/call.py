# from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
# from sqlalchemy.dialects.postgresql import UUID, JSONB
# from sqlalchemy.orm import DeclarativeBase
# import uuid
# from datetime import datetime

# class Base(DeclarativeBase):
#     pass

# class Call(Base):
#     __tablename__ = "calls"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     client_id = Column(UUID(as_uuid=True), index=True, nullable=False) # In a real app, this would be a ForeignKey
#     agent_id = Column(String, index=True)
#     provider_type = Column(String, index=True) # 'retell', 'livekit'
#     provider_call_id = Column(String, unique=True, index=True)
#     status = Column(String, index=True)
#     outcome = Column(String, index=True)
#     duration = Column(Integer)
#     transcript = Column(String)
#     analysis = Column(JSONB)
#     recording_url = Column(String)
#     raw_data = Column(JSONB)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.session import Base   # ← use the shared Base, not a local one
import uuid

class Call(Base):
    __tablename__ = "calls"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # ✅ Now a real FK to organizations — this is your tenant isolation link
    org_id           = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # ✅ FK to users — which agent/user is associated with this call
    agent_id         = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Call provider info
    provider_type    = Column(String, index=True)        # 'retell', 'livekit'
    provider_call_id = Column(String, unique=True, index=True)
    
    # Call details
    status           = Column(String, index=True)        # 'initiated', 'in_progress', 'completed', 'failed'
    outcome          = Column(String, index=True)        # 'successful', 'no_answer', 'voicemail', etc.
    duration         = Column(Integer)                   # seconds
    transcript       = Column(Text)                      # long text, use Text not String
    analysis         = Column(JSONB)                     # AI analysis results
    recording_url    = Column(String)
    raw_data         = Column(JSONB)                     # full provider payload

    # Timestamps — use server-side func.now() instead of Python datetime.utcnow
    created_at       = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)