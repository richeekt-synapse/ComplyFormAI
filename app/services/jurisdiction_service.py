from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import Jurisdiction
from app.schemas.jurisdiction import JurisdictionCreate

class JurisdictionService:
    """Service for jurisdiction operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_jurisdiction(self, jurisdiction_data: JurisdictionCreate) -> Jurisdiction:
        """Create a new jurisdiction"""
        jurisdiction = Jurisdiction(**jurisdiction_data.model_dump())
        self.db.add(jurisdiction)
        self.db.commit()
        self.db.refresh(jurisdiction)
        return jurisdiction
    
    def get_jurisdiction(self, jurisdiction_id: UUID) -> Optional[Jurisdiction]:
        """Get a jurisdiction by ID"""
        return self.db.query(Jurisdiction).filter(
            Jurisdiction.id == jurisdiction_id
        ).first()
    
    def get_jurisdiction_by_code(self, code: str) -> Optional[Jurisdiction]:
        """Get a jurisdiction by code"""
        return self.db.query(Jurisdiction).filter(
            Jurisdiction.code == code
        ).first()
    
    def get_all_jurisdictions(self) -> List[Jurisdiction]:
        """Get all jurisdictions"""
        return self.db.query(Jurisdiction).all()
    
    def update_jurisdiction(
        self, 
        jurisdiction_id: UUID, 
        update_data: dict
    ) -> Optional[Jurisdiction]:
        """Update a jurisdiction"""
        jurisdiction = self.get_jurisdiction(jurisdiction_id)
        
        if not jurisdiction:
            return None
        
        for key, value in update_data.items():
            if hasattr(jurisdiction, key):
                setattr(jurisdiction, key, value)
        
        self.db.commit()
        self.db.refresh(jurisdiction)
        return jurisdiction