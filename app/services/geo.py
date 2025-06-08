from geopy.distance import geodesic

def within_radius(point_a, point_b, radius_km):
    return geodesic(point_a, point_b).km <= radius_km

def distance_km(point_a, point_b):
    return geodesic(point_a, point_b).km