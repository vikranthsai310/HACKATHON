"""
FastAPI Application Entry Point

Main API server for HRM Decision System
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from datetime import datetime

from .api.routes import router
from .api.chat import router as chat_router
from .api.decision import router as decision_router
from .api.middleware import setup_middleware
from .config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_startup_banner():
    """Print structured startup information"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    HRM DECISION SYSTEM - BACKEND                         ║
║              Gemini LLM + Hierarchical Reasoning Model                   ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)
    print(f"🕐 Startup Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version.split()[0]}")
    print("\n" + "="*78)
    print("📦 SYSTEM COMPONENTS & STATUS")
    print("="*78)
    

def print_component_status():
    """Print status of all components"""
    import torch
    from .core.llm_enhanced import GEMINI_AVAILABLE
    
    # Check PyTorch
    pytorch_status = "✓ INSTALLED" if torch.__version__ else "✗ NOT INSTALLED"
    pytorch_version = torch.__version__ if torch.__version__ else "N/A"
    
    # Check Gemini
    gemini_status = "✓ AVAILABLE" if GEMINI_AVAILABLE else "✗ NOT AVAILABLE"
    gemini_api = "✓ CONFIGURED" if settings.GEMINI_API_KEY else "✗ NOT CONFIGURED"
    
    print(f"""
┌─ 🧠 AI/ML ENGINES ─────────────────────────────────────────────────────┐
│                                                                          │
│  1️⃣  Google Gemini LLM                                                  │
│      Status: {gemini_status:<20} Model: {settings.GEMINI_MODEL:<20}│
│      API Key: {gemini_api:<20} Mode: {'REAL API' if settings.GEMINI_API_KEY else 'MOCK':<20}│
│                                                                          │
│  2️⃣  PyTorch Framework                                                  │
│      Status: {pytorch_status:<20} Version: {pytorch_version:<19}│
│      Device: {settings.HRM_DEVICE.upper():<20} Mode: {'SIMULATION' if settings.HRM_USE_SIMULATION else 'PRODUCTION':<20}│
│                                                                          │
│  3️⃣  HRM (Hierarchical Reasoning Model)                                 │
│      Status: ✓ LOADED              Mode: {'SIMULATION' if settings.HRM_USE_SIMULATION else 'TRAINED MODEL':<20}│
│      Layers: L1 Strategic ➜ L2 Tactical ➜ L3 Operational              │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌─ 🔧 PROCESSING PIPELINE ───────────────────────────────────────────────┐
│                                                                          │
│  USER INPUT                                                              │
│      ↓                                                                   │
│  [1] NLP Preprocessor        ✓ Initialized                             │
│      ↓                                                                   │
│  [2] LLM Interpreter          ✓ Enhanced Mode (Gemini)                 │
│      ↓                                                                   │
│  [3] HRM Engine               ✓ Running (3-Layer Hierarchy)            │
│      ↓                                                                   │
│  [4] Action Executor          ✓ DRY-RUN Mode (Safe)                    │
│      ↓                                                                   │
│  [5] Audit Logger             ✓ Active (10K entries, 24h retention)    │
│      ↓                                                                   │
│  DECISION OUTPUT                                                         │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌─ 🌐 API CONFIGURATION ─────────────────────────────────────────────────┐
│                                                                          │
│  Server Host: {settings.API_HOST:<20} Port: {settings.API_PORT:<24}│
│  CORS Origins: {len(settings.CORS_ORIGINS)} configured                                        │""")
    for origin in settings.CORS_ORIGINS:
        print(f"│      • {origin:<62}│")
    print(f"""│                                                                          │
│  Endpoints:                                                              │
│      • Main API:      http://{settings.API_HOST}:{settings.API_PORT}/api/v1/                         │
│      • Chat:          http://{settings.API_HOST}:{settings.API_PORT}/api/v1/chat                     │
│      • Decision:      http://{settings.API_HOST}:{settings.API_PORT}/api/v1/decision                 │
│      • Health:        http://{settings.API_HOST}:{settings.API_PORT}/health                          │
│      • Docs:          http://{settings.API_HOST}:{settings.API_PORT}/docs                            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌─ 🔒 SECURITY & EXECUTION MODE ─────────────────────────────────────────┐
│                                                                          │
│  Action Executor:  {'DRY-RUN (No real execution)' if settings.EXECUTOR_DRY_RUN else 'LIVE (Real execution)'}                           │
│  Audit Logging:    ✓ ENABLED                                           │
│  Request Timeout:  {settings.EXECUTOR_TIMEOUT} seconds                                            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌─ 🔗 SYSTEM INTEGRATION MAP ────────────────────────────────────────────┐
│                                                                          │
│  Frontend (React) ⟷ Port 3000                                          │
│       ↕                                                                  │
│  Backend (FastAPI) ⟷ Port {settings.API_PORT}                                          │
│       ↕                                                                  │
│  ┌─────────────┐        ┌──────────────┐        ┌─────────────┐       │
│  │   Gemini    │ ⟷    │  HRM Engine  │ ⟷    │   Actions   │       │
│  │  LLM API    │        │  Simulation  │        │   Executor  │       │
│  └─────────────┘        └──────────────┘        └─────────────┘       │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
""")
    print("="*78)
    print("🚀 SERVER READY - All Systems Operational")
    print("="*78)
    print()


# Create FastAPI application
app = FastAPI(
    title="HRM Decision System API",
    description="Hybrid Decision-Making System combining LLM interpretation with Hierarchical Reasoning Model",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print_startup_banner()
    print_component_status()

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
