from sqlalchemy import Column, String, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class SubcontractorOutreach(Base):
    __tablename__ = "subcontractor_outreach"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id"))
    subcontractor_id = Column(UUID(as_uuid=True), ForeignKey("subcontractor_directory.id"))
    contact_date = Column(Date, default=datetime.utcnow)
    status = Column(String(50))  # 'CONTACTED', 'RESPONDED', 'COMMITTED', 'DECLINED'
    notes = Column(Text)
    
    # Relationships
    organization = relationship("Organization")
    opportunity = relationship("Opportunity", back_populates="outreach")
    subcontractor = relationship("SubcontractorDirectory", back_populates="outreach")