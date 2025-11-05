from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from decimal import Decimal

class JurisdictionBase(BaseModel):
    code: str
    name: str
    mbe_goal_typical: Optional[Decimal] = None
    vsbe_goal_typical: Optional[Decimal] = None

class JurisdictionCreate(JurisdictionBase):
    pass

class Jurisdiction(JurisdictionBase):
    id: UUID
    
    class Config:
        from_attributes = True