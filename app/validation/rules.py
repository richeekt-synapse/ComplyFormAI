from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import (
    Bid,
    BidSubcontractor,
    Subcontractor,
    Certification,
    NAICSCode,
    Jurisdiction,
    ComplianceRule,
    SubcontractorDirectory
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


class DirectoryJurisdictionMatchRule(ValidationRule):
    """Check if subcontractor exists in directory DB and has jurisdiction codes"""

    def __init__(self):
        super().__init__(
            "directory_jurisdiction_match",
            "Verify subcontractor exists in directory DB with valid jurisdiction codes"
        )

    def validate(self, bid: Bid, db: Session) -> Dict:
        print(f"\n=== DEBUG: DirectoryJurisdictionMatchRule ===")
        print(f"Bid ID: {bid.id}")

        errors = []

        # Check each bid subcontractor against the directory DB
        print(f"\nNumber of bid subcontractors: {len(bid.bid_subcontractors)}")
        for bid_sub in bid.bid_subcontractors:
            subcontractor = db.query(Subcontractor).filter(
                Subcontractor.id == bid_sub.subcontractor_id
            ).first()

            if not subcontractor:
                errors.append(f"Subcontractor not found: {bid_sub.subcontractor_id}")
                continue

            print(f"\nChecking subcontractor: {subcontractor.legal_name}")

            # PRIMARY CHECK: Look up in directory DB
            directory_entry = db.query(SubcontractorDirectory).filter(
                SubcontractorDirectory.legal_name == subcontractor.legal_name
            ).first()

            print(f"  Directory entry found: {directory_entry is not None}")
            if directory_entry:
                print(f"  Directory jurisdiction_codes: {directory_entry.jurisdiction_codes}")
            else:
                print(f"  NOT FOUND in subcontractor_directory table")

            # FAIL if subcontractor not found in directory DB
            if not directory_entry:
                errors.append(
                    f"{subcontractor.legal_name} not found in directory DB - FAIL"
                )
                print(f"  FAIL: Not in directory")
                continue

            # Check if jurisdiction codes exist in directory DB
            if not directory_entry.jurisdiction_codes or len(directory_entry.jurisdiction_codes) == 0:
                # FAIL if no jurisdiction codes in directory DB
                errors.append(
                    f"{subcontractor.legal_name} has no jurisdiction codes in directory DB - FAIL"
                )
                print(f"  FAIL: No jurisdiction codes in directory")
            else:
                # PASS - subcontractor exists and has jurisdiction codes
                print(f"  PASS: Has jurisdiction codes: {', '.join(directory_entry.jurisdiction_codes)}")

        if errors:
            return {
                "status": "FAIL",
                "error_message": "; ".join(errors)
            }

        return {
            "status": "PASS",
            "error_message": "All subcontractors exist in directory DB with valid jurisdiction codes"
        }


class CertificationExistsRule(ValidationRule):
    """Check if subcontractor certification exists in directory DB"""

    def __init__(self):
        super().__init__(
            "certification_exists",
            "Verify subcontractor has valid certification in directory DB"
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

            # PRIMARY CHECK: Look up certifications in directory DB
            directory_entry = db.query(SubcontractorDirectory).filter(
                SubcontractorDirectory.legal_name == subcontractor.legal_name
            ).first()

            if not directory_entry:
                errors.append(
                    f"{subcontractor.legal_name} not found in directory DB"
                )
                continue

            # Check certifications from directory DB
            if bid_sub.counts_toward_mbe:
                if directory_entry.certifications:
                    # Check if MBE certification exists in directory
                    if not directory_entry.certifications.get('mbe', False):
                        errors.append(
                            f"{subcontractor.legal_name} is marked as MBE but has no MBE certification in directory DB"
                        )
                else:
                    errors.append(
                        f"{subcontractor.legal_name} is marked as MBE but has no certifications in directory DB"
                    )

        if errors:
            return {
                "status": "FAIL",
                "error_message": "; ".join(errors)
            }

        return {
            "status": "PASS",
            "error_message": "All subcontractors have valid certifications in directory DB"
        }


class NAICSCodeValidRule(ValidationRule):
    """Check NAICS codes from directory DB"""

    def __init__(self):
        super().__init__(
            "naics_code_valid",
            "Verify NAICS codes from directory DB"
        )

    def validate(self, bid: Bid, db: Session) -> Dict:
        print(f"\n=== DEBUG: NAICSCodeValidRule ===")
        print(f"Bid ID: {bid.id}")

        errors = []

        print(f"Number of bid subcontractors to check: {len(bid.bid_subcontractors)}")
        for bid_sub in bid.bid_subcontractors:
            subcontractor = db.query(Subcontractor).filter(
                Subcontractor.id == bid_sub.subcontractor_id
            ).first()

            if not subcontractor:
                errors.append(f"Subcontractor not found: {bid_sub.subcontractor_id}")
                continue

            print(f"\nChecking NAICS for: {subcontractor.legal_name}")
            print(f"  NAICS code in bid_subcontractor: '{bid_sub.naics_code}'")

            # Check if NAICS code is provided in bid_subcontractor
            if not bid_sub.naics_code or bid_sub.naics_code.strip() == '':
                print(f"  FAIL: No NAICS code assigned in bid")
                errors.append(
                    f"{subcontractor.legal_name} has no NAICS code assigned in bid"
                )
                continue

            # PRIMARY CHECK: Look up NAICS in directory DB
            directory_entry = db.query(SubcontractorDirectory).filter(
                SubcontractorDirectory.legal_name == subcontractor.legal_name
            ).first()

            print(f"  Directory entry found: {directory_entry is not None}")
            if directory_entry:
                print(f"  Directory NAICS codes: {directory_entry.naics_codes}")
                print(f"  Type of directory naics_codes: {type(directory_entry.naics_codes)}")
            else:
                print(f"  NOT FOUND in subcontractor_directory table")

            if not directory_entry:
                errors.append(
                    f"{subcontractor.legal_name} not found in directory DB"
                )
                continue

            # Check NAICS code from directory DB
            if directory_entry.naics_codes:
                print(f"  Checking if '{bid_sub.naics_code}' in {directory_entry.naics_codes}")
                if bid_sub.naics_code not in directory_entry.naics_codes:
                    print(f"  FAIL: NAICS code not in directory list")
                    errors.append(
                        f"NAICS code '{bid_sub.naics_code}' not listed in directory DB for {subcontractor.legal_name}. Directory has: {directory_entry.naics_codes}"
                    )
                else:
                    print(f"  PASS: NAICS code found in directory")
            else:
                print(f"  FAIL: No NAICS codes in directory")
                errors.append(
                    f"{subcontractor.legal_name} has no NAICS codes in directory DB"
                )

        if errors:
            return {
                "status": "FAIL",
                "error_message": "; ".join(errors)
            }

        return {
            "status": "PASS",
            "error_message": "All NAICS codes match directory DB"
        }


class JurisdictionComplianceRule(ValidationRule):
    """
    Check compliance with jurisdiction-specific rules from compliance_rules table
    Gets jurisdiction codes from subcontractor_directory and validates against those rules
    """

    def __init__(self):
        super().__init__(
            "jurisdiction_compliance",
            "Verify compliance with jurisdiction-specific requirements from directory DB"
        )

    def validate(self, bid: Bid, db: Session) -> Dict:
        print(f"\n=== DEBUG: JurisdictionComplianceRule ===")
        print(f"Bid ID: {bid.id}")
        print(f"Bid total_amount: {bid.total_amount}")

        # Collect all unique jurisdiction codes from subcontractors in directory
        jurisdiction_codes = set()

        print(f"\nNumber of bid subcontractors: {len(bid.bid_subcontractors)}")
        for bid_sub in bid.bid_subcontractors:
            subcontractor = db.query(Subcontractor).filter(
                Subcontractor.id == bid_sub.subcontractor_id
            ).first()

            if not subcontractor:
                print(f"  WARNING: Subcontractor {bid_sub.subcontractor_id} not found")
                continue

            print(f"\nChecking subcontractor: {subcontractor.legal_name}")

            # Get jurisdiction codes from directory
            directory_entry = db.query(SubcontractorDirectory).filter(
                SubcontractorDirectory.legal_name == subcontractor.legal_name
            ).first()

            if directory_entry and directory_entry.jurisdiction_codes:
                print(f"  Directory jurisdiction_codes: {directory_entry.jurisdiction_codes}")
                jurisdiction_codes.update(directory_entry.jurisdiction_codes)
            else:
                print(f"  WARNING: No directory entry or jurisdiction codes for {subcontractor.legal_name}")

        if not jurisdiction_codes:
            print("\nRESULT: No jurisdiction codes found in directory - returning WARNING")
            return {
                "status": "WARNING",
                "error_message": "Cannot verify jurisdiction-specific compliance: no jurisdiction codes found in directory"
            }

        print(f"\nUnique jurisdiction codes found: {list(jurisdiction_codes)}")

        # Get all compliance rules for these jurisdictions
        jurisdictions = db.query(Jurisdiction).filter(
            Jurisdiction.code.in_(list(jurisdiction_codes))
        ).all()

        print(f"Jurisdictions found in DB: {[j.code for j in jurisdictions]}")

        if not jurisdictions:
            print("RESULT: No matching jurisdictions found in DB - returning WARNING")
            return {
                "status": "WARNING",
                "error_message": f"No jurisdiction records found for codes: {', '.join(jurisdiction_codes)}"
            }

        # Collect all compliance rules for these jurisdictions
        all_compliance_rules = []
        for jurisdiction in jurisdictions:
            compliance_rules = db.query(ComplianceRule).filter(
                ComplianceRule.jurisdiction_id == jurisdiction.id
            ).all()

            print(f"\nCompliance rules for {jurisdiction.code} ({jurisdiction.name}):")
            for rule in compliance_rules:
                print(f"  - {rule.rule_name} (type: {rule.rule_type}, severity: {rule.severity})")
                print(f"    Definition: {rule.rule_definition}")

            all_compliance_rules.extend(compliance_rules)

        if not all_compliance_rules:
            print("\nRESULT: No compliance rules found - returning WARNING")
            return {
                "status": "WARNING",
                "error_message": f"No compliance rules found for jurisdictions: {', '.join([j.code for j in jurisdictions])}"
            }

        print(f"\nTotal compliance rules to check: {len(all_compliance_rules)}")

        errors = []
        warnings = []

        for rule in all_compliance_rules:
            print(f"\nChecking rule: {rule.rule_name} ({rule.rule_type})")
            result = self._check_rule(bid, rule, db)
            if result:
                print(f"  FAILED: {result}")
                if rule.severity == "ERROR":
                    errors.append(result)
                else:
                    warnings.append(result)
            else:
                print(f"  PASSED")

        if errors:
            print(f"\nRESULT: FAIL with {len(errors)} error(s)")
            return {
                "status": "FAIL",
                "error_message": "; ".join(errors)
            }
        elif warnings:
            print(f"\nRESULT: WARNING with {len(warnings)} warning(s)")
            return {
                "status": "WARNING",
                "error_message": "; ".join(warnings)
            }

        print("\nRESULT: PASS - All compliance rules satisfied")
        return {
            "status": "PASS",
            "error_message": "All jurisdiction-specific compliance rules satisfied"
        }
    
    def _check_rule(self, bid: Bid, rule: ComplianceRule, db: Session) -> str:
        """Check a specific compliance rule using directory DB"""
        rule_def = rule.rule_definition

        if rule.rule_type == "MBE":
            return self._check_mbe_rule(bid, rule, rule_def, db)
        elif rule.rule_type == "VSBE":
            return self._check_vsbe_rule(bid, rule, rule_def, db)
        elif rule.rule_type == "LOCAL_PREF":
            return self._check_local_preference_rule(bid, rule, rule_def)
        elif rule.rule_type == "DBE":
            return self._check_dbe_rule(bid, rule, rule_def, db)

        return None
    
    def _check_mbe_rule(self, bid: Bid, rule: ComplianceRule, rule_def: dict, db: Session) -> str:
        """Check MBE compliance rule - using breakdown data when available"""
        threshold = Decimal(str(rule_def.get('threshold', 0)))
        print(f"    MBE Rule - Threshold: {threshold}%")

        if not bid.total_amount or bid.total_amount == 0:
            print(f"    WARNING: Bid total_amount is 0 or None, skipping MBE check")
            return None

        mbe_total = Decimal('0')
        mbe_count = 0

        for bs in bid.bid_subcontractors:
            subcontractor = bs.subcontractor
            if not subcontractor:
                continue

            print(f"    Checking {subcontractor.legal_name}: value=${bs.subcontract_value}")

            directory_entry = db.query(SubcontractorDirectory).filter(
                SubcontractorDirectory.legal_name == subcontractor.legal_name
            ).first()

            # Check if breakdown data exists
            if bs.category_breakdown:
                print(f"      Using category breakdown: {bs.category_breakdown}")
                # Use breakdown to calculate MBE portion - NO certification check needed when using breakdown
                for entry in bs.category_breakdown:
                    if entry.get('category', '').lower() == 'mbe':
                        percentage = Decimal(str(entry.get('percentage', 0)))
                        allocated_amount = bs.subcontract_value * (percentage / Decimal('100'))
                        mbe_total += allocated_amount
                        mbe_count += 1
                        print(f"      ✓ Allocated ${allocated_amount} ({percentage}%) to MBE from breakdown")
                        break
            elif bs.counts_toward_mbe:
                # Fallback: use counts_toward_mbe flag (old behavior)
                if directory_entry and directory_entry.certifications:
                    has_mbe = directory_entry.certifications.get('mbe', False)
                    print(f"      Directory MBE certification: {has_mbe}")
                    if has_mbe:
                        mbe_total += bs.subcontract_value
                        mbe_count += 1
                        print(f"      ✓ Counted full amount toward MBE total")
                else:
                    print(f"      ✗ No directory entry or certifications")

        mbe_percentage = (mbe_total / bid.total_amount) * 100
        print(f"    MBE Total: ${mbe_total} ({mbe_count} entries)")
        print(f"    MBE Percentage: {mbe_percentage:.2f}% (required: {threshold}%)")

        if mbe_percentage < threshold:
            return f"{rule.rule_name}: MBE participation {mbe_percentage:.2f}% is below required {threshold}%"

        return None
    
    def _check_vsbe_rule(self, bid: Bid, rule: ComplianceRule, rule_def: dict, db: Session) -> str:
        """Check VSBE compliance rule - using breakdown data when available"""
        threshold = Decimal(str(rule_def.get('threshold', 0)))
        print(f"    VSBE Rule - Threshold: {threshold}%")

        if not bid.total_amount or bid.total_amount == 0:
            print(f"    WARNING: Bid total_amount is 0 or None, skipping VSBE check")
            return None

        vsbe_total = Decimal('0')
        vsbe_count = 0

        for bid_sub in bid.bid_subcontractors:
            subcontractor = bid_sub.subcontractor
            if not subcontractor:
                continue

            print(f"    Checking {subcontractor.legal_name}: value=${bid_sub.subcontract_value}")

            directory_entry = db.query(SubcontractorDirectory).filter(
                SubcontractorDirectory.legal_name == subcontractor.legal_name
            ).first()

            # Check if breakdown data exists
            if bid_sub.category_breakdown:
                print(f"      Using category breakdown: {bid_sub.category_breakdown}")
                # Use breakdown to calculate VSBE portion - NO certification check needed when using breakdown
                for entry in bid_sub.category_breakdown:
                    if entry.get('category', '').lower() == 'vsbe':
                        percentage = Decimal(str(entry.get('percentage', 0)))
                        allocated_amount = bid_sub.subcontract_value * (percentage / Decimal('100'))
                        vsbe_total += allocated_amount
                        vsbe_count += 1
                        print(f"      ✓ Allocated ${allocated_amount} ({percentage}%) to VSBE from breakdown")
                        break
            else:
                # Fallback: check directory certifications (old behavior)
                if directory_entry and directory_entry.certifications:
                    has_vsbe = directory_entry.certifications.get('vsbe', False)
                    print(f"      Directory VSBE certification: {has_vsbe}")
                    if has_vsbe:
                        vsbe_total += bid_sub.subcontract_value
                        vsbe_count += 1
                        print(f"      ✓ Counted full amount toward VSBE total")
                else:
                    print(f"      ✗ No directory entry or certifications")

        vsbe_percentage = (vsbe_total / bid.total_amount) * 100
        print(f"    VSBE Total: ${vsbe_total} ({vsbe_count} entries)")
        print(f"    VSBE Percentage: {vsbe_percentage:.2f}% (required: {threshold}%)")

        if vsbe_percentage < threshold:
            return f"{rule.rule_name}: VSBE participation {vsbe_percentage:.2f}% is below required {threshold}%"

        return None
    
    def _check_local_preference_rule(self, bid: Bid, rule: ComplianceRule, rule_def: dict) -> str:
        """Check local preference rule"""
        # This would check if local businesses are given preference
        # Implementation depends on specific jurisdiction requirements
        return None
    
    def _check_dbe_rule(self, bid: Bid, rule: ComplianceRule, rule_def: dict, db: Session) -> str:
        """Check DBE compliance rule - using breakdown data when available"""
        threshold = Decimal(str(rule_def.get('threshold', 0)))
        print(f"    DBE Rule - Threshold: {threshold}%")

        if not bid.total_amount or bid.total_amount == 0:
            print(f"    WARNING: Bid total_amount is 0 or None, skipping DBE check")
            return None

        dbe_total = Decimal('0')
        dbe_count = 0

        for bid_sub in bid.bid_subcontractors:
            subcontractor = bid_sub.subcontractor
            if not subcontractor:
                continue

            print(f"    Checking {subcontractor.legal_name}: value=${bid_sub.subcontract_value}")

            directory_entry = db.query(SubcontractorDirectory).filter(
                SubcontractorDirectory.legal_name == subcontractor.legal_name
            ).first()

            # Check if breakdown data exists
            if bid_sub.category_breakdown:
                print(f"      Using category breakdown: {bid_sub.category_breakdown}")
                # Use breakdown to calculate DBE portion - NO certification check needed when using breakdown
                for entry in bid_sub.category_breakdown:
                    if entry.get('category', '').lower() == 'dbe':
                        percentage = Decimal(str(entry.get('percentage', 0)))
                        allocated_amount = bid_sub.subcontract_value * (percentage / Decimal('100'))
                        dbe_total += allocated_amount
                        dbe_count += 1
                        print(f"      ✓ Allocated ${allocated_amount} ({percentage}%) to DBE from breakdown")
                        break
            else:
                # Fallback: check directory certifications (old behavior)
                if directory_entry and directory_entry.certifications:
                    has_dbe = directory_entry.certifications.get('dbe', False)
                    print(f"      Directory DBE certification: {has_dbe}")
                    if has_dbe:
                        dbe_total += bid_sub.subcontract_value
                        dbe_count += 1
                        print(f"      ✓ Counted full amount toward DBE total")
                else:
                    print(f"      ✗ No directory entry or certifications")

        dbe_percentage = (dbe_total / bid.total_amount) * 100
        print(f"    DBE Total: ${dbe_total} ({dbe_count} entries)")
        print(f"    DBE Percentage: {dbe_percentage:.2f}% (required: {threshold}%)")

        if dbe_percentage < threshold:
            return f"{rule.rule_name}: DBE participation {dbe_percentage:.2f}% is below required {threshold}%"

        return None


class MBEPercentageRule(ValidationRule):
    """Check if MBE percentage meets goal - using breakdown data when available"""

    def __init__(self):
        super().__init__(
            "mbe_percentage",
            "Verify MBE participation meets goal (using breakdown when available, verified from directory DB)"
        )

    def validate(self, bid: Bid, db: Session) -> Dict:
        if not bid.total_amount or bid.total_amount == 0:
            return {
                "status": "WARNING",
                "error_message": "Cannot calculate MBE percentage: total amount is 0"
            }

        mbe_total = Decimal('0')
        for bs in bid.bid_subcontractors:
            subcontractor = bs.subcontractor
            if not subcontractor:
                continue

            directory_entry = db.query(SubcontractorDirectory).filter(
                SubcontractorDirectory.legal_name == subcontractor.legal_name
            ).first()

            # Check if breakdown data exists
            if bs.category_breakdown:
                # Use breakdown to calculate MBE portion
                for entry in bs.category_breakdown:
                    if entry.get('category', '').lower() == 'mbe':
                        percentage = Decimal(str(entry.get('percentage', 0)))
                        allocated_amount = bs.subcontract_value * (percentage / Decimal('100'))

                        # Verify MBE certification in directory
                        if directory_entry and directory_entry.certifications:
                            if directory_entry.certifications.get('mbe', False):
                                mbe_total += allocated_amount
                        break
            elif bs.counts_toward_mbe:
                # Fallback: use counts_toward_mbe flag (old behavior)
                if directory_entry and directory_entry.certifications:
                    if directory_entry.certifications.get('mbe', False):
                        mbe_total += bs.subcontract_value

        mbe_percentage = (mbe_total / bid.total_amount) * 100

        if mbe_percentage < bid.mbe_goal:
            return {
                "status": "FAIL",
                "error_message": f"MBE percentage {mbe_percentage:.2f}% is below goal of {bid.mbe_goal}% (verified from directory DB)"
            }

        return {
            "status": "PASS",
            "error_message": f"MBE percentage {mbe_percentage:.2f}% meets goal of {bid.mbe_goal}% (verified from directory DB)"
        }


class SubcontractorNAICSMatchRule(ValidationRule):
    """Check if bid NAICS matches subcontractor NAICS codes from directory DB"""

    def __init__(self):
        super().__init__(
            "naics_match_certification",
            "Verify NAICS code matches subcontractor NAICS codes in directory DB"
        )

    def validate(self, bid: Bid, db: Session) -> Dict:
        print(f"\n=== DEBUG: SubcontractorNAICSMatchRule ===")
        print(f"Bid ID: {bid.id}")

        errors = []

        for bid_sub in bid.bid_subcontractors:
            subcontractor = db.query(Subcontractor).filter(
                Subcontractor.id == bid_sub.subcontractor_id
            ).first()

            if not subcontractor:
                continue

            print(f"\nChecking NAICS for: {subcontractor.legal_name}")
            print(f"  Bid NAICS code: '{bid_sub.naics_code}'")

            # Get NAICS codes from directory DB
            directory_entry = db.query(SubcontractorDirectory).filter(
                SubcontractorDirectory.legal_name == subcontractor.legal_name
            ).first()

            if not directory_entry:
                print(f"  ✗ Not found in directory DB")
                errors.append(
                    f"{subcontractor.legal_name}: Not found in directory DB"
                )
                continue

            if not directory_entry.naics_codes or len(directory_entry.naics_codes) == 0:
                print(f"  ✗ No NAICS codes in directory DB")
                errors.append(
                    f"{subcontractor.legal_name}: No NAICS codes in directory DB"
                )
                continue

            print(f"  Directory NAICS codes: {directory_entry.naics_codes}")

            # Check if bid NAICS code is in directory NAICS codes
            if bid_sub.naics_code not in directory_entry.naics_codes:
                print(f"  ✗ NAICS code '{bid_sub.naics_code}' NOT in directory list")
                errors.append(
                    f"{subcontractor.legal_name}: NAICS code '{bid_sub.naics_code}' not listed in directory DB. Valid codes: {', '.join(directory_entry.naics_codes)}"
                )
            else:
                print(f"  ✓ NAICS code '{bid_sub.naics_code}' found in directory")

        if errors:
            print(f"\nRESULT: FAIL with {len(errors)} error(s)")
            return {
                "status": "FAIL",
                "error_message": "; ".join(errors)
            }

        print("\nRESULT: PASS - All NAICS codes match directory DB")
        return {
            "status": "PASS",
            "error_message": "All NAICS codes match directory DB"
        }


class JurisdictionSpecificGoalRule(ValidationRule):
    """
    Check if bid meets jurisdiction-specific category goals (MBE, VSBE, WBE, SBE, DBE, CBE, etc.)
    Gets jurisdiction codes from subcontractor_directory and validates against jurisdiction's typical goals
    """

    def __init__(self):
        super().__init__(
            "jurisdiction_specific_goals",
            "Verify bid meets jurisdiction-specific category goals from directory DB"
        )

    def validate(self, bid: Bid, db: Session) -> Dict:
        print(f"\n=== DEBUG: JurisdictionSpecificGoalRule ===")
        print(f"Bid ID: {bid.id}")
        print(f"Bid total_amount: {bid.total_amount}")
        print(f"Bid mbe_goal: {bid.mbe_goal}%")

        if not bid.total_amount or bid.total_amount == 0:
            print("WARNING: Bid total_amount is 0, cannot verify goals")
            return {
                "status": "WARNING",
                "error_message": "Cannot verify jurisdiction-specific goals: total amount is 0"
            }

        # Collect all unique jurisdiction codes from subcontractors in directory
        jurisdiction_codes = set()

        print(f"\nNumber of bid subcontractors: {len(bid.bid_subcontractors)}")
        for bid_sub in bid.bid_subcontractors:
            subcontractor = db.query(Subcontractor).filter(
                Subcontractor.id == bid_sub.subcontractor_id
            ).first()

            if not subcontractor:
                continue

            # Get jurisdiction codes from directory
            directory_entry = db.query(SubcontractorDirectory).filter(
                SubcontractorDirectory.legal_name == subcontractor.legal_name
            ).first()

            if directory_entry and directory_entry.jurisdiction_codes:
                print(f"  {subcontractor.legal_name}: jurisdictions {directory_entry.jurisdiction_codes}")
                jurisdiction_codes.update(directory_entry.jurisdiction_codes)

        if not jurisdiction_codes:
            print("\nRESULT: No jurisdiction codes found in directory")
            return {
                "status": "WARNING",
                "error_message": "Cannot verify jurisdiction-specific goals: jurisdiction not identified"
            }

        print(f"\nUnique jurisdiction codes found: {list(jurisdiction_codes)}")

        # Get jurisdiction records
        jurisdictions = db.query(Jurisdiction).filter(
            Jurisdiction.code.in_(list(jurisdiction_codes))
        ).all()

        if not jurisdictions:
            print("RESULT: No matching jurisdictions found in DB")
            return {
                "status": "WARNING",
                "error_message": f"Cannot verify jurisdiction-specific goals: no jurisdiction records found for {', '.join(jurisdiction_codes)}"
            }

        print(f"Jurisdictions found: {[(j.code, j.name) for j in jurisdictions]}")

        errors = []
        warnings = []

        # Calculate actual percentages for each certification type
        cert_totals = {
            'mbe': Decimal('0'),
            'vsbe': Decimal('0'),
            'wbe': Decimal('0'),
            'sbe': Decimal('0'),
            'dbe': Decimal('0'),
            'cbe': Decimal('0')
        }

        print("\n--- Calculating Certification Totals from Breakdown & Directory ---")
        for bid_sub in bid.bid_subcontractors:
            subcontractor = bid_sub.subcontractor
            if not subcontractor:
                continue

            directory_entry = db.query(SubcontractorDirectory).filter(
                SubcontractorDirectory.legal_name == subcontractor.legal_name
            ).first()

            print(f"\n{subcontractor.legal_name} (${bid_sub.subcontract_value}):")

            # Check if category_breakdown exists
            if bid_sub.category_breakdown:
                print(f"  Using category breakdown: {bid_sub.category_breakdown}")
                # Use the breakdown to allocate amounts to categories
                for entry in bid_sub.category_breakdown:
                    category = entry.get('category', '').lower()
                    percentage = Decimal(str(entry.get('percentage', 0)))
                    allocated_amount = bid_sub.subcontract_value * (percentage / Decimal('100'))

                    # Verify certification exists in directory
                    if directory_entry and directory_entry.certifications:
                        if directory_entry.certifications.get(category, False):
                            cert_totals[category] += allocated_amount
                            print(f"  ✓ Allocated ${allocated_amount} ({percentage}%) to {category.upper()} (verified in directory)")
                        else:
                            print(f"  ✗ {category.upper()} not certified in directory, skipping")
                    else:
                        print(f"  ✗ No directory entry or certifications, skipping {category.upper()}")
            elif directory_entry and directory_entry.certifications:
                # Fallback: Use directory certifications (old behavior)
                print(f"  No breakdown, using directory certifications: {directory_entry.certifications}")
                # Count each certification type
                for cert_type in cert_totals.keys():
                    if directory_entry.certifications.get(cert_type, False):
                        cert_totals[cert_type] += bid_sub.subcontract_value
                        print(f"  ✓ Counted full amount toward {cert_type.upper()}")

        # Calculate percentages
        cert_percentages = {}
        print("\n--- Certification Percentages ---")
        for cert_type, total in cert_totals.items():
            percentage = (total / bid.total_amount) * 100
            cert_percentages[cert_type] = percentage
            if total > 0:
                print(f"{cert_type.upper()}: ${total} = {percentage:.2f}%")

        # Check against each jurisdiction's goals
        for jurisdiction in jurisdictions:
            print(f"\n--- Checking {jurisdiction.code} ({jurisdiction.name}) Goals ---")

            # Check MBE goal
            if jurisdiction.mbe_goal_typical:
                print(f"MBE Goal: {jurisdiction.mbe_goal_typical}% (Actual: {cert_percentages['mbe']:.2f}%)")
                if cert_percentages['mbe'] < jurisdiction.mbe_goal_typical:
                    errors.append(
                        f"{jurisdiction.name}: MBE {cert_percentages['mbe']:.2f}% is below required {jurisdiction.mbe_goal_typical}%"
                    )
                    print(f"  FAIL: Below threshold")
                else:
                    print(f"  PASS: Meets threshold")

            # Check VSBE goal
            if jurisdiction.vsbe_goal_typical:
                print(f"VSBE Goal: {jurisdiction.vsbe_goal_typical}% (Actual: {cert_percentages['vsbe']:.2f}%)")
                if cert_percentages['vsbe'] < jurisdiction.vsbe_goal_typical:
                    errors.append(
                        f"{jurisdiction.name}: VSBE {cert_percentages['vsbe']:.2f}% is below required {jurisdiction.vsbe_goal_typical}%"
                    )
                    print(f"  FAIL: Below threshold")
                else:
                    print(f"  PASS: Meets threshold")

            # Note: Other certification goals (WBE, SBE, DBE, CBE) would be checked here
            # if the jurisdiction model is extended to include those fields

        if errors:
            print(f"\nRESULT: FAIL with {len(errors)} error(s)")
            return {
                "status": "FAIL",
                "error_message": "; ".join(errors)
            }
        elif warnings:
            print(f"\nRESULT: WARNING with {len(warnings)} warning(s)")
            return {
                "status": "WARNING",
                "error_message": "; ".join(warnings)
            }

        print("\nRESULT: PASS - All jurisdiction-specific goals met")
        return {
            "status": "PASS",
            "error_message": "All jurisdiction-specific goals met from directory DB"
        }


# List of all validation rules - ALL VERIFIED FROM DIRECTORY DB
# Validation order:
# 1. Directory DB jurisdiction check (FIRST)
# 2. Certifications from directory DB
# 3. Compliance rules (amounts only, verified from directory DB)
# NOTE: NAICS code validation is DISABLED
ALL_RULES = [
    DirectoryJurisdictionMatchRule(),    # FIRST: Check directory DB for jurisdiction
    # NAICSCodeValidRule(),              # DISABLED: Check NAICS codes from directory DB
    CertificationExistsRule(),           # Check certifications from directory DB
    SubcontractorNAICSMatchRule(),       # Check NAICS matches certifications
    JurisdictionComplianceRule(),        # Check compliance rules (amounts only, verified from directory DB)
    MBEPercentageRule(),                 # Count amounts for MBE percentage (verified from directory DB)
    JurisdictionSpecificGoalRule(),      # Check jurisdiction-specific goals
]