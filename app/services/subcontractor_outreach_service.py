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

        # Auto-update contractor usage count for network effects
        self._update_subcontractor_usage_count(outreach.subcontractor_id)

        return outreach

    def _update_subcontractor_usage_count(self, subcontractor_id: UUID) -> None:
        """Update the contractor usage count for a subcontractor after outreach changes"""
        from sqlalchemy import func

        # Calculate unique contractor count
        count = self.db.query(func.count(func.distinct(SubcontractorOutreach.organization_id)))\
            .filter(SubcontractorOutreach.subcontractor_id == subcontractor_id)\
            .scalar()

        # Update the subcontractor directory entry
        subcontractor = self.db.query(SubcontractorDirectory)\
            .filter(SubcontractorDirectory.id == subcontractor_id)\
            .first()

        if subcontractor:
            subcontractor.contractors_using_count = count or 0
            self.db.commit()
    
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

        subcontractor_id = outreach.subcontractor_id

        self.db.delete(outreach)
        self.db.commit()

        # Update contractor usage count after deletion
        self._update_subcontractor_usage_count(subcontractor_id)

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

    def bulk_create_outreach_from_assessment(
        self,
        organization_id: UUID,
        opportunity_id: UUID,
        subcontractor_ids: List[UUID],
        initial_status: str = 'CONTACTED',
        notes: Optional[str] = None
    ) -> List[SubcontractorOutreach]:
        """
        Bulk create outreach records for multiple subcontractors

        This is useful when an assessment identifies potential subcontractors
        and the organization wants to track outreach to all of them.

        Args:
            organization_id: The organization doing the outreach
            opportunity_id: The opportunity being pursued
            subcontractor_ids: List of subcontractor IDs from directory
            initial_status: Initial status (default: 'CONTACTED')
            notes: Optional notes to add to all records

        Returns:
            List of created outreach records
        """
        from datetime import date

        outreach_records = []

        for subcontractor_id in subcontractor_ids:
            # Check if outreach already exists for this combination
            existing = self.db.query(SubcontractorOutreach).filter(
                SubcontractorOutreach.organization_id == organization_id,
                SubcontractorOutreach.opportunity_id == opportunity_id,
                SubcontractorOutreach.subcontractor_id == subcontractor_id
            ).first()

            if existing:
                # Skip if already tracked
                continue

            outreach = SubcontractorOutreach(
                organization_id=organization_id,
                opportunity_id=opportunity_id,
                subcontractor_id=subcontractor_id,
                contact_date=date.today(),
                status=initial_status,
                notes=notes or f"Auto-created from pre-bid assessment"
            )

            self.db.add(outreach)
            outreach_records.append(outreach)

        self.db.commit()

        # Refresh all records to get IDs
        for outreach in outreach_records:
            self.db.refresh(outreach)

        return outreach_records

    def get_pending_outreach(
        self,
        organization_id: UUID,
        opportunity_id: Optional[UUID] = None
    ) -> List[SubcontractorOutreach]:
        """
        Get all pending outreach records (CONTACTED status) for follow-up

        This helps organizations track which subcontractors they've contacted
        but haven't heard back from yet.

        Args:
            organization_id: The organization
            opportunity_id: Optional filter by specific opportunity

        Returns:
            List of outreach records with CONTACTED status
        """
        query = self.db.query(SubcontractorOutreach).options(
            joinedload(SubcontractorOutreach.subcontractor),
            joinedload(SubcontractorOutreach.opportunity)
        ).filter(
            SubcontractorOutreach.organization_id == organization_id,
            SubcontractorOutreach.status == 'CONTACTED'
        )

        if opportunity_id:
            query = query.filter(SubcontractorOutreach.opportunity_id == opportunity_id)

        return query.order_by(SubcontractorOutreach.contact_date.asc()).all()