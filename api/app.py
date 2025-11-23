"""
FastAPI Application for AI-Enhanced Nurse Scheduler
HealthFlow RegTech - Egypt's Digital Health Infrastructure
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

app = FastAPI(
    title="AI-Enhanced Nurse Scheduler API",
    description="Intelligent nurse scheduling system for Egyptian healthcare",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HealthCheck(BaseModel):
    status: str
    timestamp: str
    version: str

class NurseInput(BaseModel):
    id: str
    name: str
    name_ar: Optional[str] = None
    skill_level: str = "INTERMEDIATE"
    max_hours_per_week: int = 48

class ScheduleRequest(BaseModel):
    nurses: List[NurseInput]
    start_date: str
    end_date: str
    department: str = "General"

class ScheduleResponse(BaseModel):
    status: str
    message: str
    schedule_id: Optional[str] = None

# Routes
@app.get("/", response_model=HealthCheck)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/schedule", response_model=ScheduleResponse)
async def create_schedule(request: ScheduleRequest):
    """Create a new nurse schedule"""
    try:
        # This is a placeholder - actual scheduling logic would go here
        return {
            "status": "success",
            "message": f"Schedule created for {len(request.nurses)} nurses from {request.start_date} to {request.end_date}",
            "schedule_id": f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/info")
async def get_info():
    """Get system information"""
    return {
        "name": "AI-Enhanced Nurse Scheduler",
        "organization": "HealthFlow RegTech",
        "country": "Egypt",
        "features": [
            "Branch-and-price optimization",
            "LSTM demand forecasting",
            "XGBoost fatigue prediction",
            "Ramadan-aware scheduling",
            "Egyptian labor law compliance",
            "Arabic language support"
        ],
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
