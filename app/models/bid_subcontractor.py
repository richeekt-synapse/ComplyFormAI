from sqlalchemy import Column, String, Text, Numeric, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class BidSubcontractor(Base):
    __tablename__ = "bid_subcontractors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bid_id = Column(UUID(as_uuid=True), ForeignKey("bids.id"))
    subcontractor_id = Column(UUID(as_uuid=True), ForeignKey("subcontractors.id"))
    work_description = Column(Text)
    naics_code = Column(String(10))
    subcontract_value = Column(Numeric(15, 2))
    counts_toward_mbe = Column(Boolean, default=False)
    category_breakdown = Column(JSONB, nullable=True)  # Stores breakdown as JSON array: [{"category": "MBE", "percentage": 50.0}, ...]

    # Relationships
    bid = relationship("Bid", back_populates="bid_subcontractors")
    subcontractor = relationship("Subcontractor", back_populates="bid_subcontractors")