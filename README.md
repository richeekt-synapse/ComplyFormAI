# 🏗️ Subcontractor Bidding System Schema

This repository outlines a minimal **SQL schema** designed to manage **organizations**, **subcontractors**, their **certifications**, the **bids** they participate in, and the associated **validation results**.

It serves as a foundational structure for a system that tracks subcontractors' involvement in various bids, including necessary compliance checks.

---

## 🛠️ Schema Overview

The database is composed of the following tables:

| Table Name | Description | Key Fields | Notes |
| :--- | :--- | :--- | :--- |
| **`organizations`** | Primary entities (e.g., general contractors or clients). | `organization_id`, `name` | Minimal information for organizational identity. |
| **`subcontractors`** | The companies submitting bids and performing work. | `subcontractor_id`, `name`, `certification_number`, `naics_code` | Includes basic identification and key compliance data. |
| **`certifications`** | A catalog of available compliance or industry certifications. | `certification_id`, `name`, `description` | Standard list of certifications. |
| **`bids`** | Records for each project or contracting opportunity. | `bid_id`, `name`, `date_submitted`, `organization_id` (FK) | Basic information about the bid itself. |
| **`bid_subcontractors`** | **Junction Table** linking which subcontractors are involved in which bids. | `bid_subcontractor_id`, `bid_id` (FK), `subcontractor_id` (FK) | Establishes a many-to-many relationship. |
| **`validation_results`** | Stores the outcome of compliance/eligibility checks. | `validation_id`, `bid_subcontractor_id` (FK), `status`, `notes` | Tracks if a subcontractor is valid for a specific bid. |

---

## 🚀 Setup Status

The repository currently includes the following foundational data and structure:

1.  **Minimal Schema:** The tables listed above have been created with basic field definitions and primary/foreign keys.
2.  **NAICS Data:** A set of sample **NAICS codes** (North American Industry Classification System) has been loaded to support the `subcontractors` table.
3.  **Seed Data:** **3 to 5 sample subcontractors** have been created to populate the database and allow for initial testing and querying.

---

## 💡 Next Steps

To build upon this foundation, consider the following development tasks:

* **Detailed Field Definitions:** Expand the tables with required fields (e.g., addresses, contact info, bid amounts).
* **Relationship Constraints:** Implement robust **foreign key constraints** and indexing for performance.
* **API/Application Layer:** Build an application (e.g., Python, Node.js) to interact with this database.
* **Comprehensive Seed Data:** Create a larger set of realistic dummy data for robust testing.