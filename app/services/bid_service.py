from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.models import Bid, BidSubcontractor
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
        query = self.db.query(Bid)
        
        if organization_id:
            query = query.filter(Bid.organization_id == organization_id)
        
        return query.all()
    
    def add_subcontractor_to_bid(
        self, 
        bid_id: UUID, 
        subcontractor_data: BidSubcontractorCreate
    ) -> BidSubcontractor:
        """Add a subcontractor to a bid"""
        bid_sub = BidSubcontractor(
            bid_id=bid_id,
            **subcontractor_data.model_dump()
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