-- 1. Insert Core Organization and capture its ID
WITH org_insert AS (
    INSERT INTO organizations (name) VALUES
    ('City Planning Department')
    RETURNING id AS org_id
),

-- 2. Insert Organizations for Bids
org_bid_insert AS (
    INSERT INTO organizations (name) VALUES
    ('State Department of Transportation'),
    ('MegaCorp Infrastructure')
    RETURNING id AS bid_org_id
),

-- 3. Insert Sample Subcontractors and Certifications
sub_insert AS (
    INSERT INTO subcontractors (organization_id, legal_name, certification_number, is_mbe) VALUES
    ((SELECT org_id FROM org_insert), 'Elite Bridge Builders Inc.', 'MBE-EBB-9001', TRUE),
    ((SELECT org_id FROM org_insert), 'Alpha Engineering Solutions', 'WBE-AES-1234', FALSE),
    ((SELECT org_id FROM org_insert), 'GreenStreet Landscaping', 'SBE-GSL-5555', TRUE)
    RETURNING id AS sub_id, legal_name, certification_number, is_mbe
),

cert_insert AS (
    INSERT INTO certifications (subcontractor_id, cert_number, cert_type, naics_codes)
    SELECT
        sub_id,
        certification_number,
        CASE
            WHEN is_mbe THEN 'MBE'
            ELSE 'WBE/SBE'
        END,
        -- Example of JSONB data for NAICS codes
        CASE sub_id
            WHEN (SELECT sub_id FROM sub_insert LIMIT 1 OFFSET 0) THEN '["236220", "541330"]'::jsonb
            WHEN (SELECT sub_id FROM sub_insert LIMIT 1 OFFSET 1) THEN '["541330"]'::jsonb
            ELSE '["561730"]'::jsonb
        END
    FROM sub_insert
    RETURNING *
),

-- 4. Insert a Bid record
bid_insert AS (
    INSERT INTO bids (organization_id, solicitation_number, total_amount, mbe_goal) VALUES
    ((SELECT bid_org_id FROM org_bid_insert LIMIT 1 OFFSET 0), 'DOT-2025-04A', 1500000.00, 25.00)
    RETURNING id AS bid_id
)

-- 5. Link Subcontractors to the Bid (Junction Table)
INSERT INTO bid_subcontractors (bid_id, subcontractor_id, work_description, naics_code, subcontract_value, counts_toward_mbe) VALUES
((SELECT bid_id FROM bid_insert), (SELECT sub_id FROM sub_insert WHERE legal_name = 'Elite Bridge Builders Inc.'), 'Steel fabrication and erection', '236220', 300000.00, TRUE),
((SELECT bid_id FROM bid_insert), (SELECT sub_id FROM sub_insert WHERE legal_name = 'GreenStreet Landscaping'), 'Median and shoulder landscaping', '561730', 50000.00, TRUE)

-- 6. Insert Validation Results
RETURNING *; -- Return the result of the final insert (bid_subcontractors)