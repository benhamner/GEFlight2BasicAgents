from __future__ import division
import csv
from itertools import chain
import pandas as pd
import utilities as u

def make_sample_submission():
    airports = u.read_airports()
    test_flights = u.read_flights_df()
    waypoints = []
    cruise = 38000
    descend_distance = 150
    speed = 450
    waypoints = list(chain.from_iterable(
        u.direct_route_waypoints(
            row,
            airports[row["ArrivalAirport"]],
            cruise=cruise,
            descend_distance=descend_distance,
            speed=speed) for i, row in test_flights.iterrows()))
    # file_name = "%dk_cruise_%dmiles_descend_%dknots.csv" % (int(cruise/1000), descend_distance, speed)
    file_name = "sampleSubmission.csv"
    u.save_waypoints(file_name, waypoints)

if __name__=="__main__":
    make_sample_submission()