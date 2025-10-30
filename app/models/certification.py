from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class Certification(Base):
    __tablename__ = "certifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subcontractor_id = Column(UUID(as_uuid=True), ForeignKey("subcontractors.id"))
    cert_number = Column(String(100))
    cert_type = Column(String(50))
    naics_codes = Column(JSONB)
    
    # Relationships
    subcontractor = relationship("Subcontractor", back_populates="certifications")