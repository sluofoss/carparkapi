import os
import requests
from cachetools import cached, TTLCache
from app.models.nsw_schema import NSWCarparkParam

NSW_API_URL = "https://api.transport.nsw.gov.au/v1/carpark"
HEADERS = {"Authorization": f"apikey {os.getenv('NSW_API_KEY')}"}

_cache = TTLCache(maxsize=100, ttl=int(os.getenv("CACHE_TTL", 300)))
def get_cache() -> TTLCache:
    """Get the cache instance for testing access"""
    return _cache
@cached(cache=_cache)
def get_carparks(params:NSWCarparkParam|None=None):
    """
        returns full list of carpark without parameter
        returns single carpark details with facility_id
    """
    response = requests.get(NSW_API_URL, headers=HEADERS, params = params)
    response.raise_for_status()
    return response.json()
