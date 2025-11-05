from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from decimal import Decimal
from app.models import (
    PreBidAssessment, 
    Opportunity, 
    Jurisdiction,
    SubcontractorDirectory
)
from app.schemas.pre_bid_assessment import PreBidAssessmentCreate, AssessmentRequest
from app.services.subcontractor_directory_service import SubcontractorDirectoryService

class PreBidAssessmentService:
    """Service for pre-bid assessment operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.subcontractor_service = SubcontractorDirectoryService(db)
    
    def create_assessment(
        self, 
        assessment_data: PreBidAssessmentCreate
    ) -> PreBidAssessment:
        """Create a new pre-bid assessment"""
        assessment = PreBidAssessment(**assessment_data.model_dump())
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment
    
    def get_assessment(
        self, 
        assessment_id: UUID
    ) -> Optional[PreBidAssessment]:
        """Get an assessment by ID"""
        return self.db.query(PreBidAssessment).options(
            joinedload(PreBidAssessment.opportunity).joinedload(Opportunity.jurisdiction)
        ).filter(PreBidAssessment.id == assessment_id).first()
    
    def get_assessments_by_organization(
        self, 
        organization_id: UUID
    ) -> List[PreBidAssessment]:
        """Get all assessments for an organization"""
        return self.db.query(PreBidAssessment).options(
            joinedload(PreBidAssessment.opportunity).joinedload(Opportunity.jurisdiction)
        ).filter(
            PreBidAssessment.organization_id == organization_id
        ).order_by(PreBidAssessment.assessed_at.desc()).all()
    
    def perform_assessment(
        self, 
        request: AssessmentRequest
    ) -> Dict:
        """
        Perform a comprehensive pre-bid assessment
        Returns assessment data with risk score, gaps, and recommendations
        """
        # Get the opportunity
        opportunity = self.db.query(Opportunity).options(
            joinedload(Opportunity.jurisdiction)
        ).filter(Opportunity.id == request.opportunity_id).first()
        
        if not opportunity:
            raise ValueError("Opportunity not found")
        
        # Get jurisdiction
        jurisdiction = opportunity.jurisdiction
        
        # Initialize assessment data
        assessment_data = {
            "organization_id": request.organization_id,
            "opportunity_id": request.opportunity_id,
            "overall_risk_score": 0,
            "mbe_gap_percentage": Decimal('0.0'),
            "vsbe_gap_percentage": Decimal('0.0'),
            "available_subcontractors_count": 0,
            "recommendation": "BID",
            "recommendation_reason": "",
            "risk_factors": [],
            "matching_subcontractors": []
        }
        
        risk_score = 0
        risk_factors = []
        
        # 1. Find available subcontractors
        matching_subs_mbe = []
        matching_subs_vsbe = []
        
        if opportunity.naics_codes and jurisdiction:
            # Find MBE subcontractors
            if opportunity.mbe_goal and opportunity.mbe_goal > 0:
                matching_subs_mbe = self.subcontractor_service.get_matching_subcontractors(
                    naics_codes=opportunity.naics_codes,
                    jurisdiction_code=jurisdiction.code,
                    is_mbe=True,
                    min_rating=2.0
                )
            
            # Find VSBE subcontractors
            if opportunity.vsbe_goal and opportunity.vsbe_goal > 0:
                matching_subs_vsbe = self.subcontractor_service.get_matching_subcontractors(
                    naics_codes=opportunity.naics_codes,
                    jurisdiction_code=jurisdiction.code,
                    is_vsbe=True,
                    min_rating=2.0
                )
        
        total_matching = len(set([s.id for s in matching_subs_mbe + matching_subs_vsbe]))
        assessment_data["available_subcontractors_count"] = total_matching
        assessment_data["matching_subcontractors"] = matching_subs_mbe[:10]  # Top 10
        
        # 2. Calculate MBE gap
        if opportunity.mbe_goal and opportunity.mbe_goal > 0:
            if len(matching_subs_mbe) == 0:
                assessment_data["mbe_gap_percentage"] = -opportunity.mbe_goal
                risk_score += 40
                risk_factors.append(
                    f"CRITICAL: No MBE subcontractors found. Need {opportunity.mbe_goal}% participation."
                )
            elif len(matching_subs_mbe) < 3:
                assessment_data["mbe_gap_percentage"] = Decimal('-10.0')
                risk_score += 25
                risk_factors.append(
                    f"WARNING: Only {len(matching_subs_mbe)} MBE subcontractors available. "
                    f"Limited options to meet {opportunity.mbe_goal}% goal."
                )
            else:
                assessment_data["mbe_gap_percentage"] = Decimal('0.0')
                risk_factors.append(
                    f"GOOD: {len(matching_subs_mbe)} MBE subcontractors available "
                    f"to meet {opportunity.mbe_goal}% goal."
                )
        
        # 3. Calculate VSBE gap
        if opportunity.vsbe_goal and opportunity.vsbe_goal > 0:
            if len(matching_subs_vsbe) == 0:
                assessment_data["vsbe_gap_percentage"] = -opportunity.vsbe_goal
                risk_score += 20
                risk_factors.append(
                    f"WARNING: No VSBE subcontractors found. Need {opportunity.vsbe_goal}% participation."
                )
            elif len(matching_subs_vsbe) < 2:
                assessment_data["vsbe_gap_percentage"] = Decimal('-5.0')
                risk_score += 10
                risk_factors.append(
                    f"CAUTION: Only {len(matching_subs_vsbe)} VSBE subcontractors available."
                )
            else:
                assessment_data["vsbe_gap_percentage"] = Decimal('0.0')
        
        # 4. Check opportunity value
        if opportunity.total_value:
            if opportunity.total_value > 10000000:  # $10M+
                risk_score += 15
                risk_factors.append(
                    "CAUTION: High-value contract ($10M+) requires strong team and capacity."
                )
            elif opportunity.total_value < 100000:  # Under $100k
                risk_factors.append(
                    "INFO: Small contract value may have lower margins."
                )
        
        # 5. Check due date
        if opportunity.due_date:
            from datetime import date, timedelta
            days_until_due = (opportunity.due_date - date.today()).days
            
            if days_until_due < 7:
                risk_score += 30
                risk_factors.append(
                    f"CRITICAL: Only {days_until_due} days until due date. Very tight timeline."
                )
            elif days_until_due < 14:
                risk_score += 15
                risk_factors.append(
                    f"WARNING: Only {days_until_due} days until due date. Limited prep time."
                )
            else:
                risk_factors.append(
                    f"GOOD: {days_until_due} days until due date. Adequate preparation time."
                )
        
        # 6. Calculate overall risk score (0-100, higher = more risk)
        assessment_data["overall_risk_score"] = min(risk_score, 100)
        assessment_data["risk_factors"] = risk_factors
        
        # 7. Generate recommendation
        if risk_score >= 60:
            assessment_data["recommendation"] = "NO_BID"
            assessment_data["recommendation_reason"] = (
                "HIGH RISK: Significant compliance gaps or timing constraints. "
                "Recommend passing on this opportunity."
            )
        elif risk_score >= 30:
            assessment_data["recommendation"] = "CAUTION"
            assessment_data["recommendation_reason"] = (
                "MODERATE RISK: Some concerns identified. "
                "Proceed with careful planning and strong subcontractor commitments."
            )
        else:
            assessment_data["recommendation"] = "BID"
            assessment_data["recommendation_reason"] = (
                "LOW RISK: Good subcontractor availability and reasonable timeline. "
                "Strong opportunity to pursue."
            )
        
        # 8. Save the assessment
        assessment = PreBidAssessment(
            organization_id=assessment_data["organization_id"],
            opportunity_id=assessment_data["opportunity_id"],
            overall_risk_score=assessment_data["overall_risk_score"],
            mbe_gap_percentage=assessment_data["mbe_gap_percentage"],
            vsbe_gap_percentage=assessment_data["vsbe_gap_percentage"],
            available_subcontractors_count=assessment_data["available_subcontractors_count"],
            recommendation=assessment_data["recommendation"],
            recommendation_reason=assessment_data["recommendation_reason"]
        )
        
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        
        # Return full assessment data including transient fields
        return {
            **assessment_data,
            "id": assessment.id,
            "assessed_at": assessment.assessed_at,
            "opportunity": opportunity
        }
    
    def get_assessment_summary_by_organization(
        self, 
        organization_id: UUID
    ) -> Dict:
        """Get summary statistics of assessments for an organization"""
        assessments = self.get_assessments_by_organization(organization_id)
        
        total = len(assessments)
        bid_count = sum(1 for a in assessments if a.recommendation == "BID")
        caution_count = sum(1 for a in assessments if a.recommendation == "CAUTION")
        no_bid_count = sum(1 for a in assessments if a.recommendation == "NO_BID")
        
        avg_risk_score = sum(a.overall_risk_score or 0 for a in assessments) / total if total > 0 else 0
        
        return {
            "total_assessments": total,
            "bid_recommended": bid_count,
            "caution_recommended": caution_count,
            "no_bid_recommended": no_bid_count,
            "average_risk_score": round(avg_risk_score, 2)
        }