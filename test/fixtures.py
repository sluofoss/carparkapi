import pytest
from fastapi.testclient import TestClient
from app.api import app
from app.services.nsw_service import get_cache
from app.dependencies import api_key_auth
from unittest.mock import MagicMock, patch
from slowapi.errors import RateLimitExceeded
from app.models.schema import CarparkRelative, CarparkDetail
import datetime

# Fixture to override auth dependency and reset rate limiter
@pytest.fixture
def client(mocker):
    # Override auth dependency
    def mock_api_key_auth():
        return "valid_api_key"
    app.dependency_overrides[api_key_auth] = mock_api_key_auth
    
    # Reset limiter storage before each test
    app.state.limiter._storage.storage.clear()
    
    #with TestClient(app) as test_client:
    #    yield test_client
    return TestClient(app)

    # Cleanup
    app.dependency_overrides = {}

#@pytest.fixture
#def client_without_key(mocker):    
#    # Reset limiter storage before each test
#    app.state.limiter._storage.storage.clear()
#
#    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test"""
    cache = get_cache()
    cache.clear()

@pytest.fixture
def mock_services(mocker):
    # 1. Service Mocking
    mock_nsw = mocker.patch("app.api.nsw_service")
    mock_geo = mocker.patch("app.api.geo")
    
    # 2. Default Behavior Setup
    mock_nsw.get_carparks.return_value = {
        1: "Tallawong Station Car Park (Historical Only)",
        6: "Park&Ride - Gordon Henry St (north)",
        7: "Park&Ride - Kiama"
    }
    def mocking_within_radius(loc1, loc2, rad):
        return loc2 == (-33.756009, 151.154528)
    mock_geo.within_radius.side_effect = mocking_within_radius#lambda loc1, loc2, rad: loc2 == (-33.756009, 151.154528)
    mock_geo.distance_km.return_value = 1.5
    
    return mock_nsw, mock_geo