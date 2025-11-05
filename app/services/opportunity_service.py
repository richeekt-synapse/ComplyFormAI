from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import date, datetime, timedelta
from app.models import Opportunity, Jurisdiction
from app.schemas.opportunity import OpportunityCreate, OpportunitySearchFilters

class OpportunityService:
    """Service for opportunity operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_opportunity(
        self, 
        opportunity_data: OpportunityCreate
    ) -> Opportunity:
        """Create a new opportunity"""
        opportunity = Opportunity(**opportunity_data.model_dump())
        self.db.add(opportunity)
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity
    
    def get_opportunity(self, opportunity_id: UUID) -> Optional[Opportunity]:
        """Get an opportunity by ID with relationships"""
        return self.db.query(Opportunity).options(
            joinedload(Opportunity.jurisdiction)
        ).filter(Opportunity.id == opportunity_id).first()
    
    def get_all_opportunities(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = True
    ) -> List[Opportunity]:
        """Get all opportunities with pagination"""
        query = self.db.query(Opportunity).options(
            joinedload(Opportunity.jurisdiction)
        )
        
        if is_active is not None:
            query = query.filter(Opportunity.is_active == is_active)
        
        return query.order_by(
            Opportunity.posted_date.desc()
        ).offset(skip).limit(limit).all()
    
    def search_opportunities(
        self, 
        filters: OpportunitySearchFilters
    ) -> List[Opportunity]:
        """Search opportunities with various filters"""
        query = self.db.query(Opportunity).options(
            joinedload(Opportunity.jurisdiction)
        )
        
        # Filter by active status
        if filters.is_active is not None:
            query = query.filter(Opportunity.is_active == filters.is_active)
        
        # Filter by jurisdiction codes
        if filters.jurisdiction_codes:
            query = query.join(Jurisdiction).filter(
                Jurisdiction.code.in_(filters.jurisdiction_codes)
            )
        
        # Filter by NAICS codes
        if filters.naics_codes:
            query = query.filter(
                Opportunity.naics_codes.overlap(filters.naics_codes)
            )
        
        # Filter by value range
        if filters.min_value is not None:
            query = query.filter(Opportunity.total_value >= filters.min_value)
        
        if filters.max_value is not None:
            query = query.filter(Opportunity.total_value <= filters.max_value)
        
        # Filter by days until due
        if filters.days_until_due is not None:
            target_date = date.today() + timedelta(days=filters.days_until_due)
            query = query.filter(
                and_(
                    Opportunity.due_date >= date.today(),
                    Opportunity.due_date <= target_date
                )
            )
        
        # Order by relevance score and due date
        query = query.order_by(
            Opportunity.relevance_score.desc().nullslast(),
            Opportunity.due_date.asc()
        )
        
        return query.all()
    
    def get_opportunities_by_jurisdiction(
        self, 
        jurisdiction_id: UUID
    ) -> List[Opportunity]:
        """Get all opportunities for a specific jurisdiction"""
        return self.db.query(Opportunity).options(
            joinedload(Opportunity.jurisdiction)
        ).filter(
            Opportunity.jurisdiction_id == jurisdiction_id,
            Opportunity.is_active == True
        ).order_by(Opportunity.due_date.asc()).all()
    
    def update_opportunity(
        self, 
        opportunity_id: UUID, 
        update_data: dict
    ) -> Optional[Opportunity]:
        """Update an opportunity"""
        opportunity = self.get_opportunity(opportunity_id)
        
        if not opportunity:
            return None
        
        for key, value in update_data.items():
            if hasattr(opportunity, key):
                setattr(opportunity, key, value)
        
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity
    
    def deactivate_opportunity(self, opportunity_id: UUID) -> bool:
        """Deactivate an opportunity (mark as inactive)"""
        opportunity = self.get_opportunity(opportunity_id)
        
        if not opportunity:
            return False
        
        opportunity.is_active = False
        self.db.commit()
        return True
    
    def calculate_relevance_score(
        self, 
        opportunity: Opportunity,
        organization_naics: List[str],
        organization_jurisdictions: List[str]
    ) -> int:
        """
        Calculate relevance score for an opportunity (0-100)
        Based on NAICS match, jurisdiction match, and other factors
        """
        score = 0
        
        # NAICS code match (40 points)
        if opportunity.naics_codes:
            matching_naics = set(opportunity.naics_codes) & set(organization_naics)
            if matching_naics:
                score += 40
        
        # Jurisdiction match (30 points)
        jurisdiction = self.db.query(Jurisdiction).filter(
            Jurisdiction.id == opportunity.jurisdiction_id
        ).first()
        if jurisdiction and jurisdiction.code in organization_jurisdictions:
            score += 30
        
        # Value range (15 points) - prefer opportunities in sweet spot
        if opportunity.total_value:
            if 100000 <= opportunity.total_value <= 5000000:
                score += 15
            elif opportunity.total_value < 100000:
                score += 5
        
        # Time until due (15 points) - prefer opportunities with reasonable time
        if opportunity.due_date:
            days_until_due = (opportunity.due_date - date.today()).days
            if 14 <= days_until_due <= 60:
                score += 15
            elif 7 <= days_until_due < 14 or 60 < days_until_due <= 90:
                score += 8
        
        return min(score, 100)