-- Migration: Add category_breakdown column to bid_subcontractors table
-- Description: Adds a JSONB column to store category breakdown data (MBE, WBE, SBE, VSBE, etc.)
-- Date: 2025-11-10

-- Add the category_breakdown column
ALTER TABLE bid_subcontractors
ADD COLUMN IF NOT EXISTS category_breakdown JSONB;

-- Add a comment to the column for documentation
COMMENT ON COLUMN bid_subcontractors.category_breakdown IS
'Stores category breakdown as JSON array: [{"category": "MBE", "percentage": 50.0}, {"category": "WBE", "percentage": 50.0}]';

-- Optional: Create an index on the JSONB column for better query performance
CREATE INDEX IF NOT EXISTS idx_bid_subcontractors_category_breakdown
ON bid_subcontractors USING GIN (category_breakdown);

-- Verification query to check the column was added
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'bid_subcontractors' AND column_name = 'category_breakdown';
