from pydantic import BaseModel, field_validator
from uuid import UUID
from typing import Optional, List, Dict
from decimal import Decimal

class CategoryBreakdown(BaseModel):
    """Category breakdown entry with category name and percentage"""
    category: str  # MBE, WBE, SBE, VSBE
    percentage: float

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
    category_breakdown: Optional[List[CategoryBreakdown]] = None

    @field_validator('category_breakdown')
    @classmethod
    def validate_breakdown(cls, v):
        if v is not None and len(v) > 0:
            # Validate that percentages sum to 100
            total = sum(entry.percentage for entry in v)
            if abs(total - 100.0) > 0.01:  # Allow small floating point differences
                raise ValueError(f"Category breakdown percentages must sum to 100%, got {total}%")

            # Validate category names
            valid_categories = {'MBE', 'WBE', 'SBE', 'VSBE', 'DBE', 'CBE', 'NON-MBE'}
            for entry in v:
                if entry.category.upper() not in valid_categories:
                    raise ValueError(f"Invalid category: {entry.category}. Must be one of {valid_categories}")
        return v

class BidSubcontractor(BaseModel):
    id: UUID
    bid_id: UUID
    subcontractor_id: UUID
    work_description: str
    naics_code: str
    subcontract_value: Decimal
    counts_toward_mbe: bool
    category_breakdown: Optional[List[Dict]] = None

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