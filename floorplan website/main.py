from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

app = FastAPI()

# Pydantic models
class Location(BaseModel):
    x: float
    y: float
    type: str  # e.g., 'restroom', 'water'

class FloorplanData(BaseModel):
    floorplan_name: str
    locations: List[Location]

# Endpoint to upload preprocessed floorplan data
@app.post("/upload_floorplan")
async def upload_floorplan(data: FloorplanData):
    for loc in data.locations:
        res = supabase.table("locations").insert({
            "floorplan_name": data.floorplan_name,
            "x": loc.x,
            "y": loc.y,
            "type": loc.type
        }).execute()
        if res.error:
            return {"status": "error", "details": res.error}
    return {"status": "success", "floorplan": data.floorplan_name}