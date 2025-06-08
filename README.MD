# Car Park Finder API

A REST API service that helps users find nearby parking availability in New South Wales by interacting with the NSW Government's Car Park API.

# Features

- Find nearby car parks by location
- View detailed availability information
- Real-time status (Available/Almost Full/Full)
- In memory caching for improved performance
- In memory rate limiting
- Geopy Geodesic distance calculation
- API key authentication
- test coverage report
- CI/CD
- Comprehensive API documentation

# Prerequisites

- Python 3.10+
- NSW API Key (free registration)
- pip (Python package manager)


# Local Deployment

1. Configuration

Create a `.env` file in the project root with your API keys:

```bash
NSW_API_KEY="your_nsw_api_key_here"
APP_API_KEY="your_custom_api_key_here"
CACHE_TTL=300  # 5 minutes cache
```
2. set the env variables in shell 
```bash
export $(grep -v '^#' .env | xargs)
```

3. Run the Application
```bash
uvicorn app.api:app --reload

The API will be available at: http://localhost:8000
```
# API Documentation

Access interactive documentation at: `http://localhost:8000/docs` 
Endpoints

Find Nearby Car Parks

```
GET /carparks/nearby?lat={latitude}&lng={longitude}&radius_km={radius}
```
Example: http://localhost:8000/carparks/nearby?lat=-33.8688&lng=151.2093&radius_km=5

Get Car Park Details
```
GET /carparks/{facility_id}
```
Example: http://localhost:8000/carparks/37


## Authentication

All endpoints require an API key in the request header:
```
GET /carparks/nearby?lat=-33.8688&lng=151.2093
X-API-Key: your_application_api_key_here
```

A copy of the openapi.json file is also obtained and stored in the repo.
```
curl -O localhost:8000/openapi.json
```

# Testing

Run tests with coverage report:
```bash
pytest -s --cov=app --cov-report=html
```

View coverage report: open htmlcov/index.html

A copy of coverage report is also included in the repo.

# Docker Deployment


1. Build the Docker image:
```bash
docker build -t carpark-finder .
```

Run the container:
```bash
docker run -d -p 8000:8000 --env-file .env --name carpark-api carpark-finder
```
Assumptions & Notes

1. Status Thresholds:
   - Available: >10% spots free
   - Almost Full: ≤10% spots free
   - Full: 0 spots available

2. Coordinates Format:
   - Latitude: -90 to 90
   - Longitude: -180 to 180
   - Caching:
     - Data from nsw carpark api cached for 5 minutes by default
     - Cache TTL configurable via CACHE_TTL environment variable

3. NSW API:
   - Coordinates returned as [longitude, latitude]
   - Facility IDs are treated as strings
   - "spots" = total capacity, "total" = current occupancy

4. Distance Calculation:
   - Uses geodesic distance (accurate for short-medium distances)
   - Distances in kilometers

# CI/CD Pipeline

The project includes a GitHub Actions workflow that:
- Runs tests on every push

# Current Issues:
- Deployment to AWS blocked.
- Rate limit and cache test not comprehensive.
- CI/CD test workflow api key test currently fails on github action, method to resolve pending.