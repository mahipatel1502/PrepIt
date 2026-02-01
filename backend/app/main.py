from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.routes import auth, dataset, history
from app.utils.firebase_config import initialize_firebase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Firebase
initialize_firebase()
logger.info("Firebase initialized successfully")

app = FastAPI(
    title="PrepIt API",
    description="Data preprocessing and analytics platform with Supabase storage and history tracking",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "firebase": "connected",
            "preprocessing": "available",
            "history": "enabled"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
