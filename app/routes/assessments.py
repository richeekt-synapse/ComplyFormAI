from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.pre_bid_assessment import (
    PreBidAssessment,
    PreBidAssessmentCreate,
    PreBidAssessmentDetail,
    AssessmentRequest
)
from app.services import PreBidAssessmentService

router = APIRouter(prefix="/assessments", tags=["pre-bid-assessments"])

@router.post("/perform", response_model=PreBidAssessmentDetail)
def perform_assessment(
    request: AssessmentRequest,
    db: Session = Depends(get_db)
):
    """
    Perform a comprehensive pre-bid assessment
    
    This endpoint analyzes an opportunity and provides:
    - Overall risk score (0-100, higher = more risk)
    - MBE/VSBE gap analysis
    - Available subcontractor count
    - Recommendation (BID, CAUTION, NO_BID)
    - Matching subcontractors
    - Risk factors
    """
    service = PreBidAssessmentService(db)
    
    try:
        assessment_data = service.perform_assessment(request)
        return assessment_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{assessment_id}", response_model=PreBidAssessment)
def get_assessment(
    assessment_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific pre-bid assessment"""
    service = PreBidAssessmentService(db)
    assessment = service.get_assessment(assessment_id)
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found"
        )
    
    return assessment

@router.get("/organization/{organization_id}", response_model=List[PreBidAssessment])
def get_organization_assessments(
    organization_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all assessments for an organization"""
    service = PreBidAssessmentService(db)
    return service.get_assessments_by_organization(organization_id)

@router.get("/organization/{organization_id}/summary")
def get_assessment_summary(
    organization_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get summary statistics of assessments for an organization
    
    Returns:
    - Total assessments performed
    - Count by recommendation (BID, CAUTION, NO_BID)
    - Average risk score
    """
    service = PreBidAssessmentService(db)
    return service.get_assessment_summary_by_organization(organization_id)