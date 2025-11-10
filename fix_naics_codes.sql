-- Fix NAICS codes in bid_subcontractors table
-- This script updates bid_subcontractors with NAICS codes from the subcontractor_directory

-- First, let's see the current state
SELECT
    bs.id,
    s.legal_name,
    bs.naics_code as current_naics,
    sd.naics_codes as directory_naics
FROM bid_subcontractors bs
JOIN subcontractors s ON bs.subcontractor_id = s.id
LEFT JOIN subcontractor_directory sd ON s.legal_name = sd.legal_name
WHERE bs.naics_code IS NULL OR bs.naics_code = '';

-- Update bid_subcontractors with the first NAICS code from directory
-- This assumes the directory has the correct NAICS codes
UPDATE bid_subcontractors bs
SET naics_code = sd.naics_codes[1]
FROM subcontractors s
JOIN subcontractor_directory sd ON s.legal_name = sd.legal_name
WHERE bs.subcontractor_id = s.id
  AND (bs.naics_code IS NULL OR bs.naics_code = '')
  AND sd.naics_codes IS NOT NULL
  AND array_length(sd.naics_codes, 1) > 0;

-- Verify the update
SELECT
    bs.id,
    s.legal_name,
    bs.naics_code as updated_naics,
    sd.naics_codes as directory_naics
FROM bid_subcontractors bs
JOIN subcontractors s ON bs.subcontractor_id = s.id
LEFT JOIN subcontractor_directory sd ON s.legal_name = sd.legal_name;

-- If you want to update to a specific NAICS code for Metro Construction Group:
-- UPDATE bid_subcontractors bs
-- SET naics_code = '236220'
-- FROM subcontractors s
-- WHERE bs.subcontractor_id = s.id
--   AND s.legal_name = 'Metro Construction Group'
--   AND (bs.naics_code IS NULL OR bs.naics_code = '');
