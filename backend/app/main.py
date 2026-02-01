from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from app.routes import auth, dataset, history
from app.utils.firebase_config import initialize_firebase

# Get environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# Configure logging
log_level = logging.WARNING if IS_PRODUCTION else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Firebase
try:
    initialize_firebase()
    logger.info("Firebase initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {str(e)}")
    raise

app = FastAPI(
    title="PrepIt API",
    description="Data preprocessing and analytics platform with Supabase storage and history tracking",
    version="2.0.0",
    docs_url="/docs" if not IS_PRODUCTION else None,  # Disable docs in production
    redoc_url="/redoc" if not IS_PRODUCTION else None
)

# CORS Configuration - Production Ready
allowed_origins = [
    "https://prepit-data.vercel.app",  # Production frontend
    "http://localhost:3000",  # Local development
    "http://127.0.0.1:3000",  # Local development alternative
]

# In development, allow all origins for easier testing
if not IS_PRODUCTION:
    allowed_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dataset.router, prefix="/api/dataset", tags=["Dataset"])
app.include_router(history.router, prefix="/api/history", tags=["History"])

@app.get("/")
async def root():
    return {
        "message": "PrepIt API is running",
        "version": "2.0.0",
        "status": "healthy",
        "environment": ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring services"""
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "services": {
            "api": "running",
            "firebase": "connected",
            "preprocessing": "available",
            "history": "enabled",
            "storage": "supabase"
        }
    }


@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info(f"Starting PrepIt API in {ENVIRONMENT} mode")
    logger.info(f"CORS origins: {allowed_origins}")
    logger.info(f"API Documentation: {'Disabled' if IS_PRODUCTION else 'Enabled'}")
