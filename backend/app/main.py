import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.config import settings
from app.routers import chat


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

# Configure CORS for Cloud Run
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://health-informatics-frontend-593822281192.northamerica-northeast2.run.app",
        "https://health-informatics-frontend-593822281192.us-central1.run.app",  # Your frontend URL
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {"message": "Health Informatics API on Google Cloud Run", "status": "healthy"}

@app.get("/health")
def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "platform": "google-cloud-run"}

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")
    logger.info(f"Port: {os.environ.get('PORT', '8080')}")

# For Cloud Run
if __name__ == "__main__":
    
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)