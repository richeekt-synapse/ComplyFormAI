from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class Bid(Base):
    __tablename__ = "bids"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    solicitation_number = Column(String(50))
    total_amount = Column(Numeric(15, 2))
    mbe_goal = Column(Numeric(5, 2))
    
    # Relationships
    organization = relationship("Organization", back_populates="bids")
    bid_subcontractors = relationship("BidSubcontractor", back_populates="bid")
    validation_results = relationship("ValidationResult", back_populates="bid")