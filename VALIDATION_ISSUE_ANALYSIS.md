# Validation Issue Analysis & Resolution

## Issue Summary
**Error:** `NAICS code '' not listed in directory DB for Metro Construction Group`

## Root Cause Analysis

### 1. Data Issue
The `bid_subcontractors` table has **empty NAICS codes** for some subcontractors, while the `subcontractor_directory` table has the correct NAICS codes.

**Current State:**
- `bid_subcontractors.naics_code`: `''` (empty string)
- `subcontractor_directory.naics_codes`: `["236220"]` (correct data)

### 2. Validation Flow
The validation engine now follows this order (as updated):

```
1. DirectoryJurisdictionMatchRule → Check jurisdiction from directory DB
2. NAICSCodeValidRule → Check NAICS from directory DB
3. CertificationExistsRule → Check certifications from directory DB
4. SubcontractorNAICSMatchRule → Verify NAICS matches certs
5. JurisdictionComplianceRule → Count amounts (verified from directory DB)
6. MBEPercentageRule → Count amounts (verified from directory DB)
7. JurisdictionSpecificGoalRule → Check jurisdiction goals
```

### 3. Directory DB Structure

The `subcontractor_directory` table stores:
- `jurisdiction_codes`: ARRAY of TEXT (e.g., `["MD", "DC"]`)
- `naics_codes`: ARRAY of TEXT (e.g., `["236220", "237310"]`)
- `certifications`: JSONB (e.g., `{"mbe": true, "vsbe": false, "dbe": false}`)

## Resolution Steps

### Option 1: Fix Data in Database (Recommended)

Run the SQL script in `fix_naics_codes.sql`:

```sql
-- Update bid_subcontractors with NAICS from directory
UPDATE bid_subcontractors bs
SET naics_code = sd.naics_codes[1]
FROM subcontractors s
JOIN subcontractor_directory sd ON s.legal_name = sd.legal_name
WHERE bs.subcontractor_id = s.id
  AND (bs.naics_code IS NULL OR bs.naics_code = '')
  AND sd.naics_codes IS NOT NULL
  AND array_length(sd.naics_codes, 1) > 0;
```

### Option 2: Fix Specific Record

For Metro Construction Group specifically:

```sql
UPDATE bid_subcontractors bs
SET naics_code = '236220'
FROM subcontractors s
WHERE bs.subcontractor_id = s.id
  AND s.legal_name = 'Metro Construction Group'
  AND (bs.naics_code IS NULL OR bs.naics_code = '');
```

### Option 3: Prevent Future Issues

Update the `BidService.add_subcontractor_to_bid()` method to auto-populate NAICS from directory if not provided:

```python
def add_subcontractor_to_bid(
    self,
    bid_id: UUID,
    subcontractor_data: BidSubcontractorCreate
) -> BidSubcontractor:
    """Add a subcontractor to a bid"""
    # Ensure the subcontractor exists in the organization's table
    self._ensure_subcontractor_in_org(subcontractor_data.subcontractor_id, bid_id)

    # Auto-populate NAICS if empty
    if not subcontractor_data.naics_code or subcontractor_data.naics_code.strip() == '':
        directory_sub = self.db.query(SubcontractorDirectory).filter(
            SubcontractorDirectory.id == subcontractor_data.subcontractor_id
        ).first()
        if directory_sub and directory_sub.naics_codes:
            subcontractor_data.naics_code = directory_sub.naics_codes[0]

    bid_sub = BidSubcontractor(
        bid_id=bid_id,
        **subcontractor_data.model_dump()
    )
    self.db.add(bid_sub)
    self.db.commit()
    self.db.refresh(bid_sub)
    return bid_sub
```

## Validation Rules Updated

All validation rules now use **directory DB as the single source of truth**:

### 1. Jurisdiction Validation
- **Source:** `subcontractor_directory.jurisdiction_codes`
- **Check:** Bid jurisdiction must be in directory's jurisdiction array

### 2. NAICS Code Validation
- **Source:** `subcontractor_directory.naics_codes`
- **Check:** Bid NAICS must be in directory's NAICS array
- **Enhancement:** Now provides detailed error message showing what NAICS codes are available

### 3. Certification Validation
- **Source:** `subcontractor_directory.certifications`
- **Check:** MBE/VSBE/DBE flags must match directory JSONB

### 4. Compliance Amount Counting
- **Source:** Directory DB certifications
- **Behavior:** Only counts amounts where directory confirms certification
- **Rules:** MBE, VSBE, DBE percentage calculations

## Compliance Rules & MBE Percentage

### Compliance Rules Table Structure
```sql
compliance_rules {
  id: UUID
  jurisdiction_id: UUID
  rule_name: STRING
  rule_type: STRING (MBE, VSBE, DBE, LOCAL_PREF)
  rule_definition: JSONB {"threshold": 15.0}
  severity: STRING (ERROR, WARNING)
}
```

### MBE Percentage Calculation

The system now:
1. **Retrieves** compliance rules for the bid's jurisdiction
2. **Verifies** each subcontractor in directory DB
3. **Counts** only amounts where `directory_entry.certifications.mbe == true`
4. **Calculates** percentage: `(mbe_total / bid_total) * 100`
5. **Compares** against rule threshold

**Example:**
```
Compliance Rule: MD - MBE 15% threshold
Bid Total: $1,000,000
MBE Subcontractor: Metro Construction Group
  - Directory certification: {"mbe": true}
  - Subcontract value: $150,000
  - Counts toward MBE: YES

MBE Total: $150,000
MBE Percentage: 15.00%
Result: PASS (meets 15% threshold)
```

## Testing

Run `test_validation_issue.py` to see the validation logic:

```bash
python test_validation_issue.py
```

Expected output shows:
- NAICS validation logic
- Jurisdiction validation logic
- MBE certification validation logic
- MBE percentage calculation

## Next Steps

1. ✅ Run `fix_naics_codes.sql` in Supabase SQL editor
2. ✅ Verify data update was successful
3. ✅ Re-run validation on affected bids
4. ✅ Consider implementing Option 3 to prevent future issues
5. ✅ Add validation in API to ensure NAICS is never empty

## Files Modified

- `app/validation/rules.py`: Enhanced NAICS validation with empty check
- `app/validation/engine.py`: Updated documentation
- `fix_naics_codes.sql`: SQL script to fix data
- `test_validation_issue.py`: Test script for validation logic
- `VALIDATION_ISSUE_ANALYSIS.md`: This document
