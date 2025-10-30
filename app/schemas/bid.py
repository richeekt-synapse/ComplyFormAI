from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from decimal import Decimal

class BidBase(BaseModel):
    solicitation_number: str
    total_amount: Decimal
    mbe_goal: Decimal

class BidCreate(BidBase):
    organization_id: UUID

class Bid(BidBase):
    id: UUID
    organization_id: UUID
    
    class Config:
        from_attributes = True

class BidSubcontractorCreate(BaseModel):
    subcontractor_id: UUID
    work_description: str
    naics_code: str
    subcontract_value: Decimal
    counts_toward_mbe: bool = False

class BidSubcontractor(BaseModel):
    id: UUID
    bid_id: UUID
    subcontractor_id: UUID
    work_description: str
    naics_code: str
    subcontract_value: Decimal
    counts_toward_mbe: bool
    
    class Config:
        from_attributes = True

class BidSubcontractorDetail(BidSubcontractor):
    subcontractor: "SubcontractorBase"
    
    class Config:
        from_attributes = True

class BidDetail(Bid):
    bid_subcontractors: List[BidSubcontractorDetail] = []
    
    class Config:
        from_attributes = True

# Avoid circular import
from app.schemas.subcontractor import SubcontractorBase
BidSubcontractorDetail.model_rebuild()