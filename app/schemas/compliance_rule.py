from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.models import ComplianceRule, Jurisdiction
from app.schemas.compliance_rule import ComplianceRuleCreate, ComplianceRuleUpdate

class ComplianceRuleService:
    """Service for managing jurisdiction-specific compliance rules"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_rule(self, rule_data: ComplianceRuleCreate) -> ComplianceRule:
        """Create a new compliance rule"""
        rule = ComplianceRule(**rule_data.model_dump())
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def get_rule(self, rule_id: UUID) -> Optional[ComplianceRule]:
        """Get a compliance rule by ID"""
        return self.db.query(ComplianceRule).options(
            joinedload(ComplianceRule.jurisdiction)
        ).filter(ComplianceRule.id == rule_id).first()
    
    def get_rules_by_jurisdiction(
        self, 
        jurisdiction_id: UUID
    ) -> List[ComplianceRule]:
        """Get all compliance rules for a specific jurisdiction"""
        return self.db.query(ComplianceRule).options(
            joinedload(ComplianceRule.jurisdiction)
        ).filter(
            ComplianceRule.jurisdiction_id == jurisdiction_id
        ).all()
    
    def get_rules_by_jurisdiction_code(
        self, 
        jurisdiction_code: str
    ) -> List[ComplianceRule]:
        """Get all compliance rules for a jurisdiction by code (e.g., 'MD', 'DC')"""
        jurisdiction = self.db.query(Jurisdiction).filter(
            Jurisdiction.code == jurisdiction_code
        ).first()
        
        if not jurisdiction:
            return []
        
        return self.get_rules_by_jurisdiction(jurisdiction.id)
    
    def get_rules_by_type(
        self,
        rule_type: str,
        jurisdiction_id: Optional[UUID] = None
    ) -> List[ComplianceRule]:
        """
        Get compliance rules by type (MBE, VSBE, DBE, LOCAL_PREF, etc.)
        Optionally filter by jurisdiction
        """
        query = self.db.query(ComplianceRule).options(
            joinedload(ComplianceRule.jurisdiction)
        ).filter(ComplianceRule.rule_type == rule_type)
        
        if jurisdiction_id:
            query = query.filter(ComplianceRule.jurisdiction_id == jurisdiction_id)
        
        return query.all()
    
    def get_all_rules(self) -> List[ComplianceRule]:
        """Get all compliance rules"""
        return self.db.query(ComplianceRule).options(
            joinedload(ComplianceRule.jurisdiction)
        ).all()
    
    def update_rule(
        self, 
        rule_id: UUID, 
        update_data: ComplianceRuleUpdate
    ) -> Optional[ComplianceRule]:
        """Update a compliance rule"""
        rule = self.get_rule(rule_id)
        
        if not rule:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def delete_rule(self, rule_id: UUID) -> bool:
        """Delete a compliance rule"""
        rule = self.get_rule(rule_id)
        
        if not rule:
            return False
        
        self.db.delete(rule)
        self.db.commit()
        return True
    
    def get_applicable_rules(
        self,
        jurisdiction_id: UUID,
        rule_types: Optional[List[str]] = None
    ) -> List[ComplianceRule]:
        """
        Get applicable compliance rules for a bid
        Can filter by rule types (e.g., ['MBE', 'VSBE'])
        """
        query = self.db.query(ComplianceRule).options(
            joinedload(ComplianceRule.jurisdiction)
        ).filter(ComplianceRule.jurisdiction_id == jurisdiction_id)
        
        if rule_types:
            query = query.filter(ComplianceRule.rule_type.in_(rule_types))
        
        return query.all()