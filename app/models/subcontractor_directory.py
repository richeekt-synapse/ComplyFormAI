from sqlalchemy import Column, String, Boolean, Integer, Numeric, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class SubcontractorDirectory(Base):
    __tablename__ = "subcontractor_directory"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    legal_name = Column(String(255), nullable=False)
    federal_id = Column(String(20))
    certifications = Column(JSONB)  # {mbe: true, vsbe: true, dbe: false}
    jurisdiction_codes = Column(ARRAY(Text))  # ['MD', 'DC']
    naics_codes = Column(ARRAY(Text))
    capabilities = Column(Text)
    contact_email = Column(String(255))
    phone = Column(String(20))
    location_city = Column(String(100))
    rating = Column(Numeric(3, 2), default=0.0)
    projects_completed = Column(Integer, default=0)
    contractors_using_count = Column(Integer, default=0)  # Network effect: how many contractors use this sub
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    outreach = relationship("SubcontractorOutreach", back_populates="subcontractor")