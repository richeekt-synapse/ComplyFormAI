from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas.subcontractor import (
    Subcontractor,
    SubcontractorCreate,
    SubcontractorDetail
)
from app.services import SubcontractorService

router = APIRouter(prefix="/subcontractors", tags=["subcontractors"])

@router.post("/", response_model=Subcontractor, status_code=status.HTTP_201_CREATED)
def create_subcontractor(
    subcontractor: SubcontractorCreate,
    db: Session = Depends(get_db)
):
    """Create a new subcontractor"""
    service = SubcontractorService(db)
    return service.create_subcontractor(subcontractor)

@router.get("/", response_model=List[SubcontractorDetail])
def list_subcontractors(
    organization_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """List all subcontractors"""
    service = SubcontractorService(db)
    return service.get_all_subcontractors(organization_id)

@router.get("/search", response_model=List[SubcontractorDetail])
def search_subcontractors(
    q: Optional[str] = Query(None, description="Search query"),
    is_mbe: Optional[bool] = Query(None, description="Filter by MBE status"),
    organization_id: Optional[UUID] = Query(None, description="Filter by organization"),
    db: Session = Depends(get_db)
):
    """Search for subcontractors"""
    service = SubcontractorService(db)
    return service.search_subcontractors(q, is_mbe, organization_id)

@router.get("/{subcontractor_id}", response_model=SubcontractorDetail)
def get_subcontractor(
    subcontractor_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific subcontractor"""
    service = SubcontractorService(db)
    subcontractor = service.get_subcontractor(subcontractor_id)
    
    if not subcontractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subcontractor {subcontractor_id} not found"
        )
    
    return subcontractor

@router.put("/{subcontractor_id}", response_model=Subcontractor)
def update_subcontractor(
    subcontractor_id: UUID,
    update_data: dict,
    db: Session = Depends(get_db)
):
    """Update a subcontractor"""
    service = SubcontractorService(db)
    subcontractor = service.update_subcontractor(subcontractor_id, update_data)
    
    if not subcontractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subcontractor {subcontractor_id} not found"
        )
    
    return subcontractor

@router.delete("/{subcontractor_id}")
def delete_subcontractor(
    subcontractor_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a subcontractor"""
    service = SubcontractorService(db)
    success = service.delete_subcontractor(subcontractor_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subcontractor {subcontractor_id} not found"
        )
    
    return {"message": "Subcontractor deleted successfully"}