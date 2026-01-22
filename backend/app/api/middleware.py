"""
Middleware for HRM Decision System API
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
import time
import logging

logger = logging.getLogger(__name__)


async def request_logging_middleware(request: Request, call_next):
    """Log all incoming requests"""
    
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    logger.info(f"Response: {response.status_code} - Duration: {duration:.3f}s")
    
    # Add custom header
    response.headers["X-Process-Time"] = str(duration)
    
    return response


async def error_handling_middleware(request: Request, call_next):
    """Global error handling"""
    
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(e)
            }
        )


def setup_middleware(app):
    """Setup all middleware"""
    
    app.middleware("http")(request_logging_middleware)
    app.middleware("http")(error_handling_middleware)
    
    logger.info("Middleware configured")
