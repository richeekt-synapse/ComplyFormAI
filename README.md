# 🏗️ ComplyFormAI – FastAPI Backend

A compliance management API for validating MBE participation in construction bids.

---

## 🚀 Installation & Setup Guide

### 1️⃣ Clone the Repository

Open your terminal (or VS Code terminal) and run:

```bash
git clone https://github.com/veer-kat/ComplyFormAI.git
cd ComplyFormAI
```

### 2️⃣ Set Up PostgreSQL Database

1. Open pgAdmin.

2. Create a new database named: ComplyFormAI

Inside the repo, you’ll find SQL files.

Run them in the following order in pgAdmin query tool:
-- Step 1
minimal_schema.sql;

-- Step 2
load_naics.sql;

-- Step 3
seed_data.sql;

### 3️⃣ Create .env File

Inside the root folder of your FastAPI project, create a .env file and add:

`DATABASE_URL=postgresql://postgres:password@localhost:5432/ComplyFormAI
DEBUG=True`

### 4️⃣ Set Up Virtual Environment

Use Python 3.12 (recommended) for smooth installation.

`python -m venv venv`

Activate it:

Terminal:
`.\venv\Scripts\activate`

### 5️⃣ Install Dependencies

`pip install -r requirements.txt`

### 6️⃣ Test Database Connection

Run the connection test script:

`python test_connection.py`

### 7️⃣ Run the FastAPI Server

`python run.py`

## 🧪 API Testing (Postman)

Below are the available endpoints with example requests.

✅ Health Check
`GET http://localhost:8000/health
`

### 2️⃣ Organizations Endpoints

#### ➕ Create Organization

`POST http://localhost:8000/api/v1/organizations/
Content-Type: application/json

{
  "name": "ABC Construction Company"
}
`

Save the id as {{org_id}}

#### 📋 List All Organizations

`GET http://localhost:8000/api/v1/organizations/
`

#### 🔍 Get Organization by ID

`GET http://localhost:8000/api/v1/organizations/{{org_id}}
`

### 3️⃣ Subcontractors Endpoints

#### ➕ Create Subcontractor (MBE)

`POST http://localhost:8000/api/v1/subcontractors/
Content-Type: application/json

{
  "organization_id": "{{org_id}}",
  "legal_name": "Elite Steel Fabricators Inc.",
  "certification_number": "MBE-2024-001",
  "is_mbe": true
}
`

Save the id as {{subcontractor_1_id}}

#### 📋 List All Subcontractors

`GET http://localhost:8000/api/v1/subcontractors/
`

#### 🔎 Search Subcontractors (by name)

`GET http://localhost:8000/api/v1/subcontractors/search?q=Steel
`

#### 🔎 Search MBE Subcontractors Only

`GET http://localhost:8000/api/v1/subcontractors/search?is_mbe=true
`

#### 🔍 Get Subcontractor by ID

`GET http://localhost:8000/api/v1/subcontractors/{{subcontractor_1_id}}
`

#### ✏️ Update Subcontractor

`PUT http://localhost:8000/api/v1/subcontractors/{{subcontractor_1_id}}
Content-Type: application/json

{
  "legal_name": "Elite Steel Fabricators Inc. (Updated)",
  "certification_number": "MBE-2024-001-RENEWED"
}
`

#### ❌ Delete Subcontractor

`DELETE http://localhost:8000/api/v1/subcontractors/{{subcontractor_3_id}}
`

### 4️⃣ Bids Endpoints

#### ➕ Create Bid

`POST http://localhost:8000/api/v1/bids/
Content-Type: application/json

{
  "organization_id": "{{org_id}}",
  "solicitation_number": "DOT-2025-12345",
  "total_amount": 1000000.00,
  "mbe_goal": 25.00
}
`

Save the id as {{bid_id}}

#### 📋 List All Bids

`GET http://localhost:8000/api/v1/bids/
`

#### 🔍 Get Bid by ID (with details)

`GET http://localhost:8000/api/v1/bids/{{bid_id}}
`

### 5️⃣ Bid Subcontractors

#### ➕ Add Subcontractor to Bid

`POST http://localhost:8000/api/v1/bids/{{bid_id}}/subcontractors
Content-Type: application/json

{
  "subcontractor_id": "{{subcontractor_1_id}}",
  "work_description": "Steel fabrication and structural framework",
  "naics_code": "236220",
  "subcontract_value": 200000.00,
  "counts_toward_mbe": true
}
`

Save the id as {{bid_sub_1_id}}

#### ❌ Remove Subcontractor from Bid

`DELETE http://localhost:8000/api/v1/bids/{{bid_id}}/subcontractors/{{bid_sub_2_id}}
`

### 6️⃣ Validation Endpoints

#### ✅ Validate Bid (Check MBE %)

`GET http://localhost:8000/api/v1/bids/{{bid_id}}/validate
`

### 7️⃣ Test Scenario: MBE Goal Not Met

Add additional MBE subcontractor:

`POST http://localhost:8000/api/v1/bids/{{bid_id}}/subcontractors
Content-Type: application/json

{
  "subcontractor_id": "{{subcontractor_2_id}}",
  "work_description": "Additional MBE work to meet goal",
  "naics_code": "561730",
  "subcontract_value": 50000.00,
  "counts_toward_mbe": true
}
`

Then re-validate:

`GET http://localhost:8000/api/v1/bids/{{bid_id}}/validate
`

### 8️⃣ Error Testing

#### ❗ 404 - Bid Not Found

`GET http://localhost:8000/api/v1/bids/00000000-0000-0000-0000-000000000000
`

## 🧰 Tech Stack

Backend: FastAPI
Database: PostgreSQL
ORM: SQLAlchemy
Environment: Python 3.12
Testing: Postman