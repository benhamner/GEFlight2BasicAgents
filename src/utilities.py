import csv
from geopy.distance import distance
from math import atan2, cos, pi, sin
import os
import pandas as pd
from shapely.geometry import LineString, Polygon

def input_path():
    if "DataPath" in os.environ:
        return os.path.join(os.environ["DataPath"], "GEFlight2", "Release2", "TestData")
    return ""

def output_path():
    if "DataPath" in os.environ:
        return os.path.join(os.environ["DataPath"], "GEFlight2", "Release2", "Submissions")
    return ""

class Airport:
    def __init__(self, icao_code, latitude_degrees, longitude_degrees, altitude_feet):
        self.icao_code = icao_code
        self.latitude_degrees = latitude_degrees
        self.longitude_degrees = longitude_degrees
        self.altitude_feet = altitude_feet

def read_airports():
    airports_path = os.path.join(input_path(), "airports.csv")
    reader = csv.reader(open(airports_path))
    reader.next()
    airports = {}
    for row in reader:
        airports[row[0]]=Airport(row[0], float(row[1]), float(row[2]), float(row[3]))
    return airports

def read_no_fly_zones():
    no_fly_path = os.path.join(input_path(), "restrictedZones.csv")
    zones = pd.read_csv(no_fly_path)
    vertices = zones["LatLongVertices"]
    points = [[[float(x) for x in c.split(":")] for c in l.split(" ")] for l in vertices]
    polygons = [Polygon(x) for x in points]
    return polygons

def read_flights_df():
    test_flights_path = os.path.join(input_path(), "TestFlights.csv")
    return pd.read_csv(test_flights_path)

def airport_waypoint(flight, airport, ordinal, speed):
    return [flight["FlightHistoryId"], ordinal, airport.latitude_degrees, airport.longitude_degrees, 17000, speed]
 
def direct_route_waypoints(flight, airport, cruise=38000, descend_distance=150, speed=500):
    flight_loc = (flight["CurrentLatitude"], flight["CurrentLongitude"])
    airport_loc = (airport.latitude_degrees, airport.longitude_degrees)
    remaining_distance = distance(flight_loc, airport_loc).miles
    if remaining_distance < descend_distance:
        return [airport_waypoint(flight, airport, 1, speed)]

    lat_diff = airport.latitude_degrees - flight["CurrentLatitude"]
    long_diff = airport.longitude_degrees - flight["CurrentLongitude"]
    proportion_to_descent = (remaining_distance-descend_distance) / remaining_distance
    waypoint_latitude = flight["CurrentLatitude"] + proportion_to_descent*lat_diff
    waypoint_longitude = flight["CurrentLongitude"] + proportion_to_descent*long_diff
    return [[flight["FlightHistoryId"], 1, waypoint_latitude, waypoint_longitude, cruise, speed],
            airport_waypoint(flight, airport, 2, speed)]

def move_point(no_fly_zone, flight_loc, first_waypoint_loc, zone_loc, delta_x, delta_y, direction):
    i = 0
    while i<100 and (LineString([flight_loc, zone_loc]).intersects(no_fly_zone) or LineString([first_waypoint_loc, zone_loc]).intersects(no_fly_zone)):
        zone_loc = (zone_loc[0]+direction*delta_x, zone_loc[1]+direction*delta_y)
        i += 1

    return i, zone_loc

def avoid_no_fly_zone(no_fly_zone, waypoints, flight_loc, first_waypoint_loc, path):
    zone_loc = no_fly_zone.intersection(path).centroid.coords[0]
    theta = atan2(first_waypoint_loc[1]-flight_loc[1], first_waypoint_loc[0]-flight_loc[0]) + pi/2

    delta_x = 0.1*cos(theta)
    delta_y = 0.1*sin(theta)

    i1, zone_loc_1 = move_point(no_fly_zone, flight_loc, first_waypoint_loc, zone_loc, delta_x, delta_y, 1.0)
    i2, zone_loc_2 = move_point(no_fly_zone, flight_loc, first_waypoint_loc, zone_loc, delta_x, delta_y, -1.0)

    print(min(i1, i2))

    if i1 < i2:
        waypoints.insert(0, [waypoints[0][0], 0, zone_loc_1[0], zone_loc_1[1], waypoints[0][4], waypoints[0][5]])
    else: 
        waypoints.insert(0, [waypoints[0][0], 0, zone_loc_2[0], zone_loc_2[1], waypoints[0][4], waypoints[0][5]])
    return waypoints

def no_fly_avoidance_waypoints(no_fly_zones, flight, airport, cruise=38000, descend_distance=150, speed=500):
    waypoints = direct_route_waypoints(flight, airport, cruise, descend_distance, speed)
    flight_loc = (flight["CurrentLatitude"], flight["CurrentLongitude"])
    first_waypoint_loc = (waypoints[0][2], waypoints[0][3])
    path = LineString([flight_loc, first_waypoint_loc])

    for no_fly_zone in no_fly_zones:
        if path.intersects(no_fly_zone):
            waypoints = avoid_no_fly_zone(no_fly_zone, waypoints, flight_loc, first_waypoint_loc, path)
            break
    return waypoints

def save_waypoints(file_name, waypoints):
    waypoints_header = ["FlightId", "Ordinal", "LatitudeDegrees", "LongitudeDegrees", "AltitudeFeet", "AirspeedKnots"]
    waypoints.insert(0, waypoints_header)
    writer = csv.writer(open(os.path.join(output_path(), file_name), "w"), lineterminator="\n")
    writer.writerows([[str(x) for x in waypoint] for waypoint in waypoints])

if __name__=="__main__":
    for p in read_no_fly_zones():
        print(p.centroid.coords[0][0])