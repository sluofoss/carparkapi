from pydantic import BaseModel
from datetime import datetime

class CarparkRelative(BaseModel):
    facility_id: str
    name: str
    distance_km: float

class CarparkDetail(BaseModel):
    facility_id: str
    name: str
    total_spots: int
    available_spots: int  
    status: str # Available/Almost Full/Full
    last_updated: datetime