"""
Test script to debug validation issue with Metro Construction Group
"""

# Test data simulation
print("="*70)
print("Testing NAICS Code Validation Logic")
print("="*70)

# Simulated data from Supabase
bid_subcontractor_naics = ""  # Empty string from error message
subcontractor_name = "Metro Construction Group"
directory_naics_codes = ["236220"]  # From Supabase

print(f"\nSubcontractor: {subcontractor_name}")
print(f"NAICS in bid_subcontractor: '{bid_subcontractor_naics}'")
print(f"NAICS in directory: {directory_naics_codes}")

# Test the validation logic
if not bid_subcontractor_naics or bid_subcontractor_naics.strip() == '':
    print(f"\n[X] ERROR: {subcontractor_name} has no NAICS code assigned in bid")
elif bid_subcontractor_naics not in directory_naics_codes:
    print(f"\n[X] ERROR: NAICS code '{bid_subcontractor_naics}' not in directory {directory_naics_codes}")
else:
    print(f"\n[OK] PASS: NAICS code valid")

print("\n" + "="*70)
print("Issue Identified:")
print("="*70)
print("The bid_subcontractor table has an empty NAICS code for Metro Construction Group")
print("The directory has NAICS code '236220' but it's not assigned in the bid")
print("\nSolution:")
print("1. Update bid_subcontractor record to include NAICS code '236220'")
print("2. Or ensure NAICS code is populated when creating bid subcontractors")
print("="*70)

# Test jurisdiction matching
print("\n" + "="*70)
print("Testing Jurisdiction Validation Logic")
print("="*70)

directory_jurisdiction_codes = ["MD", "DC"]  # Example
bid_jurisdiction_code = "MD"  # Example

print(f"\nJurisdiction in bid: {bid_jurisdiction_code}")
print(f"Jurisdictions in directory: {directory_jurisdiction_codes}")

if directory_jurisdiction_codes:
    if bid_jurisdiction_code not in directory_jurisdiction_codes:
        print(f"\n[X] ERROR: Jurisdiction {bid_jurisdiction_code} not authorized")
    else:
        print(f"\n[OK] PASS: Jurisdiction authorized")
else:
    print(f"\n[X] ERROR: No jurisdiction codes in directory")

# Test MBE certification
print("\n" + "="*70)
print("Testing MBE Certification Validation Logic")
print("="*70)

directory_certifications = {"mbe": True, "vsbe": False, "dbe": False}  # Example
counts_toward_mbe = True

print(f"\nCounts toward MBE: {counts_toward_mbe}")
print(f"Directory certifications: {directory_certifications}")

if counts_toward_mbe:
    if directory_certifications:
        if not directory_certifications.get('mbe', False):
            print(f"\n[X] ERROR: Marked as MBE but no MBE certification in directory")
        else:
            print(f"\n[OK] PASS: MBE certification verified")
    else:
        print(f"\n[X] ERROR: No certifications in directory")

# Test MBE percentage calculation
print("\n" + "="*70)
print("Testing MBE Percentage Calculation")
print("="*70)

bid_total = 1000000
subcontract_value = 150000
mbe_goal = 15.0

print(f"\nBid Total: ${bid_total:,.2f}")
print(f"MBE Subcontract Value: ${subcontract_value:,.2f}")
print(f"MBE Goal: {mbe_goal}%")

mbe_percentage = (subcontract_value / bid_total) * 100
print(f"MBE Percentage: {mbe_percentage:.2f}%")

if mbe_percentage < mbe_goal:
    print(f"[X] FAIL: MBE percentage {mbe_percentage:.2f}% is below goal of {mbe_goal}%")
else:
    print(f"[OK] PASS: MBE percentage {mbe_percentage:.2f}% meets goal of {mbe_goal}%")

print("\n" + "="*70)
