from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.models import SubcontractorOutreach, SubcontractorDirectory, Opportunity
from app.schemas.subcontractor_outreach import (
    SubcontractorOutreachCreate,
    SubcontractorOutreachUpdate
)

class SubcontractorOutreachService:
    """Service for subcontractor outreach tracking"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_outreach(
        self, 
        outreach_data: SubcontractorOutreachCreate
    ) -> SubcontractorOutreach:
        """Create a new outreach record"""
        outreach = SubcontractorOutreach(**outreach_data.model_dump())
        self.db.add(outreach)
        self.db.commit()
        self.db.refresh(outreach)
        return outreach
    
    def get_outreach(self, outreach_id: UUID) -> Optional[SubcontractorOutreach]:
        """Get an outreach record by ID"""
        return self.db.query(SubcontractorOutreach).options(
            joinedload(SubcontractorOutreach.subcontractor),
            joinedload(SubcontractorOutreach.opportunity)
        ).filter(SubcontractorOutreach.id == outreach_id).first()
    
    def get_outreach_by_opportunity(
        self, 
        opportunity_id: UUID
    ) -> List[SubcontractorOutreach]:
        """Get all outreach records for an opportunity"""
        return self.db.query(SubcontractorOutreach).options(
            joinedload(SubcontractorOutreach.subcontractor),
            joinedload(SubcontractorOutreach.opportunity)
        ).filter(
            SubcontractorOutreach.opportunity_id == opportunity_id
        ).order_by(SubcontractorOutreach.contact_date.desc()).all()
    
    def get_outreach_by_organization(
        self, 
        organization_id: UUID
    ) -> List[SubcontractorOutreach]:
        """Get all outreach records for an organization"""
        return self.db.query(SubcontractorOutreach).options(
            joinedload(SubcontractorOutreach.subcontractor),
            joinedload(SubcontractorOutreach.opportunity)
        ).filter(
            SubcontractorOutreach.organization_id == organization_id
        ).order_by(SubcontractorOutreach.contact_date.desc()).all()
    
    def get_outreach_by_subcontractor(
        self, 
        subcontractor_id: UUID
    ) -> List[SubcontractorOutreach]:
        """Get all outreach records for a subcontractor"""
        return self.db.query(SubcontractorOutreach).options(
            joinedload(SubcontractorOutreach.opportunity)
        ).filter(
            SubcontractorOutreach.subcontractor_id == subcontractor_id
        ).order_by(SubcontractorOutreach.contact_date.desc()).all()
    
    def update_outreach(
        self, 
        outreach_id: UUID, 
        update_data: SubcontractorOutreachUpdate
    ) -> Optional[SubcontractorOutreach]:
        """Update an outreach record"""
        outreach = self.get_outreach(outreach_id)
        
        if not outreach:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(outreach, key):
                setattr(outreach, key, value)
        
        self.db.commit()
        self.db.refresh(outreach)
        return outreach
    
    def delete_outreach(self, outreach_id: UUID) -> bool:
        """Delete an outreach record"""
        outreach = self.get_outreach(outreach_id)
        
        if not outreach:
            return False
        
        self.db.delete(outreach)
        self.db.commit()
        return True
    
    def get_outreach_statistics(
        self, 
        organization_id: Optional[UUID] = None,
        opportunity_id: Optional[UUID] = None
    ) -> dict:
        """Get statistics about outreach efforts"""
        query = self.db.query(SubcontractorOutreach)
        
        if organization_id:
            query = query.filter(SubcontractorOutreach.organization_id == organization_id)
        
        if opportunity_id:
            query = query.filter(SubcontractorOutreach.opportunity_id == opportunity_id)
        
        all_outreach = query.all()
        
        total = len(all_outreach)
        contacted = sum(1 for o in all_outreach if o.status == 'CONTACTED')
        responded = sum(1 for o in all_outreach if o.status == 'RESPONDED')
        committed = sum(1 for o in all_outreach if o.status == 'COMMITTED')
        declined = sum(1 for o in all_outreach if o.status == 'DECLINED')
        
        return {
            "total_outreach": total,
            "contacted": contacted,
            "responded": responded,
            "committed": committed,
            "declined": declined,
            "response_rate": round((responded + committed + declined) / total * 100, 2) if total > 0 else 0,
            "commit_rate": round(committed / total * 100, 2) if total > 0 else 0
        }