# Network Effects Feature Implementation

## Overview
This document describes the implementation of the "network effects" feature that shows how many contractors use each subcontractor (e.g., "24 other contractors use this sub").

## Changes Made

### 1. Database Schema Changes

#### Added Field to `subcontractor_directory` Table
- **Field**: `contractors_using_count` (INTEGER, default: 0)
- **Purpose**: Tracks the number of unique contractors that have engaged with this subcontractor
- **Location**: [app/models/subcontractor_directory.py](app/models/subcontractor_directory.py:24)

#### Migration Script
- **File**: [migrations/001_add_contractor_usage_count.sql](migrations/001_add_contractor_usage_count.sql)
- **Run this to add the field to your database**:
  ```sql
  ALTER TABLE subcontractor_directory
  ADD COLUMN contractors_using_count INTEGER DEFAULT 0;

  -- Update existing records
  UPDATE subcontractor_directory sd
  SET contractors_using_count = (
      SELECT COUNT(DISTINCT so.organization_id)
      FROM subcontractor_outreach so
      WHERE so.subcontractor_id = sd.id
  );
  ```

### 2. API Schema Updates

#### Updated Pydantic Schemas
- **File**: [app/schemas/subcontractor_directory.py](app/schemas/subcontractor_directory.py:19)
- **Changes**:
  - Added `contractors_using_count` to `SubcontractorDirectoryBase`
  - Added `contractors_using_count` to `SubcontractorDirectoryUpdate`
  - Field is now included in all API responses

### 3. Service Layer Methods

#### SubcontractorDirectoryService
**File**: [app/services/subcontractor_directory_service.py](app/services/subcontractor_directory_service.py:191-229)

**New Methods**:

1. **`calculate_contractor_usage_count(subcontractor_id: UUID) -> int`**
   - Calculates how many unique contractors have used this subcontractor
   - Queries the `subcontractor_outreach` table for distinct `organization_id` values

2. **`update_contractor_usage_count(subcontractor_id: UUID) -> SubcontractorDirectory`**
   - Updates the cached `contractors_using_count` for a specific subcontractor
   - Returns the updated subcontractor object

3. **`update_all_contractor_usage_counts() -> int`**
   - Batch updates all subcontractor usage counts
   - Useful for initial data population or periodic refresh
   - Returns count of updated records

#### SubcontractorOutreachService
**File**: [app/services/subcontractor_outreach_service.py](app/services/subcontractor_outreach_service.py:31-47)

**New Methods**:

1. **`_update_subcontractor_usage_count(subcontractor_id: UUID) -> None`** (private)
   - Automatically recalculates and updates the usage count
   - Called after outreach creation and deletion

**Modified Methods**:
- `create_outreach()` - Now auto-updates usage count after creating outreach
- `delete_outreach()` - Now auto-updates usage count after deleting outreach

### 4. API Endpoints

#### New Endpoints in `/directory`
**File**: [app/routes/directory.py](app/routes/directory.py:167-201)

1. **`POST /directory/{subcontractor_id}/update-usage-count`**
   - Manually trigger usage count update for a specific subcontractor
   - Returns the updated subcontractor object
   - **Response**: `SubcontractorDirectory` schema

2. **`POST /directory/update-all-usage-counts`**
   - Batch update usage counts for all subcontractors
   - Useful for data maintenance
   - **Response**:
     ```json
     {
       "message": "Successfully updated contractor usage counts",
       "updated_count": 42
     }
     ```

## Usage Examples

### Frontend Display Example

When displaying a subcontractor in search results or detail view:

```javascript
// Example API response
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "legal_name": "ABC Construction Services",
  "rating": 4.5,
  "projects_completed": 87,
  "contractors_using_count": 24,  // <-- Network effect metric
  "certifications": {
    "mbe": true,
    "vsbe": false
  },
  ...
}

// Frontend display
const networkEffectText = `${subcontractor.contractors_using_count} other contractors use this sub`;
```

### API Request Examples

#### Get Subcontractor with Usage Count
```bash
GET /directory/{subcontractor_id}
```

Response includes `contractors_using_count` field automatically.

#### Search Subcontractors (all include usage count)
```bash
POST /directory/search
{
  "naics_codes": ["236220"],
  "is_mbe": true,
  "min_rating": 3.0
}
```

