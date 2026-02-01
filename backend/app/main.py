from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, dataset
from app.utils.firebase_config import initialize_firebase

# Initialize Firebase
initialize_firebase()

app = FastAPI(
    title="PrepIt API",
    description="Data preprocessing and analytics platform",
    version="1.0.0"
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

@app.get("/")
async def root():
    return {"message": "PrepIt API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
