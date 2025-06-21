# app/api/api.py
# This file aggregates all the different API routers into a single main router.
# Author: Shibo Li
# Date: 2025-06-21
# Version: 0.1.0

from fastapi import APIRouter
from app.api.routes import optimization

api_router = APIRouter()

# Include routers from different modules here
api_router.include_router(optimization.router, prefix="/optimize", tags=["Optimization"])
