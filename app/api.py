from fastapi import FastAPI, Depends, HTTPException, Query, Request
from app.services import nsw_service, geo
from app.models.schema import CarparkRelative, CarparkDetail
from app.models.nsw_schema import NSWCarparkParam
from app.dependencies import api_key_auth

from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address


limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get('/')
@limiter.limit("5/minute")
async def root(request: Request):
    """
    presence of request param is due to implicit requirement of slowapi
    """
    return {'Hello':'World'}

@app.get("/carparks/nearby", response_model=list[CarparkRelative])
@limiter.limit("5/minute")
async def nearby_carparks(
    request: Request,
    lat: float = Query(..., gt=-90, lt=90),
    lng: float = Query(..., gt=-180, lt=180),
    radius_km: float = Query(5, gt=0),
    api_key: str = Depends(api_key_auth)
):
    """
    fastapi depends auto verifies the validity of api_key
    """
    carparks = []
    user_location = (lat, lng)
    for cp, name in nsw_service.get_carparks().items():
        if '(historical only)' in name.lower():
            continue
        #props = cp["properties"]
        props = nsw_service.get_carparks(NSWCarparkParam(facility=cp))
        location = (props["location"]["latitude"], 
                    props["location"]["longitude"])
        
        if geo.within_radius(user_location, location, radius_km):
            distance = geo.distance_km(user_location, location)
            carparks.append({
                "facility_id": props["facility_id"],
                "name": props["facility_name"],
                "distance_km": distance,
            })
    
    return sorted(carparks, key=lambda x: x["distance_km"])

@app.get("/carparks/{facility_id}", response_model=CarparkDetail)
@limiter.limit("5/minute")
async def carpark_detail(
    request: Request,
    facility_id: str,
    api_key: str = Depends(api_key_auth)
):
    try:
        props = nsw_service.get_carparks(NSWCarparkParam(facility=facility_id))

        total = int(props["spots"])
        occupied = int(props["occupancy"]['total'])
        available =  total - occupied


        status = "Full" if available == 0 else "Almost Full" if available <= total * 0.1 else "Available"
        
        return {
            "facility_id": props["facility_id"],
            "name": props["facility_name"],
            'total_spots': total,
            'available_spots': available,
            'status':status,
            'last_updated': props["MessageDate"]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Carpark not found")
