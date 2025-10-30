CREATE TABLE naics_codes (
    code VARCHAR(10) PRIMARY KEY,
    description TEXT NOT NULL
);

INSERT INTO naics_codes (code, description) VALUES
('236220', 'Commercial and Institutional Building Construction'),
('541330', 'Engineering Services'),
('541511', 'Custom Computer Programming Services'),
('541611', 'Administrative Management and General Management Consulting Services'),
('561730', 'Landscaping Services');