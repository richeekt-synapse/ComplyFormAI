from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import ValidationResult
from app.validation import ValidationEngine
from app.schemas.validation import ValidationResponse

class ValidationService:
    """Service for validation operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.engine = ValidationEngine(db)
    
    def validate_bid(self, bid_id: UUID) -> ValidationResponse:
        """Validate a bid and return results"""
        
        # Run validation
        results = self.engine.validate_bid(bid_id)
        
        # Calculate statistics
        total = len(results)
        passed = sum(1 for r in results if r.status == "PASS")
        failed = sum(1 for r in results if r.status == "FAIL")
        warnings = sum(1 for r in results if r.status == "WARNING")
        
        # Determine overall status
        if failed > 0:
            overall_status = "FAIL"
        elif warnings > 0:
            overall_status = "WARNING"
        else:
            overall_status = "PASS"
        
        return ValidationResponse(
            bid_id=bid_id,
            overall_status=overall_status,
            total_validations=total,
            passed=passed,
            failed=failed,
            warnings=warnings,
            validations=results
        )
    
    def get_validation_results(self, bid_id: UUID) -> List[ValidationResult]:
        """Get validation results for a bid"""
        return self.db.query(ValidationResult).filter(
            ValidationResult.bid_id == bid_id
        ).order_by(ValidationResult.created_at.desc()).all()