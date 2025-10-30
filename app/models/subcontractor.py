from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class Subcontractor(Base):
    __tablename__ = "subcontractors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    legal_name = Column(String(255), nullable=False)
    certification_number = Column(String(100))
    is_mbe = Column(Boolean, default=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="subcontractors")
    certifications = relationship("Certification", back_populates="subcontractor")
    bid_subcontractors = relationship("BidSubcontractor", back_populates="subcontractor")