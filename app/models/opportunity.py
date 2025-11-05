from sqlalchemy import Column, String, Boolean, Numeric, Date, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import date
import uuid

from app.database import Base

class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solicitation_number = Column(String(100))
    title = Column(String(500))
    jurisdiction_id = Column(UUID(as_uuid=True), ForeignKey("jurisdictions.id"))
    agency = Column(String(255))
    mbe_goal = Column(Numeric(5, 2))
    vsbe_goal = Column(Numeric(5, 2))
    total_value = Column(Numeric(15, 2))
    naics_codes = Column(ARRAY(Text))
    due_date = Column(Date)
    posted_date = Column(Date, default=date.today)
    opportunity_url = Column(Text)
    is_active = Column(Boolean, default=True)
    relevance_score = Column(Integer)  # 0-100, calculated
    
    # Relationships
    jurisdiction = relationship("Jurisdiction", back_populates="opportunities")
    assessments = relationship("PreBidAssessment", back_populates="opportunity")
    outreach = relationship("SubcontractorOutreach", back_populates="opportunity")