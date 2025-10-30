from typing import List
from sqlalchemy.orm import Session
from app.models import Bid, ValidationResult
from app.validation.rules import ALL_RULES
from uuid import UUID

class ValidationEngine:
    """Engine to run all validation rules on a bid"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_bid(self, bid_id: UUID) -> List[ValidationResult]:
        """Run all validation rules on a bid"""
        
        # Get the bid with all relationships
        bid = self.db.query(Bid).filter(Bid.id == bid_id).first()
        
        if not bid:
            raise ValueError(f"Bid {bid_id} not found")
        
        # Clear previous validation results
        self.db.query(ValidationResult).filter(
            ValidationResult.bid_id == bid_id
        ).delete()
        
        results = []
        
        # Run each validation rule
        for rule in ALL_RULES:
            result_data = rule.validate(bid, self.db)
            
            validation_result = ValidationResult(
                bid_id=bid_id,
                rule_name=rule.name,
                status=result_data["status"],
                error_message=result_data["error_message"]
            )
            
            self.db.add(validation_result)
            results.append(validation_result)
        
        self.db.commit()
        
        # Refresh to get created_at timestamps
        for result in results:
            self.db.refresh(result)
        
        return results