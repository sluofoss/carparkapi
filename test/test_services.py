#import pytest
from unittest.mock import patch, Mock
from app.services import nsw_service, geo
from app.services.nsw_service import get_cache
from test.fixtures import client, clear_cache, mock_services

# ---- NSW Service Tests ----
@patch("app.services.nsw_service.requests.get")
def test_get_carparks_success(mock_get):
    """Test successful API response parsing"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {1: "carpark"}
    
    result = nsw_service.get_carparks()
    assert len(result) == 1

def test_get_carparks_caching():
    """Test caching reduces API calls"""
    # Clear cache before test
    cache = get_cache()
    cache.clear()
    
    with patch("app.services.nsw_service.requests.get") as mock_get:
        # Setup mock response
        mock_response = {
            1:"Test Carpark"
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
        
        # First call - should make API request
        result1 = nsw_service.get_carparks()
        # Second call - should use cache
        result2 = nsw_service.get_carparks()
        
        # Verify only one API call was made
        assert mock_get.call_count == 1
        # Verify same result is returned both times
        assert result1 == result2 == mock_response

# ---- Geo Service Tests ----
def test_distance_calculation():
    """Test distance calculation accuracy"""
    # Sydney to Melbourne ~714km
    sydney = (-33.8688, 151.2093)
    melbourne = (-37.8136, 144.9631)
    distance = geo.distance_km(sydney, melbourne)
    assert 710 < distance < 720

def test_within_radius():
    """Test radius filtering logic"""
    point_a = (0, 0)
    point_b = (0.1, 0.1)
    assert geo.within_radius(point_a, point_b, 20) is True
    assert geo.within_radius(point_a, point_b, 10) is False