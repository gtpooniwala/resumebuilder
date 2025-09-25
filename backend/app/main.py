from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume Builder API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(api_router)

# TODO: Implement user management for multiple users in the future.