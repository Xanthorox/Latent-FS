"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import settings
from backend.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Latent-FS API",
    description="Vector database visualization through a file system interface",
    version="1.0.0"
)

# ============================================================================
# Global Exception Handlers
# ============================================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions with consistent error response format.
    
    Returns appropriate HTTP status codes with descriptive error messages.
    """
    logger.error(
        f"HTTP {exc.status_code} error on {request.method} {request.url.path}: {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "status_code": exc.status_code,
                "message": exc.detail,
                "path": str(request.url.path)
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors (Pydantic validation failures).
    
    Returns 422 Unprocessable Entity with detailed validation error information.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error on {request.method} {request.url.path}: {errors}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "validation_error",
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "Request validation failed",
                "details": errors,
                "path": str(request.url.path)
            }
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Handle ValueError exceptions (invalid input values).
    
    Returns 400 Bad Request with error details.
    """
    logger.error(
        f"ValueError on {request.method} {request.url.path}: {str(exc)}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "type": "value_error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid input value",
                "details": str(exc),
                "path": str(request.url.path)
            }
        }
    )


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    """
    Handle RuntimeError exceptions (operational failures).
    
    Returns 500 Internal Server Error for runtime issues.
    """
    logger.error(
        f"RuntimeError on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "runtime_error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An operational error occurred",
                "details": str(exc),
                "path": str(request.url.path)
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unexpected exceptions.
    
    Returns 500 Internal Server Error with generic message.
    Logs full exception details for debugging.
    """
    logger.error(
        f"Unexpected error on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )
    
    # Don't expose internal error details in production
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "internal_error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred. Please try again later.",
                "path": str(request.url.path)
            }
        }
    )


# ============================================================================
# Middleware Configuration
# ============================================================================

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3008",
        "http://localhost:3009",
    ],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["documents"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Latent-FS API",
        "device": settings.DEVICE
    }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print(f"Starting Latent-FS API on device: {settings.DEVICE}")
    print(f"Embedding model: {settings.EMBEDDING_MODEL}")
    
    # Initialize database and check if it's empty
    try:
        from backend.services.database import ChromaDBManager
        from backend.services.embedding import EmbeddingService
        from backend.services.mock_data import populate_database_with_mock_data
        
        db_manager = ChromaDBManager(persist_directory=settings.CHROMA_PERSIST_DIR)
        doc_count = db_manager.count_documents()
        
        if doc_count == 0:
            print("Database is empty. Populating with mock data...")
            embedding_service = EmbeddingService(
                model_name=settings.EMBEDDING_MODEL,
                device=settings.DEVICE
            )
            
            num_docs = populate_database_with_mock_data(db_manager, embedding_service)
            print(f"Successfully added {num_docs} mock documents to the database")
        else:
            print(f"Database already contains {doc_count} documents")
            
    except Exception as e:
        print(f"Warning: Failed to initialize mock data: {e}")
        # Don't fail startup if mock data initialization fails

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9999, reload=True)
