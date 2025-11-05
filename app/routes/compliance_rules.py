from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas.compliance_rule import (
    ComplianceRule,
    ComplianceRuleCreate,
    ComplianceRuleUpdate,
    ComplianceRuleDetail
)
from app.services.compliance_rule_service import ComplianceRuleService

router = APIRouter(prefix="/compliance-rules", tags=["compliance-rules"])

@router.post("/", response_model=ComplianceRule, status_code=status.HTTP_201_CREATED)
def create_compliance_rule(
    rule: ComplianceRuleCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new compliance rule for a jurisdiction
    
    Rule types:
    - MBE: Minority Business Enterprise requirements
    - VSBE: Very Small Business Enterprise requirements
    - DBE: Disadvantaged Business Enterprise requirements
    - LOCAL_PREF: Local business preference requirements
    
    Severity levels:
    - ERROR: Must be met (validation fails)
    - WARNING: Should be met (validation warns but doesn't fail)
    
    Example rule_definition:
    {
        "threshold": 29.0,
        "description": "MBE participation must meet or exceed 29% of total contract value"
    }
    """
    service = ComplianceRuleService(db)
    return service.create_rule(rule)

@router.get("/", response_model=List[ComplianceRuleDetail])
def list_compliance_rules(db: Session = Depends(get_db)):
    """List all compliance rules"""
    service = ComplianceRuleService(db)
    return service.get_all_rules()

@router.get("/{rule_id}", response_model=ComplianceRuleDetail)
def get_compliance_rule(
    rule_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific compliance rule"""
    service = ComplianceRuleService(db)
    rule = service.get_rule(rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compliance rule {rule_id} not found"
        )
    
    return rule

@router.get("/jurisdiction/{jurisdiction_id}", response_model=List[ComplianceRuleDetail])
def get_rules_by_jurisdiction(
    jurisdiction_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all compliance rules for a specific jurisdiction"""
    service = ComplianceRuleService(db)
    return service.get_rules_by_jurisdiction(jurisdiction_id)

@router.get("/jurisdiction/code/{jurisdiction_code}", response_model=List[ComplianceRuleDetail])
def get_rules_by_jurisdiction_code(
    jurisdiction_code: str,
    db: Session = Depends(get_db)
):
    """
    Get all compliance rules for a jurisdiction by code
    
    Examples:
    - MD (Maryland)
    - DC (District of Columbia)
    """
    service = ComplianceRuleService(db)
    rules = service.get_rules_by_jurisdiction_code(jurisdiction_code)
    
    if not rules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No compliance rules found for jurisdiction '{jurisdiction_code}'"
        )
    
    return rules

@router.get("/type/{rule_type}", response_model=List[ComplianceRuleDetail])
def get_rules_by_type(
    rule_type: str,
    jurisdiction_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get compliance rules by type
    
    Rule types:
    - MBE
    - VSBE
    - DBE
    - LOCAL_PREF
    
    Optionally filter by jurisdiction
    """
    service = ComplianceRuleService(db)
    return service.get_rules_by_type(rule_type, jurisdiction_id)

@router.put("/{rule_id}", response_model=ComplianceRule)
def update_compliance_rule(
    rule_id: UUID,
    update_data: ComplianceRuleUpdate,
    db: Session = Depends(get_db)
):
    """Update a compliance rule"""
    service = ComplianceRuleService(db)
    rule = service.update_rule(rule_id, update_data)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compliance rule {rule_id} not found"
        )
    
    return rule

@router.delete("/{rule_id}")
def delete_compliance_rule(
    rule_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a compliance rule"""
    service = ComplianceRuleService(db)
    success = service.delete_rule(rule_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compliance rule {rule_id} not found"
        )
    
    return {"message": "Compliance rule deleted successfully"}

@router.get("/applicable/{jurisdiction_id}", response_model=List[ComplianceRuleDetail])
def get_applicable_rules(
    jurisdiction_id: UUID,
    rule_types: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get applicable compliance rules for a bid in a specific jurisdiction
    
    This is used by the validation engine to determine which rules to check
    
    Optional filter by rule types (e.g., ['MBE', 'VSBE'])
    """
    service = ComplianceRuleService(db)
    return service.get_applicable_rules(jurisdiction_id, rule_types)