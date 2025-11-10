from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.models import Bid, BidSubcontractor, Subcontractor, SubcontractorDirectory
from app.schemas.bid import BidCreate, BidSubcontractorCreate

class BidService:
    """Service for bid operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_bid(self, bid_data: BidCreate) -> Bid:
        """Create a new bid"""
        bid = Bid(**bid_data.model_dump())
        self.db.add(bid)
        self.db.commit()
        self.db.refresh(bid)
        return bid
    
    def get_bid(self, bid_id: UUID) -> Optional[Bid]:
        """Get a bid by ID with all relationships"""
        return self.db.query(Bid).options(
            joinedload(Bid.bid_subcontractors).joinedload(BidSubcontractor.subcontractor)
        ).filter(Bid.id == bid_id).first()
    
    def get_all_bids(self, organization_id: Optional[UUID] = None) -> List[Bid]:
        """Get all bids, optionally filtered by organization"""
        query = self.db.query(Bid).options(
            joinedload(Bid.bid_subcontractors).joinedload(BidSubcontractor.subcontractor)
        )
        
        if organization_id:
            query = query.filter(Bid.organization_id == organization_id)
        
        return query.all()
    
    def subcontractor_exists(self, subcontractor_id: UUID) -> bool:
        """Check if a subcontractor exists in the directory"""
        return self.db.query(SubcontractorDirectory).filter(
            SubcontractorDirectory.id == subcontractor_id
        ).first() is not None

    def _ensure_subcontractor_in_org(self, subcontractor_id: UUID, bid_id: UUID) -> None:
        """
        Ensure subcontractor from directory exists in organization's subcontractors table.
        If not, copy it from the directory.
        """
        # Check if already in organization's subcontractors
        existing = self.db.query(Subcontractor).filter(
            Subcontractor.id == subcontractor_id
        ).first()

        if existing:
            return  # Already exists

        # Get from directory
        directory_sub = self.db.query(SubcontractorDirectory).filter(
            SubcontractorDirectory.id == subcontractor_id
        ).first()

        if not directory_sub:
            return  # Will fail on foreign key, but validation should catch this

        # Get organization_id from the bid
        bid = self.db.query(Bid).filter(Bid.id == bid_id).first()
        if not bid:
            return

        # Copy to organization's subcontractors
        org_subcontractor = Subcontractor(
            id=directory_sub.id,  # Use same ID for consistency
            organization_id=bid.organization_id,
            legal_name=directory_sub.legal_name,
            certification_number=directory_sub.federal_id,
            is_mbe=directory_sub.certifications.get('mbe', False) if directory_sub.certifications else False
        )
        self.db.add(org_subcontractor)
        self.db.flush()  # Flush but don't commit yet

    def add_subcontractor_to_bid(
        self,
        bid_id: UUID,
        subcontractor_data: BidSubcontractorCreate
    ) -> BidSubcontractor:
        """Add a subcontractor to a bid"""
        # Ensure the subcontractor exists in the organization's table
        self._ensure_subcontractor_in_org(subcontractor_data.subcontractor_id, bid_id)

        # Convert category_breakdown to dict format for JSONB storage
        data_dict = subcontractor_data.model_dump()
        if data_dict.get('category_breakdown'):
            # Convert list of CategoryBreakdown objects to list of dicts
            data_dict['category_breakdown'] = [
                {"category": entry.category.upper(), "percentage": entry.percentage}
                for entry in subcontractor_data.category_breakdown
            ]

        bid_sub = BidSubcontractor(
            bid_id=bid_id,
            **data_dict
        )
        self.db.add(bid_sub)
        self.db.commit()
        self.db.refresh(bid_sub)
        return bid_sub
    
    def remove_subcontractor_from_bid(
        self, 
        bid_id: UUID, 
        bid_subcontractor_id: UUID
    ) -> bool:
        """Remove a subcontractor from a bid"""
        bid_sub = self.db.query(BidSubcontractor).filter(
            BidSubcontractor.id == bid_subcontractor_id,
            BidSubcontractor.bid_id == bid_id
        ).first()
        
        if not bid_sub:
            return False
        
        self.db.delete(bid_sub)
        self.db.commit()
        return True
    
    def update_bid(self, bid_id: UUID, bid_data: dict) -> Optional[Bid]:
        """Update a bid"""
        bid = self.db.query(Bid).filter(Bid.id == bid_id).first()
        
        if not bid:
            return None
        
        for key, value in bid_data.items():
            if hasattr(bid, key):
                setattr(bid, key, value)
        
        self.db.commit()
        self.db.refresh(bid)
        return bid