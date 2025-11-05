from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class PreBidAssessmentBase(BaseModel):
    organization_id: UUID
    opportunity_id: UUID

class PreBidAssessmentCreate(PreBidAssessmentBase):
    pass

class PreBidAssessment(PreBidAssessmentBase):
    id: UUID
    overall_risk_score: Optional[int] = None
    mbe_gap_percentage: Optional[Decimal] = None
    vsbe_gap_percentage: Optional[Decimal] = None
    available_subcontractors_count: Optional[int] = None
    recommendation: Optional[str] = None
    recommendation_reason: Optional[str] = None
    assessed_at: datetime
    
    class Config:
        from_attributes = True

class PreBidAssessmentDetail(PreBidAssessment):
    opportunity: "OpportunitySchema" = None
    matching_subcontractors: List["SubcontractorDirectorySchema"] = []
    risk_factors: List[str] = []
    
    class Config:
        from_attributes = True

class AssessmentRequest(BaseModel):
    opportunity_id: UUID
    organization_id: UUID
    estimated_subcontract_percentage: Optional[Decimal] = 30.0

# Avoid circular imports
from app.schemas.opportunity import Opportunity as OpportunitySchema
from app.schemas.subcontractor_directory import SubcontractorDirectory as SubcontractorDirectorySchema
PreBidAssessmentDetail.model_rebuild()