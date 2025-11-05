from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.jurisdiction import Jurisdiction, JurisdictionCreate
from app.services import JurisdictionService

router = APIRouter(prefix="/jurisdictions", tags=["jurisdictions"])

@router.post("/", response_model=Jurisdiction, status_code=status.HTTP_201_CREATED)
def create_jurisdiction(
    jurisdiction: JurisdictionCreate,
    db: Session = Depends(get_db)
):
    """Create a new jurisdiction"""
    service = JurisdictionService(db)
    return service.create_jurisdiction(jurisdiction)

@router.get("/", response_model=List[Jurisdiction])
def list_jurisdictions(db: Session = Depends(get_db)):
    """List all jurisdictions"""
    service = JurisdictionService(db)
    return service.get_all_jurisdictions()

@router.get("/{jurisdiction_id}", response_model=Jurisdiction)
def get_jurisdiction(
    jurisdiction_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific jurisdiction"""
    service = JurisdictionService(db)
    jurisdiction = service.get_jurisdiction(jurisdiction_id)
    
    if not jurisdiction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Jurisdiction {jurisdiction_id} not found"
        )
    
    return jurisdiction

@router.get("/code/{code}", response_model=Jurisdiction)
def get_jurisdiction_by_code(
    code: str,
    db: Session = Depends(get_db)
):
    """Get a jurisdiction by code (e.g., 'MD', 'DC')"""
    service = JurisdictionService(db)
    jurisdiction = service.get_jurisdiction_by_code(code)
    
    if not jurisdiction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Jurisdiction with code '{code}' not found"
        )
    
    return jurisdiction