#### Manually Update Usage Count for One Subcontractor
```bash
POST /directory/{subcontractor_id}/update-usage-count
```

#### Batch Update All Usage Counts
```bash
POST /directory/update-all-usage-counts
```

## How It Works

### Automatic Updates
The usage count is **automatically updated** when:
1. A new outreach record is created (via `SubcontractorOutreachService.create_outreach()`)
2. An outreach record is deleted (via `SubcontractorOutreachService.delete_outreach()`)

### Calculation Logic
The count represents the number of **unique organizations** (contractors) that have:
- Created at least one outreach record with this subcontractor
- Status can be any of: `CONTACTED`, `RESPONDED`, `COMMITTED`, or `DECLINED`

The SQL query used:
```sql
SELECT COUNT(DISTINCT organization_id)
FROM subcontractor_outreach
WHERE subcontractor_id = {subcontractor_id}
```

### Caching Strategy
- The count is **cached** in the `contractors_using_count` field for performance
- This avoids expensive COUNT queries on every API call
- The cache is updated automatically via triggers in the service layer

## Database Migration Steps

1. **Run the migration script**:
   ```bash
   psql -U your_user -d your_database -f migrations/001_add_contractor_usage_count.sql
   ```

2. **Or manually execute**:
   ```sql
   ALTER TABLE subcontractor_directory
   ADD COLUMN contractors_using_count INTEGER DEFAULT 0;
   ```

3. **Populate initial data** (if you have existing outreach records):
   ```bash
   POST /directory/update-all-usage-counts
   ```

## Testing

### Test the Feature

1. **Create some outreach records** for a subcontractor:
   ```bash
   POST /outreach/
   {
     "organization_id": "org-1-uuid",
     "opportunity_id": "opp-1-uuid",
     "subcontractor_id": "sub-1-uuid",
     "status": "CONTACTED"
   }
   ```

2. **Check the subcontractor's usage count**:
   ```bash
   GET /directory/{sub-1-uuid}
   ```

   Should show `contractors_using_count: 1`

3. **Create outreach from another organization**:
   ```bash
   POST /outreach/
   {
     "organization_id": "org-2-uuid",  // Different org
     "opportunity_id": "opp-2-uuid",
     "subcontractor_id": "sub-1-uuid",  // Same sub
     "status": "CONTACTED"
   }
   ```

4. **Verify count increased**:
   ```bash
   GET /directory/{sub-1-uuid}
   ```

   Should now show `contractors_using_count: 2`

## Performance Considerations

- **Caching**: The count is cached in the database, so reads are very fast
- **Write overhead**: Small overhead when creating/deleting outreach (one additional UPDATE query)
- **Batch updates**: Use `/update-all-usage-counts` endpoint for periodic recalculation if needed
- **Scalability**: For very high-volume systems, consider moving updates to async queue

## Future Enhancements

Potential improvements:
1. Add time-based filtering (e.g., "contractors in last 12 months")
2. Filter by outreach status (e.g., only count "COMMITTED" status)
3. Add database trigger to auto-update on outreach changes (instead of service layer)
4. Add analytics: most popular subcontractors, trending subcontractors, etc.
5. Display the actual contractor names (with privacy controls)

## Files Modified

1. [app/models/subcontractor_directory.py](app/models/subcontractor_directory.py:24) - Added field
2. [app/schemas/subcontractor_directory.py](app/schemas/subcontractor_directory.py:19) - Updated schemas
3. [app/services/subcontractor_directory_service.py](app/services/subcontractor_directory_service.py:191-229) - Added methods
4. [app/services/subcontractor_outreach_service.py](app/services/subcontractor_outreach_service.py:31-47) - Auto-update logic
5. [app/routes/directory.py](app/routes/directory.py:167-201) - New endpoints
6. [migrations/001_add_contractor_usage_count.sql](migrations/001_add_contractor_usage_count.sql) - Migration script

## Summary

You now have a complete network effects feature that:
- Shows "X contractors use this sub" on every subcontractor record
- Auto-updates when contractors reach out to subcontractors
- Provides manual update endpoints for maintenance
- Is cached for performance
- Works seamlessly with your existing outreach tracking system
