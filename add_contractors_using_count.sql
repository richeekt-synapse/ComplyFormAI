-- Migration: Add contractors_using_count column to subcontractor_directory table
-- This column tracks the network effect: how many contractors use this subcontractor

ALTER TABLE subcontractor_directory
ADD COLUMN IF NOT EXISTS contractors_using_count INTEGER DEFAULT 0;

-- Optional: Update existing records to have a default value
UPDATE subcontractor_directory
SET contractors_using_count = 0
WHERE contractors_using_count IS NULL;
