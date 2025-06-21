# app/main.py
# This is the main entry point of the FastAPI application.
# Author: Shibo Li
# Date: 2025-06-21
# Version: 0.1.0

from fastapi import FastAPI
from app.api.api import api_router

app = FastAPI(
    title="DFTB+ Automation Service",
    description="A modular service to run computational chemistry tasks with DFTB+.",
    version="0.1.0" # Version updated to reflect new architecture
)

# Include the main router from the api module
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the DFTB+ Automation Service!"}