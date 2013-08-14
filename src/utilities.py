import csv
from geopy.distance import distance
import os
import pandas as pd

def input_path():
    if "DataPath" in os.environ:
        return os.path.join(os.environ["DataPath"], "GEFlight2", "Release1", "TestData")
    return ""

def output_path():
    if "DataPath" in os.environ:
        return os.path.join(os.environ["DataPath"], "GEFlight2", "Release1", "Submissions")
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

def read_flights_df():
    test_flights_path = os.path.join(input_path(), "testFlights.csv")
    return pd.read_csv(test_flights_path)

def airport_waypoint(flight, airport, ordinal, speed):
    return [flight["FlightHistoryId"], ordinal, airport.latitude_degrees, airport.longitude_degrees, 18000, speed]
 
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

def save_waypoints(file_name, waypoints):
    waypoints_header = ["FlightId", "Ordinal", "LatitudeDegrees", "LongitudeDegrees", "AltitudeFeet", "AirspeedKnots"]
    waypoints.insert(0, waypoints_header)
    writer = csv.writer(open(os.path.join(output_path(), file_name), "w"), lineterminator="\n")
    writer.writerows([[str(x) for x in waypoint] for waypoint in waypoints])