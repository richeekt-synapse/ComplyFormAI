from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import (
    Bid, 
    BidSubcontractor, 
    Subcontractor, 
    Certification, 
    NAICSCode,
    Opportunity,
    Jurisdiction,
    ComplianceRule
)
from decimal import Decimal
import json

class ValidationRule:
    """Base class for validation rules"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def validate(self, bid: Bid, db: Session) -> Dict:
        """Override this method in subclasses"""
        raise NotImplementedError


class CertificationExistsRule(ValidationRule):
    """Check if subcontractor certification exists"""
    
    def __init__(self):
        super().__init__(
            "certification_exists",
            "Verify subcontractor has valid certification"
        )
    
    def validate(self, bid: Bid, db: Session) -> Dict:
        errors = []
        
        for bid_sub in bid.bid_subcontractors:
            subcontractor = db.query(Subcontractor).filter(
                Subcontractor.id == bid_sub.subcontractor_id
            ).first()
            
            if not subcontractor:
                errors.append(f"Subcontractor not found: {bid_sub.subcontractor_id}")
                continue
            
            if bid_sub.counts_toward_mbe and not subcontractor.certification_number:
                errors.append(
                    f"{subcontractor.legal_name} is marked as MBE but has no certification number"
                )
        
        if errors:
            return {
                "status": "FAIL",
                "error_message": "; ".join(errors)
            }
        
        return {
            "status": "PASS",
            "error_message": "All subcontractors have valid certifications"
        }


class NAICSCodeValidRule(ValidationRule):
    """Check if NAICS codes are valid"""
    
    def __init__(self):
        super().__init__(
            "naics_code_valid",
            "Verify NAICS codes exist in database"
        )
    
    def validate(self, bid: Bid, db: Session) -> Dict:
        errors = []
        
        for bid_sub in bid.bid_subcontractors:
            naics_exists = db.query(NAICSCode).filter(
                NAICSCode.code == bid_sub.naics_code
            ).first()
            
            if not naics_exists:
                subcontractor = db.query(Subcontractor).filter(
                    Subcontractor.id == bid_sub.subcontractor_id
                ).first()
                errors.append(
                    f"Invalid NAICS code '{bid_sub.naics_code}' for {subcontractor.legal_name}"
                )
        
        if errors:
            return {
                "status": "FAIL",
                "error_message": "; ".join(errors)
            }
        
        return {
            "status": "PASS",
            "error_message": "All NAICS codes are valid"
        }


class JurisdictionComplianceRule(ValidationRule):
    """
    NEW: Check compliance with jurisdiction-specific rules from compliance_rules table
    This dynamically loads rules from the database based on the bid's jurisdiction
    """
    
    def __init__(self):
        super().__init__(
            "jurisdiction_compliance",
            "Verify compliance with jurisdiction-specific requirements"
        )
    
    def validate(self, bid: Bid, db: Session) -> Dict:
        # Get the jurisdiction for this bid
        # First, try to get it from an associated opportunity
        opportunity = db.query(Opportunity).filter(
            Opportunity.solicitation_number == bid.solicitation_number
        ).first()
        
        if not opportunity or not opportunity.jurisdiction_id:
            return {
                "status": "WARNING",
                "error_message": "Cannot verify jurisdiction-specific compliance: jurisdiction not identified"
            }
        
        # Get all compliance rules for this jurisdiction
        compliance_rules = db.query(ComplianceRule).filter(
            ComplianceRule.jurisdiction_id == opportunity.jurisdiction_id
        ).all()
        
        if not compliance_rules:
            return {
                "status": "WARNING",
                "error_message": "No compliance rules found for this jurisdiction"
            }
        
        errors = []
        warnings = []
        
        for rule in compliance_rules:
            result = self._check_rule(bid, rule, db)
            if result:
                if rule.severity == "ERROR":
                    errors.append(result)
                else:
                    warnings.append(result)
        
        if errors:
            return {
                "status": "FAIL",
                "error_message": "; ".join(errors)
            }
        elif warnings:
            return {
                "status": "WARNING",
                "error_message": "; ".join(warnings)
            }
        
        return {
            "status": "PASS",
            "error_message": "All jurisdiction-specific compliance rules satisfied"
        }
    
    def _check_rule(self, bid: Bid, rule: ComplianceRule, db: Session) -> str:
        """Check a specific compliance rule"""
        rule_def = rule.rule_definition
        
        if rule.rule_type == "MBE":
            return self._check_mbe_rule(bid, rule, rule_def)
        elif rule.rule_type == "VSBE":
            return self._check_vsbe_rule(bid, rule, rule_def)
        elif rule.rule_type == "LOCAL_PREF":
            return self._check_local_preference_rule(bid, rule, rule_def)
        elif rule.rule_type == "DBE":
            return self._check_dbe_rule(bid, rule, rule_def)
        
        return None
    
    def _check_mbe_rule(self, bid: Bid, rule: ComplianceRule, rule_def: dict) -> str:
        """Check MBE compliance rule"""
        threshold = Decimal(str(rule_def.get('threshold', 0)))
        
        if not bid.total_amount or bid.total_amount == 0:
            return None
        
        mbe_total = sum(
            float(bs.subcontract_value) 
            for bs in bid.bid_subcontractors 
            if bs.counts_toward_mbe
        )
        
        mbe_percentage = Decimal(str((mbe_total / float(bid.total_amount)) * 100))
        
        if mbe_percentage < threshold:
            return f"{rule.rule_name}: MBE participation {mbe_percentage:.2f}% is below required {threshold}%"
        
        return None
    
    def _check_vsbe_rule(self, bid: Bid, rule: ComplianceRule, rule_def: dict) -> str:
        """Check VSBE compliance rule"""
        threshold = Decimal(str(rule_def.get('threshold', 0)))
        
        if not bid.total_amount or bid.total_amount == 0:
            return None
        
        # Check if subcontractors have VSBE certification
        vsbe_total = Decimal('0')
        for bid_sub in bid.bid_subcontractors:
            subcontractor = bid_sub.subcontractor
            if subcontractor and subcontractor.certifications:
                for cert in subcontractor.certifications:
                    if cert.cert_type == "VSBE":
                        vsbe_total += bid_sub.subcontract_value
                        break
        
        vsbe_percentage = (vsbe_total / bid.total_amount) * 100
        
        if vsbe_percentage < threshold:
            return f"{rule.rule_name}: VSBE participation {vsbe_percentage:.2f}% is below required {threshold}%"
        
        return None
    
    def _check_local_preference_rule(self, bid: Bid, rule: ComplianceRule, rule_def: dict) -> str:
        """Check local preference rule"""
        # This would check if local businesses are given preference
        # Implementation depends on specific jurisdiction requirements
        return None
    
    def _check_dbe_rule(self, bid: Bid, rule: ComplianceRule, rule_def: dict) -> str:
        """Check DBE compliance rule"""
        threshold = Decimal(str(rule_def.get('threshold', 0)))
        
        if not bid.total_amount or bid.total_amount == 0:
            return None
        
        # Check if subcontractors have DBE certification
        dbe_total = Decimal('0')
        for bid_sub in bid.bid_subcontractors:
            subcontractor = bid_sub.subcontractor
            if subcontractor and subcontractor.certifications:
                for cert in subcontractor.certifications:
                    if cert.cert_type == "DBE":
                        dbe_total += bid_sub.subcontract_value
                        break
        
        dbe_percentage = (dbe_total / bid.total_amount) * 100
        
        if dbe_percentage < threshold:
            return f"{rule.rule_name}: DBE participation {dbe_percentage:.2f}% is below required {threshold}%"
        
        return None


class MBEPercentageRule(ValidationRule):
    """Check if MBE percentage meets goal"""
    
    def __init__(self):
        super().__init__(
            "mbe_percentage",
            "Verify MBE participation meets goal"
        )
    
    def validate(self, bid: Bid, db: Session) -> Dict:
        if not bid.total_amount or bid.total_amount == 0:
            return {
                "status": "WARNING",
                "error_message": "Cannot calculate MBE percentage: total amount is 0"
            }
        
        mbe_total = sum(
            float(bs.subcontract_value) 
            for bs in bid.bid_subcontractors 
            if bs.counts_toward_mbe
        )
        
        mbe_percentage = (mbe_total / float(bid.total_amount)) * 100
        
        if mbe_percentage < float(bid.mbe_goal):
            return {
                "status": "FAIL",
                "error_message": f"MBE percentage {mbe_percentage:.2f}% is below goal of {bid.mbe_goal}%"
            }
        
        return {
            "status": "PASS",
            "error_message": f"MBE percentage {mbe_percentage:.2f}% meets goal of {bid.mbe_goal}%"
        }


class SubcontractorNAICSMatchRule(ValidationRule):
    """Check if bid NAICS matches subcontractor certifications"""
    
    def __init__(self):
        super().__init__(
            "naics_match_certification",
            "Verify NAICS code matches subcontractor certification"
        )
    
    def validate(self, bid: Bid, db: Session) -> Dict:
        warnings = []
        
        for bid_sub in bid.bid_subcontractors:
            if not bid_sub.counts_toward_mbe:
                continue
            
            certifications = db.query(Certification).filter(
                Certification.subcontractor_id == bid_sub.subcontractor_id
            ).all()
            
            if not certifications:
                continue
            
            for cert in certifications:
                if cert.naics_codes and bid_sub.naics_code not in cert.naics_codes:
                    subcontractor = db.query(Subcontractor).filter(
                        Subcontractor.id == bid_sub.subcontractor_id
                    ).first()
                    warnings.append(
                        f"{subcontractor.legal_name}: NAICS {bid_sub.naics_code} not in certification"
                    )
        
        if warnings:
            return {
                "status": "WARNING",
                "error_message": "; ".join(warnings)
            }
        
        return {
            "status": "PASS",
            "error_message": "All NAICS codes match certifications"
        }


class JurisdictionSpecificGoalRule(ValidationRule):
    """
    NEW: Check if bid meets jurisdiction-specific MBE/VSBE goals
    Uses typical goals from jurisdictions table as fallback
    """
    
    def __init__(self):
        super().__init__(
            "jurisdiction_specific_goals",
            "Verify bid meets jurisdiction-specific MBE/VSBE goals"
        )
    
    def validate(self, bid: Bid, db: Session) -> Dict:
        # Get the jurisdiction
        opportunity = db.query(Opportunity).filter(
            Opportunity.solicitation_number == bid.solicitation_number
        ).first()
        
        if not opportunity or not opportunity.jurisdiction_id:
            return {
                "status": "WARNING",
                "error_message": "Cannot verify jurisdiction-specific goals: jurisdiction not identified"
            }
        
        jurisdiction = db.query(Jurisdiction).filter(
            Jurisdiction.id == opportunity.jurisdiction_id
        ).first()
        
        if not jurisdiction:
            return {
                "status": "WARNING",
                "error_message": "Jurisdiction not found"
            }
        
        errors = []
        
        # Check if bid's MBE goal matches jurisdiction's typical goal
        if jurisdiction.mbe_goal_typical:
            if not bid.mbe_goal or bid.mbe_goal < jurisdiction.mbe_goal_typical:
                errors.append(
                    f"Bid MBE goal ({bid.mbe_goal}%) is below {jurisdiction.name}'s "
                    f"typical requirement ({jurisdiction.mbe_goal_typical}%)"
                )
        
        # Check VSBE if applicable
        if opportunity.vsbe_goal and jurisdiction.vsbe_goal_typical:
            if opportunity.vsbe_goal < jurisdiction.vsbe_goal_typical:
                errors.append(
                    f"Opportunity VSBE goal ({opportunity.vsbe_goal}%) is below {jurisdiction.name}'s "
                    f"typical requirement ({jurisdiction.vsbe_goal_typical}%)"
                )
        
        if errors:
            return {
                "status": "WARNING",
                "error_message": "; ".join(errors)
            }
        
        return {
            "status": "PASS",
            "error_message": f"Bid meets {jurisdiction.name}'s typical goals"
        }


# List of all validation rules - NOW INCLUDING COMPLIANCE RULES
ALL_RULES = [
    CertificationExistsRule(),
    NAICSCodeValidRule(),
    MBEPercentageRule(),
    SubcontractorNAICSMatchRule(),
    JurisdictionComplianceRule(),        # NEW: Dynamic jurisdiction rules
    JurisdictionSpecificGoalRule(),      # NEW: Jurisdiction-specific goals
]