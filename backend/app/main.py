import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.api.profile_routes import router as profile_router
from app.database.connection import create_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Set specific loggers to appropriate levels
logging.getLogger("app.services.chat_service").setLevel(logging.INFO)
logging.getLogger("app.services.resume_tools").setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.WARNING)  # Reduce HTTP client noise
logging.getLogger("httpx").setLevel(logging.WARNING)     # Reduce HTTP client noise

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume Builder API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(api_router)
app.include_router(profile_router, prefix="/api")
