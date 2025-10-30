from pydantic import BaseModel
from uuid import UUID
from typing import List
from datetime import datetime

class ValidationResult(BaseModel):
    id: UUID
    bid_id: UUID
    rule_name: str
    status: str
    error_message: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ValidationResponse(BaseModel):
    bid_id: UUID
    overall_status: str
    total_validations: int
    passed: int
    failed: int
    warnings: int
    validations: List[ValidationResult]