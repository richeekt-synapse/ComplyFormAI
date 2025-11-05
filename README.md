# ComplyFormAI Enhanced Backend
## Version 2.0 - Compliance-First Platform Edition

This enhanced backend implements all the features outlined in the ComplyFormAI Enhanced Prototype Plan, transforming the system from a simple validation tool into a comprehensive compliance platform.

## 🚀 New Features

### 1. **Multi-Jurisdiction Support**
- Support for Maryland (MD), District of Columbia (DC), and extensible to other jurisdictions
- Jurisdiction-specific compliance rules
- Typical MBE/VSBE goals per jurisdiction

### 2. **Pre-Bid Assessment** (Bid/No-Bid Intelligence)
- Comprehensive risk scoring (0-100)
- MBE/VSBE gap analysis
- Available subcontractor count analysis
- Smart recommendations: BID, CAUTION, or NO_BID
- Detailed risk factors and recommendations

### 3. **Subcontractor Directory & Matching**
- Searchable directory of subcontractors
- Advanced filtering by:
  - Jurisdiction codes
  - NAICS codes
  - MBE/VSBE certification
  - Verification status
  - Rating
- Intelligent matching algorithm for opportunities
- Network effects foundation

### 4. **Opportunity Alerts**
- Procurement opportunity tracking
- Relevance scoring based on NAICS and jurisdiction
- Due date monitoring
- Active/inactive status management
- Search and filtering capabilities

### 5. **Subcontractor Outreach Tracking**
- Track communication with subcontractors
- Status management (CONTACTED, RESPONDED, COMMITTED, DECLINED)
- Outreach statistics and analytics
- Response rate and commit rate calculation

### 6. **Enhanced Validation** (Original Feature Improved)
- Cross-form validation
- Certification verification
- NAICS code validation
- MBE percentage compliance
- NAICS-certification matching

## 📁 Project Structure

```
app/
├── __init__.py
├── config.py              # Application configuration
├── database.py            # Database connection setup
├── main.py                # FastAPI application entry point
│
├── models/                # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── organization.py
│   ├── subcontractor.py
│   ├── certification.py
│   ├── bid.py
│   ├── bid_subcontractor.py
│   ├── validation_result.py
│   ├── naics_code.py
│   ├── jurisdiction.py              # NEW
│   ├── compliance_rule.py           # NEW
│   ├── subcontractor_directory.py   # NEW
│   ├── opportunity.py               # NEW
│   ├── pre_bid_assessment.py        # NEW
│   └── subcontractor_outreach.py    # NEW
│
├── schemas/               # Pydantic schemas for API
│   ├── __init__.py
│   ├── organization.py
│   ├── subcontractor.py
│   ├── bid.py
│   ├── validation.py
│   ├── jurisdiction.py              # NEW
│   ├── subcontractor_directory.py   # NEW
│   ├── opportunity.py               # NEW
│   ├── pre_bid_assessment.py        # NEW
│   └── subcontractor_outreach.py    # NEW
│
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── bid_service.py
│   ├── subcontractor_service.py
│   ├── validation_service.py
│   ├── jurisdiction_service.py              # NEW
│   ├── subcontractor_directory_service.py   # NEW
│   ├── opportunity_service.py               # NEW
│   ├── pre_bid_assessment_service.py        # NEW
│   └── subcontractor_outreach_service.py    # NEW
│
├── routes/                # FastAPI route handlers
│   ├── __init__.py
│   ├── organizations.py
│   ├── subcontractors.py
│   ├── bids.py
│   ├── jurisdictions.py             # NEW
│   ├── directory.py                 # NEW
│   ├── opportunities.py             # NEW
│   ├── assessments.py               # NEW
│   └── outreach.py                  # NEW
│
└── validation/            # Validation rules engine
    ├── __init__.py
    ├── engine.py
    └── rules.py
```

## 🔌 New API Endpoints

### Jurisdictions
```
POST   /api/v1/jurisdictions              - Create jurisdiction
GET    /api/v1/jurisdictions              - List all jurisdictions
GET    /api/v1/jurisdictions/{id}         - Get jurisdiction by ID
GET    /api/v1/jurisdictions/code/{code}  - Get jurisdiction by code
```

### Subcontractor Directory
```
POST   /api/v1/directory                      - Add to directory
GET    /api/v1/directory                      - List directory
POST   /api/v1/directory/search               - Advanced search
GET    /api/v1/directory/search/simple        - Simple query param search
GET    /api/v1/directory/{id}                 - Get directory entry
PUT    /api/v1/directory/{id}                 - Update directory entry
DELETE /api/v1/directory/{id}                 - Remove from directory
GET    /api/v1/directory/match/opportunity/{id} - Find matching subcontractors
```

### Opportunities
```
POST   /api/v1/opportunities                     - Create opportunity
GET    /api/v1/opportunities                     - List opportunities
POST   /api/v1/opportunities/search              - Advanced search
GET    /api/v1/opportunities/search/simple       - Simple query param search
GET    /api/v1/opportunities/{id}                - Get opportunity
GET    /api/v1/opportunities/jurisdiction/{id}   - Get by jurisdiction
PUT    /api/v1/opportunities/{id}                - Update opportunity
POST   /api/v1/opportunities/{id}/deactivate     - Deactivate opportunity
GET    /api/v1/opportunities/alerts/relevant     - Get relevant opportunities
```

