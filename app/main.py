from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import (
    bids_router,
    subcontractors_router,
    organizations_router,
    jurisdictions_router,
    directory_router,
    opportunities_router,
    assessments_router,
    outreach_router
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    description="ComplyFormAI Enhanced Backend - Compliance-First Platform"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5432"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "2.0 - Enhanced Edition"
    }

# Include routers
app.include_router(organizations_router, prefix=settings.API_V1_PREFIX)
app.include_router(jurisdictions_router, prefix=settings.API_V1_PREFIX)
app.include_router(bids_router, prefix=settings.API_V1_PREFIX)
app.include_router(subcontractors_router, prefix=settings.API_V1_PREFIX)
app.include_router(directory_router, prefix=settings.API_V1_PREFIX)
app.include_router(opportunities_router, prefix=settings.API_V1_PREFIX)
app.include_router(assessments_router, prefix=settings.API_V1_PREFIX)
app.include_router(outreach_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "message": "Welcome to ComplyFormAI Enhanced API",
        "version": "2.0",
        "features": [
            "Cross-form validation",
            "Pre-bid assessment",
            "Multi-jurisdiction support",
            "Subcontractor directory & matching",
            "Opportunity alerts",
            "Outreach tracking"
        ],
        "docs": "/docs",
        "health": "/health"
    }