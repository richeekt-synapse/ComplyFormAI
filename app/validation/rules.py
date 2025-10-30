from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import Bid, BidSubcontractor, Subcontractor, Certification, NAICSCode
from decimal import Decimal

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

# List of all validation rules
ALL_RULES = [
    CertificationExistsRule(),
    NAICSCodeValidRule(),
    MBEPercentageRule(),
    SubcontractorNAICSMatchRule()
]