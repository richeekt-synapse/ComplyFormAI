from sqlalchemy import Column, String, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class Jurisdiction(Base):
    __tablename__ = "jurisdictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(10), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    mbe_goal_typical = Column(Numeric(5, 2))
    vsbe_goal_typical = Column(Numeric(5, 2))
    
    # Relationships
    compliance_rules = relationship("ComplianceRule", back_populates="jurisdiction")
    opportunities = relationship("Opportunity", back_populates="jurisdiction")