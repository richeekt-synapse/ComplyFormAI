from app.routes.bids import router as bids_router
from app.routes.subcontractors import router as subcontractors_router
from app.routes.organizations import router as organizations_router
from app.routes.jurisdictions import router as jurisdictions_router
from app.routes.directory import router as directory_router
from app.routes.opportunities import router as opportunities_router
from app.routes.assessments import router as assessments_router
from app.routes.outreach import router as outreach_router

__all__ = [
    "bids_router",
    "subcontractors_router",
    "organizations_router",
    "jurisdictions_router",
    "directory_router",
    "opportunities_router",
    "assessments_router",
    "outreach_router"
]