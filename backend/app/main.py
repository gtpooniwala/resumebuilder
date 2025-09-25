from fastapi import FastAPI
from app.api.routes import router as api_router
from app.api.profile_routes import router as profile_router
from app.database.connection import create_tables

app = FastAPI()

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