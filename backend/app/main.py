"""
DataCrunch API - Main Application Entry Point

This module initializes the FastAPI application with CORS middleware,
routers, and lifecycle events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configuration
from app.core.config import settings
# Routes
from app.api.routes import ai_routes

app = FastAPI(
    title="DataCrunch API",
    description="High-performance data processing API with Excel-like UX",
    version="0.1.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Root endpoint for health check.
    
    Returns:
        dict: API status and version information.
    
    Source/Caller:
        - Called by: Health check monitors, initial connection tests
    """
    return {
        "message": "DataCrunch API",
        "version": "0.1.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: Service health status.
    
    Source/Caller:
        - Called by: Load balancers, monitoring systems
    """
    return {"status": "healthy"}


# Register AI routes
app.include_router(ai_routes.router, prefix="/api/v1/ai", tags=["AI"])
