from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class PreBidAssessment(Base):
    __tablename__ = "pre_bid_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id"))
    overall_risk_score = Column(Integer)  # 0-100
    mbe_gap_percentage = Column(Numeric(5, 2))  # Shortfall if negative
    vsbe_gap_percentage = Column(Numeric(5, 2))
    available_subcontractors_count = Column(Integer)
    recommendation = Column(String(50))  # 'BID', 'NO_BID', 'CAUTION'
    recommendation_reason = Column(Text)
    assessed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization")
    opportunity = relationship("Opportunity", back_populates="assessments")