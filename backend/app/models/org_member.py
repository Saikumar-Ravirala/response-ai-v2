from sqlalchemy import Column, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid
import enum


class OrgRole(enum.Enum):
    owner  = "owner"
    admin  = "admin"
    member = "member"
    viewer = "viewer"


class OrgMembership(Base):
    __tablename__ = "org_memberships"

    id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    org_id  = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    role    = Column(SAEnum(OrgRole), nullable=False, default=OrgRole.member)

    # This is what build_scopes uses — membership.org.slug
    org     = relationship("Organization", lazy="select")