from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app.schemas.opportunity import (
    Opportunity,
    OpportunityCreate,
    OpportunityDetail,
    OpportunitySearchFilters
)
from app.services import OpportunityService

router = APIRouter(prefix="/opportunities", tags=["opportunities"])

@router.post("/", response_model=Opportunity, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    opportunity: OpportunityCreate,
    db: Session = Depends(get_db)
):
    """Create a new opportunity"""
    service = OpportunityService(db)
    return service.create_opportunity(opportunity)

@router.get("/", response_model=List[OpportunityDetail])
def list_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """List all opportunities with pagination"""
    service = OpportunityService(db)
    return service.get_all_opportunities(skip=skip, limit=limit, is_active=is_active)

@router.post("/search", response_model=List[OpportunityDetail])
def search_opportunities(
    filters: OpportunitySearchFilters,
    db: Session = Depends(get_db)
):
    """
    Search opportunities with advanced filters
    
    Filters include:
    - jurisdiction_codes: Filter by jurisdictions
    - naics_codes: Filter by NAICS codes
    - min_value / max_value: Filter by contract value range
    - is_active: Filter active/inactive opportunities
    - days_until_due: Filter by days remaining until due date
    """
    service = OpportunityService(db)
    return service.search_opportunities(filters)

@router.get("/search/simple", response_model=List[OpportunityDetail])
def simple_search_opportunities(
    jurisdiction: Optional[str] = Query(None, description="Jurisdiction code"),
    naics: Optional[str] = Query(None, description="NAICS code"),
    min_value: Optional[float] = Query(None, ge=0),
    max_value: Optional[float] = Query(None, ge=0),
    is_active: Optional[bool] = Query(True),
    days_until_due: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    """Simple search with query parameters"""
    filters = OpportunitySearchFilters(
        jurisdiction_codes=[jurisdiction] if jurisdiction else None,
        naics_codes=[naics] if naics else None,
        min_value=Decimal(str(min_value)) if min_value is not None else None,
        max_value=Decimal(str(max_value)) if max_value is not None else None,
        is_active=is_active,
        days_until_due=days_until_due
    )
    
    service = OpportunityService(db)
    return service.search_opportunities(filters)

@router.get("/{opportunity_id}", response_model=OpportunityDetail)
def get_opportunity(
    opportunity_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific opportunity"""
    service = OpportunityService(db)
    opportunity = service.get_opportunity(opportunity_id)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )
    
    return opportunity

@router.get("/jurisdiction/{jurisdiction_id}", response_model=List[OpportunityDetail])
def get_opportunities_by_jurisdiction(
    jurisdiction_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all active opportunities for a specific jurisdiction"""
    service = OpportunityService(db)
    return service.get_opportunities_by_jurisdiction(jurisdiction_id)

@router.put("/{opportunity_id}", response_model=Opportunity)
def update_opportunity(
    opportunity_id: UUID,
    update_data: dict,
    db: Session = Depends(get_db)
):
    """Update an opportunity"""
    service = OpportunityService(db)
    opportunity = service.update_opportunity(opportunity_id, update_data)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )
    
    return opportunity

@router.post("/{opportunity_id}/deactivate")
def deactivate_opportunity(
    opportunity_id: UUID,
    db: Session = Depends(get_db)
):
    """Deactivate an opportunity (mark as closed/expired)"""
    service = OpportunityService(db)
    success = service.deactivate_opportunity(opportunity_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )
    
    return {"message": "Opportunity deactivated successfully"}

@router.get("/alerts/relevant", response_model=List[OpportunityDetail])
def get_relevant_opportunities(
    organization_naics: List[str] = Query(..., description="Organization NAICS codes"),
    organization_jurisdictions: List[str] = Query(..., description="Organization jurisdictions"),
    min_relevance: int = Query(50, ge=0, le=100, description="Minimum relevance score"),
    db: Session = Depends(get_db)
):
    """
    Get opportunities relevant to an organization based on NAICS and jurisdiction
    This powers the opportunity alerts feature
    """
    service = OpportunityService(db)
    
    # Get all active opportunities
    opportunities = service.get_all_opportunities(is_active=True)
    
    # Calculate relevance scores and filter
    relevant_opportunities = []
    for opp in opportunities:
        score = service.calculate_relevance_score(
            opp,
            organization_naics,
            organization_jurisdictions
        )
        if score >= min_relevance:
            opp.relevance_score = score
            relevant_opportunities.append(opp)
    
    # Sort by relevance score
    relevant_opportunities.sort(key=lambda x: x.relevance_score, reverse=True)
    
    return relevant_opportunities