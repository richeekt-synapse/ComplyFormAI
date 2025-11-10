from sqlalchemy import create_engine, text

# Supabase connection string
connection_url = "postgresql://postgres.lfizixmiqrspdskubdyj:sgnAdmin11%24%24@aws-1-us-east-1.pooler.supabase.com:5432/postgres"

print("="*70)
print("Checking Validation Data")
print("="*70)

engine = create_engine(connection_url, pool_pre_ping=True)

with engine.connect() as conn:
    # Check NAICS codes table
    print("\n=== NAICS Codes Table ===")
    result = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'naics_codes'
        ORDER BY ordinal_position
    """))
    for row in result:
        print(f"{row[0]}: {row[1]}")

    # Check sample NAICS codes
    print("\n=== Sample NAICS Codes ===")
    result = conn.execute(text("SELECT code, description FROM naics_codes LIMIT 10"))
    for row in result:
        print(f"Code: {row[0]}, Description: {row[1][:50] if row[1] else 'N/A'}")

    # Check if '236220' exists
    print("\n=== Checking NAICS Code 236220 ===")
    result = conn.execute(text("SELECT code, description FROM naics_codes WHERE code = '236220'"))
    row = result.fetchone()
    if row:
        print(f"✓ Found: {row[0]} - {row[1]}")
    else:
        print("✗ NAICS code 236220 NOT found in table")

    # Check subcontractor_directory table
    print("\n=== Subcontractor Directory Table ===")
    result = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'subcontractor_directory'
        ORDER BY ordinal_position
    """))
    for row in result:
        print(f"{row[0]}: {row[1]}")

    # Check Metro Construction Group
    print("\n=== Metro Construction Group Entry ===")
    result = conn.execute(text("""
        SELECT legal_name, naics_codes, jurisdiction_codes, certifications
        FROM subcontractor_directory
        WHERE legal_name ILIKE '%Metro Construction%'
    """))
    row = result.fetchone()
    if row:
        print(f"Legal Name: {row[0]}")
        print(f"NAICS Codes: {row[1]}")
        print(f"Jurisdiction Codes: {row[2]}")
        print(f"Certifications: {row[3]}")
    else:
        print("✗ Metro Construction Group NOT found in directory")

    # Check all directory entries
    print("\n=== All Directory Entries ===")
    result = conn.execute(text("""
        SELECT legal_name, naics_codes, jurisdiction_codes, certifications
        FROM subcontractor_directory
    """))
    for row in result:
        print(f"\nName: {row[0]}")
        print(f"  NAICS: {row[1]}")
        print(f"  Jurisdictions: {row[2]}")
        print(f"  Certifications: {row[3]}")

    # Check bid_subcontractors
    print("\n=== Bid Subcontractors ===")
    result = conn.execute(text("""
        SELECT bs.naics_code, s.legal_name, bs.counts_toward_mbe, bs.subcontract_value
        FROM bid_subcontractors bs
        JOIN subcontractors s ON bs.subcontractor_id = s.id
        LIMIT 10
    """))
    for row in result:
        print(f"NAICS: {row[0]}, Name: {row[1]}, MBE: {row[2]}, Value: {row[3]}")

    # Check jurisdictions
    print("\n=== Jurisdictions ===")
    result = conn.execute(text("SELECT code, name FROM jurisdictions"))
    for row in result:
        print(f"Code: {row[0]}, Name: {row[1]}")

    # Check compliance rules
    print("\n=== Compliance Rules ===")
    result = conn.execute(text("""
        SELECT cr.rule_name, cr.rule_type, cr.rule_definition, j.code as jurisdiction_code
        FROM compliance_rules cr
        JOIN jurisdictions j ON cr.jurisdiction_id = j.id
    """))
    for row in result:
        print(f"Rule: {row[0]}, Type: {row[1]}, Definition: {row[2]}, Jurisdiction: {row[3]}")

print("\n" + "="*70)
