from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jurisdiction_id = Column(UUID(as_uuid=True), ForeignKey("jurisdictions.id"))
    rule_name = Column(String(255))
    rule_type = Column(String(50))  # 'MBE', 'VSBE', 'LOCAL_PREF', etc.
    rule_definition = Column(JSONB)
    severity = Column(String(20), default='ERROR')
    
    # Relationships
    jurisdiction = relationship("Jurisdiction", back_populates="compliance_rules")