### Pre-Bid Assessments
```
POST   /api/v1/assessments/perform                   - Perform assessment
GET    /api/v1/assessments/{id}                      - Get assessment
GET    /api/v1/assessments/organization/{id}         - Get org assessments
GET    /api/v1/assessments/organization/{id}/summary - Get assessment summary
```

### Subcontractor Outreach
```
POST   /api/v1/outreach                         - Create outreach record
GET    /api/v1/outreach/{id}                    - Get outreach record
GET    /api/v1/outreach/opportunity/{id}        - Get by opportunity
GET    /api/v1/outreach/organization/{id}       - Get by organization
GET    /api/v1/outreach/subcontractor/{id}      - Get by subcontractor
PUT    /api/v1/outreach/{id}                    - Update outreach
DELETE /api/v1/outreach/{id}                    - Delete outreach
GET    /api/v1/outreach/statistics/opportunity/{id}   - Get opportunity stats
GET    /api/v1/outreach/statistics/organization/{id}  - Get organization stats
```

## 🗄️ Database Schema

The enhanced backend requires the following new tables in PostgreSQL:

### New Tables
1. **jurisdictions** - Multi-jurisdiction support
2. **compliance_rules** - Jurisdiction-specific rules
3. **subcontractor_directory** - Searchable subcontractor network
4. **opportunities** - Procurement opportunities
5. **pre_bid_assessments** - Assessment results
6. **subcontractor_outreach** - Outreach tracking

### Original Tables (Retained)
1. **organizations**
2. **subcontractors**
3. **certifications**
4. **bids**
5. **bid_subcontractors**
6. **validation_results**
7. **naics_codes**

See the enhanced prototype plan document for complete SQL schema and seed data.

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 14+
- pip or conda

### Step 1: Install Dependencies

```bash
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install sqlalchemy==2.0.23
pip install psycopg2-binary==2.9.9
pip install pydantic-settings==2.1.0
pip install python-multipart==0.0.6
```

### Step 2: Configure Database

1. Create PostgreSQL database:
```sql
CREATE DATABASE ComplyFormAI;
```

2. Update `app/config.py` with your database credentials:
```python
DATABASE_URL: str = "postgresql://user:password@localhost:5432/ComplyFormAI"
```

Or use environment variables in `.env` file:
```
DATABASE_URL=postgresql://user:password@localhost:5432/ComplyFormAI
DEBUG=True
```

### Step 3: Create Database Tables

Run the SQL schema from the enhanced prototype plan to create all tables and populate with seed data.

### Step 4: Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## 📊 Key Service Features

### Pre-Bid Assessment Service

The assessment service performs intelligent analysis:

1. **Subcontractor Availability Check**
   - Finds MBE/VSBE subcontractors matching opportunity NAICS
   - Filters by jurisdiction
   - Considers rating and verification status

2. **Gap Analysis**
   - Calculates MBE goal shortfall
   - Calculates VSBE goal shortfall
   - Identifies critical gaps

3. **Risk Scoring** (0-100, higher = more risk)
   - +40 points: No MBE subcontractors available
   - +25 points: Limited MBE options (< 3)
   - +20 points: No VSBE subcontractors available
   - +15 points: High-value contract ($10M+)
   - +30 points: Less than 7 days until due
   - +15 points: 7-14 days until due

4. **Smart Recommendations**
   - **BID** (risk < 30): Good opportunity, proceed
   - **CAUTION** (risk 30-59): Proceed with care
   - **NO_BID** (risk ≥ 60): High risk, recommend passing

### Subcontractor Directory Service

Advanced search capabilities:

```python
# Example search
filters = SubcontractorSearchFilters(
    query="construction",
    jurisdiction_codes=["MD", "DC"],
    naics_codes=["236220"],
    is_mbe=True,
    is_verified=True,
    min_rating=3.0
)
results = service.search_subcontractors(filters)
```

### Opportunity Service

Relevance scoring algorithm:
- 40 points: NAICS code match
- 30 points: Jurisdiction match
- 15 points: Value in sweet spot ($100k-$5M)
- 15 points: Reasonable timeline (14-60 days)

## 🧪 Testing the API

### Example: Perform Pre-Bid Assessment

```bash
curl -X POST "http://localhost:8000/api/v1/assessments/perform" \
  -H "Content-Type: application/json" \
  -d '{
    "opportunity_id": "123e4567-e89b-12d3-a456-426614174000",
    "organization_id": "123e4567-e89b-12d3-a456-426614174001",
    "estimated_subcontract_percentage": 30.0
  }'
```

Response:
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
  "recommendation_reason": "LOW RISK: Good subcontractor availability...",
  "assessed_at": "2025-11-05T10:30:00",
  "risk_factors": [
    "GOOD: 5 MBE subcontractors available to meet 29.0% goal.",
    "GOOD: 21 days until due date. Adequate preparation time."
  ],
  "matching_subcontractors": [...]
}
```

### Example: Search Subcontractor Directory

```bash
curl -X POST "http://localhost:8000/api/v1/directory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "jurisdiction_codes": ["MD"],
    "naics_codes": ["236220"],
    "is_mbe": true,
    "min_rating": 3.0
  }'
```

### Example: Find Relevant Opportunities

```bash
curl -X GET "http://localhost:8000/api/v1/opportunities/alerts/relevant?organization_naics=236220&organization_naics=237310&organization_jurisdictions=MD&organization_jurisdictions=DC&min_relevance=60"
```
