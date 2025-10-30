from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models import Subcontractor, Certification
from app.schemas.subcontractor import SubcontractorCreate

class SubcontractorService:
    """Service for subcontractor operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_subcontractor(self, subcontractor_data: SubcontractorCreate) -> Subcontractor:
        """Create a new subcontractor"""
        subcontractor = Subcontractor(**subcontractor_data.model_dump())
        self.db.add(subcontractor)
        self.db.commit()
        self.db.refresh(subcontractor)
        return subcontractor
    
    def get_subcontractor(self, subcontractor_id: UUID) -> Optional[Subcontractor]:
        """Get a subcontractor by ID with certifications"""
        return self.db.query(Subcontractor).options(
            joinedload(Subcontractor.certifications)
        ).filter(Subcontractor.id == subcontractor_id).first()
    
    def search_subcontractors(
        self, 
        query: Optional[str] = None,
        is_mbe: Optional[bool] = None,
        organization_id: Optional[UUID] = None
    ) -> List[Subcontractor]:
        """Search for subcontractors"""
        db_query = self.db.query(Subcontractor).options(
            joinedload(Subcontractor.certifications)
        )
        
        if query:
            search_term = f"%{query}%"
            db_query = db_query.filter(
                or_(
                    Subcontractor.legal_name.ilike(search_term),
                    Subcontractor.certification_number.ilike(search_term)
                )
            )
        
        if is_mbe is not None:
            db_query = db_query.filter(Subcontractor.is_mbe == is_mbe)
        
        if organization_id:
            db_query = db_query.filter(Subcontractor.organization_id == organization_id)
        
        return db_query.all()
    
    def get_all_subcontractors(self, organization_id: Optional[UUID] = None) -> List[Subcontractor]:
        """Get all subcontractors"""
        query = self.db.query(Subcontractor).options(
            joinedload(Subcontractor.certifications)
        )
        
        if organization_id:
            query = query.filter(Subcontractor.organization_id == organization_id)
        
        return query.all()
    
    def update_subcontractor(
        self, 
        subcontractor_id: UUID, 
        update_data: dict
    ) -> Optional[Subcontractor]:
        """Update a subcontractor"""
        subcontractor = self.db.query(Subcontractor).filter(
            Subcontractor.id == subcontractor_id
        ).first()
        
        if not subcontractor:
            return None
        
        for key, value in update_data.items():
            if hasattr(subcontractor, key):
                setattr(subcontractor, key, value)
        
        self.db.commit()
        self.db.refresh(subcontractor)
        return subcontractor
    
    def delete_subcontractor(self, subcontractor_id: UUID) -> bool:
        """Delete a subcontractor"""
        subcontractor = self.db.query(Subcontractor).filter(
            Subcontractor.id == subcontractor_id
        ).first()
        
        if not subcontractor:
            return False
        
        self.db.delete(subcontractor)
        self.db.commit()
        return True