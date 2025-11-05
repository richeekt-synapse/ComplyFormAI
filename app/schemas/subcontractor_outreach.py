from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import date

class SubcontractorOutreachBase(BaseModel):
    organization_id: UUID
    opportunity_id: UUID
    subcontractor_id: UUID
    status: str  # 'CONTACTED', 'RESPONDED', 'COMMITTED', 'DECLINED'
    notes: Optional[str] = None

class SubcontractorOutreachCreate(SubcontractorOutreachBase):
    contact_date: Optional[date] = None

class SubcontractorOutreachUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class SubcontractorOutreach(SubcontractorOutreachBase):
    id: UUID
    contact_date: date
    
    class Config:
        from_attributes = True

class SubcontractorOutreachDetail(SubcontractorOutreach):
    subcontractor: "SubcontractorDirectorySchema" = None
    opportunity: "OpportunitySchema" = None
    
    class Config:
        from_attributes = True

# Avoid circular imports
from app.schemas.subcontractor_directory import SubcontractorDirectory as SubcontractorDirectorySchema
from app.schemas.opportunity import Opportunity as OpportunitySchema
SubcontractorOutreachDetail.model_rebuild()