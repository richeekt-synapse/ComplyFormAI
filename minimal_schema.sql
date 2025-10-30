CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL
);

CREATE TABLE subcontractors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    legal_name VARCHAR(255) NOT NULL,
    certification_number VARCHAR(100),
    is_mbe BOOLEAN DEFAULT false
);

CREATE TABLE certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subcontractor_id UUID REFERENCES subcontractors(id),
    cert_number VARCHAR(100),
    cert_type VARCHAR(50),
    naics_codes JSONB
);

CREATE TABLE bids (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    solicitation_number VARCHAR(50),
    total_amount DECIMAL(15,2),
    mbe_goal DECIMAL(5,2)
);

CREATE TABLE bid_subcontractors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bid_id UUID REFERENCES bids(id),
    subcontractor_id UUID REFERENCES subcontractors(id),
    work_description TEXT,
    naics_code VARCHAR(10),
    subcontract_value DECIMAL(15,2),
    counts_toward_mbe BOOLEAN DEFAULT false
);

CREATE TABLE validation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bid_id UUID REFERENCES bids(id),
    rule_name VARCHAR(255),
    status VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);