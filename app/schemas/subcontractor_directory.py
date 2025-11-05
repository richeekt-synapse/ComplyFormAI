from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime

class SubcontractorDirectoryBase(BaseModel):
    legal_name: str
    federal_id: Optional[str] = None
    certifications: Optional[Dict] = None
    jurisdiction_codes: Optional[List[str]] = None
    naics_codes: Optional[List[str]] = None
    capabilities: Optional[str] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    location_city: Optional[str] = None
    rating: Optional[Decimal] = 0.0
    projects_completed: Optional[int] = 0
    is_verified: Optional[bool] = False

class SubcontractorDirectoryCreate(SubcontractorDirectoryBase):
    pass

class SubcontractorDirectoryUpdate(BaseModel):
    legal_name: Optional[str] = None
    federal_id: Optional[str] = None
    certifications: Optional[Dict] = None
    jurisdiction_codes: Optional[List[str]] = None
    naics_codes: Optional[List[str]] = None
    capabilities: Optional[str] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    location_city: Optional[str] = None
    rating: Optional[Decimal] = None
    projects_completed: Optional[int] = None
    is_verified: Optional[bool] = None

class SubcontractorDirectory(SubcontractorDirectoryBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubcontractorSearchFilters(BaseModel):
    query: Optional[str] = None
    jurisdiction_codes: Optional[List[str]] = None
    naics_codes: Optional[List[str]] = None
    is_mbe: Optional[bool] = None
    is_vsbe: Optional[bool] = None
    is_verified: Optional[bool] = None
    min_rating: Optional[Decimal] = None