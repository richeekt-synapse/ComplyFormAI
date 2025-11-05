from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime

class OpportunityBase(BaseModel):
    solicitation_number: str
    title: str
    jurisdiction_id: UUID
    agency: str
    mbe_goal: Optional[Decimal] = None
    vsbe_goal: Optional[Decimal] = None
    total_value: Optional[Decimal] = None
    naics_codes: Optional[List[str]] = None
    due_date: Optional[date] = None
    opportunity_url: Optional[str] = None
    is_active: Optional[bool] = True
    relevance_score: Optional[int] = None

class OpportunityCreate(OpportunityBase):
    posted_date: Optional[date] = None

class Opportunity(OpportunityBase):
    id: UUID
    posted_date: date
    
    class Config:
        from_attributes = True

class OpportunityDetail(Opportunity):
    jurisdiction: "JurisdictionSchema" = None
    
    class Config:
        from_attributes = True

class OpportunitySearchFilters(BaseModel):
    jurisdiction_codes: Optional[List[str]] = None
    naics_codes: Optional[List[str]] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    is_active: Optional[bool] = True
    days_until_due: Optional[int] = None

# Avoid circular import
from app.schemas.jurisdiction import Jurisdiction as JurisdictionSchema
OpportunityDetail.model_rebuild()