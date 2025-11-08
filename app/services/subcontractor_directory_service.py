from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, Boolean
from app.models import SubcontractorDirectory
from app.schemas.subcontractor_directory import (
    SubcontractorDirectoryCreate, 
    SubcontractorDirectoryUpdate,
    SubcontractorSearchFilters
)

class SubcontractorDirectoryService:
    """Service for subcontractor directory operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_subcontractor(
        self, 
        subcontractor_data: SubcontractorDirectoryCreate
    ) -> SubcontractorDirectory:
        """Add a subcontractor to the directory"""
        subcontractor = SubcontractorDirectory(**subcontractor_data.model_dump())
        self.db.add(subcontractor)
        self.db.commit()
        self.db.refresh(subcontractor)
        return subcontractor
    
    def get_subcontractor(
        self, 
        subcontractor_id: UUID
    ) -> Optional[SubcontractorDirectory]:
        """Get a subcontractor by ID"""
        return self.db.query(SubcontractorDirectory).filter(
            SubcontractorDirectory.id == subcontractor_id
        ).first()
    
    def search_subcontractors(
        self, 
        filters: SubcontractorSearchFilters
    ) -> List[SubcontractorDirectory]:
        """Search subcontractors with various filters"""
        query = self.db.query(SubcontractorDirectory)
        
        # Text search on name
        if filters.query:
            search_term = f"%{filters.query}%"
            query = query.filter(
                SubcontractorDirectory.legal_name.ilike(search_term)
            )
        
        # Filter by jurisdiction codes
        if filters.jurisdiction_codes:
            query = query.filter(
                SubcontractorDirectory.jurisdiction_codes.overlap(filters.jurisdiction_codes)
            )
        
        # Filter by NAICS codes
        if filters.naics_codes:
            query = query.filter(
                SubcontractorDirectory.naics_codes.overlap(filters.naics_codes)
            )
        
        # Filter by MBE certification
        if filters.is_mbe is not None:
            if filters.is_mbe:
                query = query.filter(
                    SubcontractorDirectory.certifications['mbe'].astext.cast(
                        type_=type(True)
                    ) == True
                )
            else:
                query = query.filter(
                    or_(
                        SubcontractorDirectory.certifications['mbe'].astext.cast(
                            type_=type(False)
                        ) == False,
                        SubcontractorDirectory.certifications['mbe'].is_(None)
                    )
                )
        
        # Filter by VSBE certification
        if filters.is_vsbe is not None:
            if filters.is_vsbe:
                query = query.filter(
                    SubcontractorDirectory.certifications['vsbe'].astext.cast(
                        type_=type(True)
                    ) == True
                )
        
        # Filter by verified status
        if filters.is_verified is not None:
            query = query.filter(
                SubcontractorDirectory.is_verified == filters.is_verified
            )
        
        # Filter by minimum rating
        if filters.min_rating is not None:
            query = query.filter(
                SubcontractorDirectory.rating >= filters.min_rating
            )
        
        # Order by rating and projects completed
        query = query.order_by(
            SubcontractorDirectory.rating.desc(),
            SubcontractorDirectory.projects_completed.desc()
        )
        
        return query.all()
    
    def get_all_subcontractors(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[SubcontractorDirectory]:
        """Get all subcontractors with pagination"""
        return self.db.query(SubcontractorDirectory).offset(skip).limit(limit).all()
    
    def update_subcontractor(
        self, 
        subcontractor_id: UUID, 
        update_data: SubcontractorDirectoryUpdate
    ) -> Optional[SubcontractorDirectory]:
        """Update a subcontractor in the directory"""
        subcontractor = self.get_subcontractor(subcontractor_id)
        
        if not subcontractor:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(subcontractor, key):
                setattr(subcontractor, key, value)
        
        self.db.commit()
        self.db.refresh(subcontractor)
        return subcontractor
    
    def delete_subcontractor(self, subcontractor_id: UUID) -> bool:
        """Delete a subcontractor from the directory"""
        subcontractor = self.get_subcontractor(subcontractor_id)
        
        if not subcontractor:
            return False
        
        self.db.delete(subcontractor)
        self.db.commit()
        return True
    
    def get_matching_subcontractors(
        self,
        naics_codes: List[str],
        jurisdiction_code: str,
        is_mbe: bool = False,
        is_vsbe: bool = False,
        min_rating: float = 0.0
    ) -> List[SubcontractorDirectory]:
        """Find subcontractors matching specific criteria for an opportunity"""
        query = self.db.query(SubcontractorDirectory)

        # Match NAICS codes
        if naics_codes:
            query = query.filter(
                SubcontractorDirectory.naics_codes.overlap(naics_codes)
            )

        # Match jurisdiction
        query = query.filter(
            SubcontractorDirectory.jurisdiction_codes.contains([jurisdiction_code])
        )

        # Match certifications
        if is_mbe:
            query = query.filter(
                SubcontractorDirectory.certifications['mbe'].astext.cast(Boolean) == True
            )

        if is_vsbe:
            query = query.filter(
                SubcontractorDirectory.certifications['vsbe'].astext.cast(Boolean) == True
            )

        # Filter by rating
        query = query.filter(SubcontractorDirectory.rating >= min_rating)

        # Order by rating
        query = query.order_by(SubcontractorDirectory.rating.desc())

        return query.all()

    def calculate_contractor_usage_count(self, subcontractor_id: UUID) -> int:
        """Calculate how many unique contractors have used this subcontractor"""
        from app.models import SubcontractorOutreach

        count = self.db.query(func.count(func.distinct(SubcontractorOutreach.organization_id)))\
            .filter(SubcontractorOutreach.subcontractor_id == subcontractor_id)\
            .scalar()

        return count or 0

    def update_contractor_usage_count(self, subcontractor_id: UUID) -> Optional[SubcontractorDirectory]:
        """Update the cached contractor usage count for a subcontractor"""
        subcontractor = self.get_subcontractor(subcontractor_id)

        if not subcontractor:
            return None

        count = self.calculate_contractor_usage_count(subcontractor_id)
        subcontractor.contractors_using_count = count

        self.db.commit()
        self.db.refresh(subcontractor)
        return subcontractor

    def update_all_contractor_usage_counts(self) -> int:
        """Update contractor usage counts for all subcontractors in the directory"""
        from app.models import SubcontractorOutreach

        # Get all subcontractors
        all_subs = self.db.query(SubcontractorDirectory).all()
        updated_count = 0

        for sub in all_subs:
            count = self.calculate_contractor_usage_count(sub.id)
            sub.contractors_using_count = count
            updated_count += 1

        self.db.commit()
        return updated_count