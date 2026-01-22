"""
FastAPI Application Entry Point

Main API server for HRM Decision System
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .api.routes import router
from .api.chat import router as chat_router
from .api.decision import router as decision_router
from .api.middleware import setup_middleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="HRM Decision System API",
    description="Hybrid Decision-Making System combining LLM interpretation with Hierarchical Reasoning Model",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup custom middleware
setup_middleware(app)

# Include API routes
app.include_router(router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(decision_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HRM Decision System API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "hrm-decision-system",
        "components": {
            "api": "ok",
            "preprocessor": "ok",
            "llm_interpreter": "ok",
            "hrm_engine": "ok",
            "action_executor": "ok"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
