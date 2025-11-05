# ComplyFormAI Enhanced API Endpoints Reference

## Base URL
`http://localhost:8000/api/v1`

## Table of Contents
1. [Organizations](#organizations)
2. [Subcontractors](#subcontractors)
3. [Bids](#bids)
4. [Jurisdictions](#jurisdictions-new)
5. [Subcontractor Directory](#subcontractor-directory-new)
6. [Opportunities](#opportunities-new)
7. [Pre-Bid Assessments](#pre-bid-assessments-new)
8. [Subcontractor Outreach](#subcontractor-outreach-new)

---

## Organizations

### Create Organization
**POST** `/organizations`

**Request Body:**
```json
{
  "name": "ABC Construction Inc."
}
```

**Response:** `201 Created`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "ABC Construction Inc."
}
```

### List Organizations
**GET** `/organizations`

**Response:** `200 OK`
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "ABC Construction Inc."
  }
]
```

### Get Organization
**GET** `/organizations/{organization_id}`

**Response:** `200 OK`

---

## Subcontractors

### Create Subcontractor
**POST** `/subcontractors`

**Request Body:**
```json
{
  "organization_id": "123e4567-e89b-12d3-a456-426614174000",
  "legal_name": "XYZ Electrical Services",
  "certification_number": "MBE-12345",
  "is_mbe": true
}
```

### List Subcontractors
**GET** `/subcontractors?organization_id={id}`

### Search Subcontractors
**GET** `/subcontractors/search?q={query}&is_mbe={bool}`

### Get Subcontractor
**GET** `/subcontractors/{subcontractor_id}`

### Update Subcontractor
**PUT** `/subcontractors/{subcontractor_id}`

### Delete Subcontractor
**DELETE** `/subcontractors/{subcontractor_id}`

---

## Bids

### Create Bid
**POST** `/bids`

**Request Body:**
```json
{
  "organization_id": "123e4567-e89b-12d3-a456-426614174000",
  "solicitation_number": "MDOT-2024-001",
  "total_amount": 1000000.00,
  "mbe_goal": 29.0
}
```

### List Bids
**GET** `/bids?organization_id={id}`

### Get Bid
**GET** `/bids/{bid_id}`

### Add Subcontractor to Bid
**POST** `/bids/{bid_id}/subcontractors`

**Request Body:**
```json
{
  "subcontractor_id": "123e4567-e89b-12d3-a456-426614174001",
  "work_description": "Electrical work for new facility",
  "naics_code": "238210",
  "subcontract_value": 150000.00,
  "counts_toward_mbe": true
}
```

### Remove Subcontractor from Bid
**DELETE** `/bids/{bid_id}/subcontractors/{bid_subcontractor_id}`

### Validate Bid
**GET** `/bids/{bid_id}/validate`

**Response:** `200 OK`
```json
{
  "bid_id": "123e4567-e89b-12d3-a456-426614174000",
  "overall_status": "PASS",
  "total_validations": 4,
  "passed": 4,
  "failed": 0,
  "warnings": 0,
  "validations": [
    {
      "id": "...",
      "bid_id": "...",
      "rule_name": "certification_exists",
      "status": "PASS",
      "error_message": "All subcontractors have valid certifications",
      "created_at": "2025-11-05T10:30:00"
    }
  ]
}
```

---

## Jurisdictions (NEW)

### Create Jurisdiction
**POST** `/jurisdictions`

**Request Body:**
```json
{
  "code": "MD",
  "name": "Maryland State",
  "mbe_goal_typical": 29.0,
  "vsbe_goal_typical": 10.0
}
```

### List Jurisdictions
**GET** `/jurisdictions`

**Response:** `200 OK`
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "code": "MD",
    "name": "Maryland State",
    "mbe_goal_typical": 29.0,
    "vsbe_goal_typical": 10.0
  },
  {
    "id": "123e4567-e89b-12d3-a456-426614174001",
    "code": "DC",
    "name": "District of Columbia",
    "mbe_goal_typical": 35.0,
    "vsbe_goal_typical": 12.0
  }
]
```

### Get Jurisdiction by ID
**GET** `/jurisdictions/{jurisdiction_id}`

### Get Jurisdiction by Code
**GET** `/jurisdictions/code/{code}`

**Example:** `GET /jurisdictions/code/MD`

---

## Subcontractor Directory (NEW)

### Add to Directory
**POST** `/directory`

**Request Body:**
```json
{
  "legal_name": "Elite HVAC Solutions",
  "federal_id": "12-3456789",
  "certifications": {
    "mbe": true,
    "vsbe": true,
    "dbe": false
  },
  "jurisdiction_codes": ["MD", "DC"],
  "naics_codes": ["238220", "238290"],
  "capabilities": "HVAC installation, maintenance, and repair",
  "contact_email": "contact@elitehvac.com",
  "phone": "555-0123",
  "location_city": "Baltimore",
  "rating": 4.5,
  "projects_completed": 45,
  "is_verified": true
}
```

**Response:** `201 Created`

### List Directory
**GET** `/directory?skip=0&limit=100`

### Advanced Search
**POST** `/directory/search`

**Request Body:**
```json
{
  "query": "construction",
  "jurisdiction_codes": ["MD", "DC"],
  "naics_codes": ["236220"],
  "is_mbe": true,
  "is_vsbe": null,
  "is_verified": true,
  "min_rating": 3.0
}
```

**Response:** `200 OK`
```json
[
  {
    "id": "...",
    "legal_name": "Elite Construction Co",
    "federal_id": "12-3456789",
    "certifications": {
      "mbe": true,
      "vsbe": true
    },
    "jurisdiction_codes": ["MD", "DC"],
    "naics_codes": ["236220", "237310"],
    "capabilities": "Commercial construction",
    "contact_email": "info@eliteconst.com",
    "phone": "555-0100",
    "location_city": "Silver Spring",
    "rating": 4.2,
    "projects_completed": 32,
    "is_verified": true,
    "created_at": "2025-10-01T00:00:00"
  }
]
```

### Simple Search (Query Params)
**GET** `/directory/search/simple?q=construction&jurisdiction=MD&is_mbe=true&min_rating=3.0`

### Get Directory Entry
**GET** `/directory/{subcontractor_id}`

### Update Directory Entry
**PUT** `/directory/{subcontractor_id}`

**Request Body:**
```json
{
  "rating": 4.8,
  "projects_completed": 50,
  "is_verified": true
}
```

### Remove from Directory
**DELETE** `/directory/{subcontractor_id}`

### Find Matching Subcontractors for Opportunity
**GET** `/directory/match/opportunity/{opportunity_id}?is_mbe=true&min_rating=2.0`

**Response:** List of matching subcontractors

---

## Opportunities (NEW)

### Create Opportunity
**POST** `/opportunities`

**Request Body:**
```json
{
  "solicitation_number": "MDOT-2025-042",
  "title": "Highway Bridge Rehabilitation Project",
  "jurisdiction_id": "123e4567-e89b-12d3-a456-426614174000",
  "agency": "Maryland Department of Transportation",
  "mbe_goal": 29.0,
  "vsbe_goal": 10.0,
  "total_value": 2500000.00,
  "naics_codes": ["237310", "238120"],
  "due_date": "2025-12-15",
  "opportunity_url": "https://procurement.maryland.gov/...",
  "is_active": true,
  "posted_date": "2025-11-01"
}
```

**Response:** `201 Created`

### List Opportunities
**GET** `/opportunities?skip=0&limit=100&is_active=true`

**Response:** `200 OK`
```json
[
  {
    "id": "...",
    "solicitation_number": "MDOT-2025-042",
    "title": "Highway Bridge Rehabilitation Project",
    "jurisdiction_id": "...",
    "agency": "Maryland Department of Transportation",
    "mbe_goal": 29.0,
    "vsbe_goal": 10.0,
    "total_value": 2500000.00,
    "naics_codes": ["237310", "238120"],
    "due_date": "2025-12-15",
    "posted_date": "2025-11-01",
    "opportunity_url": "https://...",
    "is_active": true,
    "relevance_score": 85,
    "jurisdiction": {
      "id": "...",
      "code": "MD",
      "name": "Maryland State",
      "mbe_goal_typical": 29.0,
      "vsbe_goal_typical": 10.0
    }
  }
]
```

### Advanced Search
**POST** `/opportunities/search`

**Request Body:**
```json
{
  "jurisdiction_codes": ["MD", "DC"],
  "naics_codes": ["237310"],
  "min_value": 100000.00,
  "max_value": 5000000.00,
  "is_active": true,
  "days_until_due": 30
}
```

### Simple Search (Query Params)
**GET** `/opportunities/search/simple?jurisdiction=MD&naics=237310&min_value=100000&is_active=true`

### Get Opportunity
**GET** `/opportunities/{opportunity_id}`

### Get Opportunities by Jurisdiction
**GET** `/opportunities/jurisdiction/{jurisdiction_id}`

### Update Opportunity
**PUT** `/opportunities/{opportunity_id}`

### Deactivate Opportunity
**POST** `/opportunities/{opportunity_id}/deactivate`

### Get Relevant Opportunities (Alert Feature)
**GET** `/opportunities/alerts/relevant?organization_naics=237310&organization_naics=238120&organization_jurisdictions=MD&organization_jurisdictions=DC&min_relevance=50`

**Response:** List of opportunities sorted by relevance score

**Relevance Score Calculation:**
- 40 points: NAICS code match
- 30 points: Jurisdiction match
- 15 points: Value in sweet spot ($100k-$5M)
- 15 points: Reasonable timeline (14-60 days)
- Max score: 100

---

## Pre-Bid Assessments (NEW)

### Perform Assessment
**POST** `/assessments/perform`

**Request Body:**
```json
{
  "opportunity_id": "123e4567-e89b-12d3-a456-426614174000",
  "organization_id": "123e4567-e89b-12d3-a456-426614174001",
  "estimated_subcontract_percentage": 30.0
}
```

**Response:** `200 OK`
```json
{
  "id": "...",
  "organization_id": "...",
  "opportunity_id": "...",
  "overall_risk_score": 25,
  "mbe_gap_percentage": 0.0,
  "vsbe_gap_percentage": 0.0,
  "available_subcontractors_count": 8,
  "recommendation": "BID",
  "recommendation_reason": "LOW RISK: Good subcontractor availability and reasonable timeline. Strong opportunity to pursue.",
  "assessed_at": "2025-11-05T10:30:00",
  "risk_factors": [
    "GOOD: 5 MBE subcontractors available to meet 29.0% goal.",
    "GOOD: 3 VSBE subcontractors available.",
    "GOOD: 21 days until due date. Adequate preparation time.",
    "INFO: Contract value $2.5M is in optimal range."
  ],
  "matching_subcontractors": [
    {
      "id": "...",
      "legal_name": "Elite Construction Co",
      "certifications": {"mbe": true},
      "rating": 4.2,
      "projects_completed": 32
    }
  ],
  "opportunity": {
    "id": "...",
    "solicitation_number": "MDOT-2025-042",
    "title": "Highway Bridge Rehabilitation Project",
    "mbe_goal": 29.0,
    "vsbe_goal": 10.0,
    "total_value": 2500000.00,
    "due_date": "2025-12-15"
  }
}
```

**Risk Score Breakdown:**
- 0-29: **LOW RISK** → Recommendation: **BID**
- 30-59: **MODERATE RISK** → Recommendation: **CAUTION**
- 60-100: **HIGH RISK** → Recommendation: **NO_BID**

**Risk Factors:**
- +40: No MBE subcontractors available (CRITICAL)
- +25: Limited MBE options (< 3)
- +20: No VSBE subcontractors available
- +10: Limited VSBE options (< 2)
- +15: High-value contract ($10M+)
- +30: Less than 7 days until due (CRITICAL)
- +15: 7-14 days until due

### Get Assessment
**GET** `/assessments/{assessment_id}`

### Get Organization Assessments
**GET** `/assessments/organization/{organization_id}`

**Response:** List of all assessments for the organization

### Get Assessment Summary
**GET** `/assessments/organization/{organization_id}/summary`

**Response:** `200 OK`
```json
{
  "total_assessments": 15,
  "bid_recommended": 8,
  "caution_recommended": 5,
  "no_bid_recommended": 2,
  "average_risk_score": 32.5
}
```

---

## Subcontractor Outreach (NEW)

### Create Outreach Record
**POST** `/outreach`

**Request Body:**
```json
{
  "organization_id": "123e4567-e89b-12d3-a456-426614174000",
  "opportunity_id": "123e4567-e89b-12d3-a456-426614174001",
  "subcontractor_id": "123e4567-e89b-12d3-a456-426614174002",
  "status": "CONTACTED",
  "notes": "Initial email sent, awaiting response",
  "contact_date": "2025-11-05"
}
```

**Status Options:**
- `CONTACTED`: Initial contact made
- `RESPONDED`: Subcontractor responded
- `COMMITTED`: Subcontractor committed to project
- `DECLINED`: Subcontractor declined

**Response:** `201 Created`

### Get Outreach Record
**GET** `/outreach/{outreach_id}`

### Get Outreach by Opportunity
**GET** `/outreach/opportunity/{opportunity_id}`

**Response:** List of all outreach records for an opportunity

### Get Outreach by Organization
**GET** `/outreach/organization/{organization_id}`

**Response:** List of all outreach records for an organization

### Get Outreach by Subcontractor
**GET** `/outreach/subcontractor/{subcontractor_id}`

**Response:** List of all outreach records for a subcontractor

### Update Outreach
**PUT** `/outreach/{outreach_id}`

**Request Body:**
```json
{
  "status": "COMMITTED",
  "notes": "Subcontractor agreed to 15% of project scope. Quote received."
}
```

### Delete Outreach
**DELETE** `/outreach/{outreach_id}`

### Get Opportunity Outreach Statistics
**GET** `/outreach/statistics/opportunity/{opportunity_id}`

**Response:** `200 OK`
```json
{
  "total_outreach": 12,
  "contacted": 12,
  "responded": 8,
  "committed": 5,
  "declined": 3,
  "response_rate": 66.67,
  "commit_rate": 41.67
}
```

### Get Organization Outreach Statistics
**GET** `/outreach/statistics/organization/{organization_id}`

**Response:** Similar format, but aggregated across all opportunities

---

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Pagination

List endpoints support pagination:

**Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100, max: 500)

**Example:**
```
GET /opportunities?skip=20&limit=10
```

---

## Authentication (Future Enhancement)

Currently, the API does not require authentication. For production:

1. Add JWT token authentication
2. Include token in Authorization header:
   ```
   Authorization: Bearer <token>
   ```

---

## Rate Limiting (Future Enhancement)

Consider implementing rate limiting for production:
- 100 requests per minute per IP
- 1000 requests per hour per authenticated user

---

## API Versioning

Current version: **v1**

Base path: `/api/v1`

Future versions will use: `/api/v2`, `/api/v3`, etc.

---

## Interactive Documentation

Access interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Test all endpoints
- View request/response schemas
- See example data
- Execute API calls directly from browser

---

**Last Updated**: November 5, 2025  
**API Version**: 2.0 (Enhanced Edition)