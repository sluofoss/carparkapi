import pytest
from app.models.nsw_schema import NSWCarparkParam
from unittest.mock import patch, Mock
from test.fixtures import client, clear_cache, mock_services#, client_without_key
from fastapi import HTTPException
from app.dependencies import api_key_auth

def test_root_endpoint(client):
    # First 5 requests should succeed
    for _ in range(5):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}
    
    # Sixth request should be rate-limited
    response = client.get("/")
    assert response.status_code == 429

def test_unauthorized_blocking(client):
    client.app.dependency_overrides.pop(api_key_auth)
    response = client.get("/carparks/1")
    assert response.status_code == 401 #unauthorized

def test_nearby_carparks_success(client, mock_services):
    mock_nsw, mock_geo = mock_services
    
    # Configure detailed carpark response
    call_mock = {
        # First call: get all carparks (no parameters)
        None:{
            1: "Tallawong Station Car Park (historical only)",
            2: "Park&Ride - Gordon Henry St (north)",
            #7: "Park&Ride - Kiama"
        },
        # Second call: get details for facility "1" (with parameters)
        # This call should actually contribute to actual location because of how mock_geo is defined
        NSWCarparkParam(facility=2): {
            "facility_id": "2",
            "facility_name": "Carpark 2",
            #"total_spots":10,
            #"available_spots":10,
            #"status":"Available",
            'last_updated':'2025-01-01T12:00:00',
            "location": {"latitude": -33.756009, "longitude": 151.154528}
        },
        NSWCarparkParam(facility=1): {
            "facility_id": "1",
            "facility_name": "Carpark 1 (historical only)",
            #"total_spots":10,
            #"available_spots":10,
            #"status":"Available",
            'last_updated':'2025-01-01T12:00:00',
            "location": {"latitude": 0, "longitude": 0}
        }
    }
    def side_effect(x=None):
        return call_mock[x]
    mock_nsw.get_carparks.side_effect = side_effect

    response = client.get(
        "/carparks/nearby",
        params={"lat": 0.0, "lng": 0.0, "radius_km": 5}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["facility_id"] == "2"


def test_specific_carpark_exist(client, mock_services):
    mock_nsw, mock_geo = mock_services
    
    # Configure detailed carpark response
    call_mock = {
        NSWCarparkParam(facility=1): {
            "facility_id": "1",
            "facility_name": "Carpark 1",
            "spots":10,
            "occupancy":{
                'total':10
            },
            'MessageDate':'2025-01-01T12:00:00',
            "location": {"latitude": 0, "longitude": 0}
        }
    }
    def side_effect(x=None):
        return call_mock[x]
    mock_nsw.get_carparks.side_effect = side_effect

    response = client.get(
        "/carparks/1"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Full"
    assert data["available_spots"] == 0

def test_obsolete_carpark(client, mock_services):
    mock_nsw, mock_geo = mock_services
    
    # Configure detailed carpark response
    call_mock = {
        NSWCarparkParam(facility=2): None
    }
    def side_effect(x=None):
        return call_mock[x]
    mock_nsw.get_carparks.side_effect = side_effect

    response = client.get(
        "/carparks/2"
    )
    assert response.status_code == 404
    