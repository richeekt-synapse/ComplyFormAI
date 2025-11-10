from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas.bid import (
    Bid, 
    BidCreate, 
    BidDetail,
    BidSubcontractorCreate,
    BidSubcontractor
)
from app.schemas.validation import ValidationResponse
from app.services import BidService, ValidationService

router = APIRouter(prefix="/bids", tags=["bids"])

@router.post("/", response_model=Bid, status_code=status.HTTP_201_CREATED)
def create_bid(bid: BidCreate, db: Session = Depends(get_db)):
    """Create a new bid"""
    service = BidService(db)
    return service.create_bid(bid)

@router.get("/", response_model=List[BidDetail])
def list_bids(
    organization_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """List all bids"""
    service = BidService(db)
    return service.get_all_bids(organization_id)

@router.get("/{bid_id}", response_model=BidDetail)
def get_bid(bid_id: UUID, db: Session = Depends(get_db)):
    """Get a specific bid with all details"""
    service = BidService(db)
    bid = service.get_bid(bid_id)
    
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bid {bid_id} not found"
        )
    
    return bid

@router.post("/{bid_id}/subcontractors", response_model=BidSubcontractor)
def add_subcontractor_to_bid(
    bid_id: UUID,
    subcontractor: BidSubcontractorCreate,
    db: Session = Depends(get_db)
):
    """Add a subcontractor to a bid"""
    service = BidService(db)

    # Check if bid exists
    bid = service.get_bid(bid_id)
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bid {bid_id} not found"
        )

    # Check if subcontractor exists
    if not service.subcontractor_exists(subcontractor.subcontractor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subcontractor {subcontractor.subcontractor_id} not found"
        )

    return service.add_subcontractor_to_bid(bid_id, subcontractor)

@router.delete("/{bid_id}/subcontractors/{bid_subcontractor_id}")
def remove_subcontractor_from_bid(
    bid_id: UUID,
    bid_subcontractor_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove a subcontractor from a bid"""
    service = BidService(db)
    
    success = service.remove_subcontractor_from_bid(bid_id, bid_subcontractor_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcontractor not found in this bid"
        )
    
    return {"message": "Subcontractor removed successfully"}

@router.get("/{bid_id}/validate", response_model=ValidationResponse)
def validate_bid(bid_id: UUID, db: Session = Depends(get_db)):
    """Validate a bid and return results"""
    bid_service = BidService(db)
    validation_service = ValidationService(db)
    
    # Check if bid exists
    bid = bid_service.get_bid(bid_id)
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bid {bid_id} not found"
        )
    
    return validation_service.validate_bid(bid_id)