from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import Organization
from app.schemas.organization import Organization as OrgSchema, OrganizationCreate

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("/", response_model=OrgSchema, status_code=status.HTTP_201_CREATED)
def create_organization(
    organization: OrganizationCreate,
    db: Session = Depends(get_db)
):
    """Create a new organization"""
    org = Organization(**organization.model_dump())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

@router.get("/", response_model=List[OrgSchema])
def list_organizations(db: Session = Depends(get_db)):
    """List all organizations"""
    return db.query(Organization).all()

@router.get("/{organization_id}", response_model=OrgSchema)
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific organization"""
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {organization_id} not found"
        )
    
    return org