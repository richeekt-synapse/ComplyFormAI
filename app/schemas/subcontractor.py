from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List

class SubcontractorBase(BaseModel):
    legal_name: str
    certification_number: Optional[str] = None
    is_mbe: bool = False

class SubcontractorCreate(SubcontractorBase):
    organization_id: UUID

class Subcontractor(SubcontractorBase):
    id: UUID
    organization_id: UUID
    
    class Config:
        from_attributes = True

class CertificationSchema(BaseModel):
    id: UUID
    cert_number: Optional[str]
    cert_type: Optional[str]
    naics_codes: Optional[List[str]]
    
    class Config:
        from_attributes = True

class SubcontractorDetail(Subcontractor):
    certifications: List[CertificationSchema] = []
    
    class Config:
        from_attributes = True