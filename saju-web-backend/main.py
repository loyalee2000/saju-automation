from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from saju_app import SajuAnalyzer
import uvicorn
import os

app = FastAPI(title="Saju Web API", description="API for Saju Analysis (Onyul Clone)")

# Configurations for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SajuInput(BaseModel):
    name: Optional[str] = "Unknown"
    gender: str = "male"  # male or female
    year: int
    month: int
    day: int
    hour: int
    minute: int = 0
    calendarType: str = "solar" # solar or lunar
    isLeapMonth: bool = False
    location: Optional[str] = "Seoul"

@app.post("/api/analyze")
async def analyze_saju(data: SajuInput):
    try:
        # Format dates for SajuAnalyzer
        birth_date_str = f"{data.year:04d}{data.month:02d}{data.day:02d}"
        birth_time_str = f"{data.hour:02d}{data.minute:02d}"
        
        # Initialize Analyzer
        analyzer = SajuAnalyzer(
            birth_date_str=birth_date_str,
            birth_time_str=birth_time_str,
            gender=data.gender, # 'male' or 'female'
            name=data.name,
            calendar_type=data.calendarType, # 'solar' or 'lunar'
            is_leap_month=data.isLeapMonth
        )
        
        # Perform Calculation
        # The analyzer returns a rich dictionary
        result = analyzer.get_result_json()
        
        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
