from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app.schemas.subcontractor_directory import (
    SubcontractorDirectory,
    SubcontractorDirectoryCreate,
    SubcontractorDirectoryUpdate,
    SubcontractorSearchFilters
)
from app.services import SubcontractorDirectoryService

router = APIRouter(prefix="/directory", tags=["subcontractor-directory"])

@router.post("/", response_model=SubcontractorDirectory, status_code=status.HTTP_201_CREATED)
def add_to_directory(
    subcontractor: SubcontractorDirectoryCreate,
    db: Session = Depends(get_db)
):
    """Add a subcontractor to the directory"""
    service = SubcontractorDirectoryService(db)
    return service.create_subcontractor(subcontractor)

@router.get("/", response_model=List[SubcontractorDirectory])
def list_directory(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all subcontractors in the directory"""
    service = SubcontractorDirectoryService(db)
    return service.get_all_subcontractors(skip=skip, limit=limit)

@router.post("/search", response_model=List[SubcontractorDirectory])
def search_directory(
    filters: SubcontractorSearchFilters,
    db: Session = Depends(get_db)
):
    """
    Search subcontractors in the directory with advanced filters
    
    Filters include:
    - query: Text search on legal name
    - jurisdiction_codes: Filter by jurisdictions (e.g., ['MD', 'DC'])
    - naics_codes: Filter by NAICS codes
    - is_mbe: Filter by MBE certification
    - is_vsbe: Filter by VSBE certification
    - is_verified: Filter by verification status
    - min_rating: Minimum rating (0.0 - 5.0)
    """
    service = SubcontractorDirectoryService(db)
    return service.search_subcontractors(filters)

@router.get("/search/simple", response_model=List[SubcontractorDirectory])
def simple_search(
    q: Optional[str] = Query(None, description="Search query"),
    jurisdiction: Optional[str] = Query(None, description="Jurisdiction code (e.g., 'MD')"),
    naics: Optional[str] = Query(None, description="NAICS code"),
    is_mbe: Optional[bool] = Query(None, description="Filter by MBE status"),
    is_vsbe: Optional[bool] = Query(None, description="Filter by VSBE status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verified status"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0, description="Minimum rating"),
    db: Session = Depends(get_db)
):
    """Simple search with query parameters"""
    filters = SubcontractorSearchFilters(
        query=q,
        jurisdiction_codes=[jurisdiction] if jurisdiction else None,
        naics_codes=[naics] if naics else None,
        is_mbe=is_mbe,
        is_vsbe=is_vsbe,
        is_verified=is_verified,
        min_rating=Decimal(str(min_rating)) if min_rating is not None else None
    )
    
    service = SubcontractorDirectoryService(db)
    return service.search_subcontractors(filters)

@router.get("/{subcontractor_id}", response_model=SubcontractorDirectory)
def get_directory_entry(
    subcontractor_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific subcontractor from the directory"""
    service = SubcontractorDirectoryService(db)
    subcontractor = service.get_subcontractor(subcontractor_id)
    
    if not subcontractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subcontractor {subcontractor_id} not found in directory"
        )
    
    return subcontractor

@router.put("/{subcontractor_id}", response_model=SubcontractorDirectory)
def update_directory_entry(
    subcontractor_id: UUID,
    update_data: SubcontractorDirectoryUpdate,
    db: Session = Depends(get_db)
):
    """Update a subcontractor in the directory"""
    service = SubcontractorDirectoryService(db)
    subcontractor = service.update_subcontractor(subcontractor_id, update_data)
    
    if not subcontractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subcontractor {subcontractor_id} not found"
        )
    
    return subcontractor

@router.delete("/{subcontractor_id}")
def remove_from_directory(
    subcontractor_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove a subcontractor from the directory"""
    service = SubcontractorDirectoryService(db)
    success = service.delete_subcontractor(subcontractor_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subcontractor {subcontractor_id} not found"
        )
    
    return {"message": "Subcontractor removed from directory successfully"}

@router.get("/match/opportunity/{opportunity_id}", response_model=List[SubcontractorDirectory])
def find_matching_subcontractors(
    opportunity_id: UUID,
    is_mbe: Optional[bool] = Query(None),
    is_vsbe: Optional[bool] = Query(None),
    min_rating: float = Query(2.0, ge=0.0, le=5.0),
    db: Session = Depends(get_db)
):
    """
    Find subcontractors matching an opportunity's requirements
    """
    from app.services import OpportunityService
    
    # Get the opportunity
    opp_service = OpportunityService(db)
    opportunity = opp_service.get_opportunity(opportunity_id)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )
    
    # Find matching subcontractors
    service = SubcontractorDirectoryService(db)
    return service.get_matching_subcontractors(
        naics_codes=opportunity.naics_codes or [],
        jurisdiction_code=opportunity.jurisdiction.code,
        is_mbe=is_mbe or False,
        is_vsbe=is_vsbe or False,
        min_rating=min_rating
    )