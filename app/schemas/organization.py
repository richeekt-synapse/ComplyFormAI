from pydantic import BaseModel
from uuid import UUID

class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: UUID
    
    class Config:
        from_attributes = True