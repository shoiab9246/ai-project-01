#!/usr/local/bin/python3
# route.py : Find routes through maps
#
# Code by: Shoiab Mohammed , Vijay
#
# Based on skeleton code by V. Mathur and D. Crandall, January 2021


# !/usr/bin/env python3
import sys
import math
import re


class City:
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.cameFrom = None
        self.neighbors = []
        self.visited = 0
        self.gscore = math.inf
        self.fscore = math.inf


class Neighbor:
    def __init__(self, City, Highway, SpeedLimit, Distance):
        self.city = City
        self.highway = Highway
        self.distance = Distance
        self.speedlimit = SpeedLimit
        self.timetaken = (self.distance)/(self.speedlimit)
        self.accidents = 2 if "I-" in self.highway else 1


def GenerateCities():
    f = open("city-gps.txt")
    Cities = {}
    for i in f.readlines():
        if i.split()[0] not in Cities:
            Cities[i.split()[0]] = City(i.split()[0], i.split()[1], i.split()[2])
    f = open("road-segments.txt")
    for i in f.read().splitlines():
        city1 = i.split(' ')[0]
        city2 = i.split(' ')[1]
        if city1 not in Cities:
            Cities[city1] = City(city1, 0, 0)
        if city2 not in Cities:
            Cities[city2] = City(city2, 0, 0)
        Cities[city1].neighbors.append(Neighbor(Cities[city2], str(i.split(' ')[4]), int(i.split(' ')[3]), int(i.split(' ')[2])))
        Cities[city2].neighbors.append(Neighbor(Cities[city1], str(i.split(' ')[4]), int(i.split(' ')[3]), int(i.split(' ')[2])))
    return Cities


#https://stackoverflow.com/questions/28994289/calculate-euclidean-distance-with-google-maps-coordinates
#If the two points are near each other, for example in the same city, estimating the great circle with a straight line in the latitude-longitude space will produce minimal error, and be a lot faster to calculate. A minor complication is the fact that the length of a degree of longitude depends on the latitude: a degree of longitude spans 111km on the Equator, but half of that on 60° north. Adjusting for this is easy: multiply the longitude by the cosine of the latitude. Then you can just
# take the Euclidean distance between the two points, and multiply by the length of a degree:

def heuristic1(Cities,current_city,goal_city):
    if current_city.latitude == 0:
        return 0
    Lat1 = float(Cities[current_city.name].latitude)
    Lon1 = float(Cities[current_city.name].longitude)
    Lat2 = float(Cities[goal_city].latitude)
    Lon2 = float(Cities[goal_city].longitude)
    deglen = 110.25
    x = Lat1 - Lat2
    y = (Lon1-Lon2) * math.cos(Lat2)
    return deglen * math.sqrt(x * x + y * y)


def heuristic2(Cities, current_city, goal_city):
    if current_city.latitude == 0:
        return 0
    Lat1 = float(Cities[current_city.name].latitude)
    Lon1 = float(Cities[current_city.name].longitude)
    Lat2 = float(Cities[goal_city].latitude)
    Lon2 = float(Cities[goal_city].longitude)
    return getDistanceFromLatLonInKm(Lat1, Lon1, Lat2, Lon2)*0.621371   # conversion from km to miles


# https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
def getDistanceFromLatLonInKm(lat1,lon1,lat2,lon2):
      R = 6371; #Radius of the earth in km
      dLat = deg2rad(lat2-lat1)
      dLon = deg2rad(lon2-lon1)
      a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
      c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a));
      d = R * c;
      return d


def deg2rad(deg):
    return deg * (math.pi/180)

#https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
def heuristic3(Cities, current_city, goal_city):
    if current_city.latitude == 0:
        return 0
    lat1 = float(Cities[current_city.name].latitude)
    lon1 = float(Cities[current_city.name].longitude)
    lat2 = float(Cities[goal_city].latitude)
    lon2 = float(Cities[goal_city].longitude)
    p = math.pi / 180
    a = 0.5 - math.cos((lat2 - lat1) * p) / 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * (1 - math.cos((lon2 - lon1) * p)) / 2
    return 12742 * math.asin(math.sqrt(a))*0.621371 # conversion from km to miles


def reconstructPath(current, start):
    route = []
    distance : float = 0
    segments = 0
    time = 0
    accidents = 0
    while current.name != start:
        neighbor = [i for i in current.neighbors if current.cameFrom.name == i.city.name]
        route.append((current.name, "{0} for {1} miles".format(neighbor[0].highway, neighbor[0].distance)))
        distance += neighbor[0].distance
        segments += 1
        time += neighbor[0].timetaken
        accidents += neighbor[0].accidents
        current = current.cameFrom
    return {"total-segments": segments,
            "total-miles": float(distance),
            "total-hours": time,
            "total-expected-accidents": accidents/(10**6),
            "route-taken": route[::-1]}


def get_route(start, end, cost):

    """
    Find shortest driving route between start city and end city based on a cost function.

    1. Your function should return a dictionary having the following keys:
        -"route-taken" : a list of pairs of the form (next-stop, segment-info), where
           next-stop is a string giving the next stop in the route, and segment-info is a free-form
           string containing information about the segment that will be displayed to the user.
           (segment-info is not inspected by the automatic testing program).
        -"total-segments": an integer indicating number of segments in the route-taken
        -"total-miles": a float indicating total number of miles in the route-taken
        -"total-hours": a float indicating total amount of time in the route-taken
        -"total-expected-accidents": a float indicating the expected accident count on the route taken
    2. Do not add any extra parameters to the get_route() function, or it will break our grading and testing code.
    3. Please do not use any global variables, as it may cause the testing code to fail.
    4. You can assume that all test cases will be solvable.
    5. The current code just returns a dummy solution.
    """

    Cities = GenerateCities()
    if cost == "segments":
        return findsmallestpath(Cities, start, end, "segments")
    elif cost == "distance":
        return findsmallestpath(Cities, start, end, "distance")
    elif cost == "time":
        return findsmallestpath(Cities, start, end, "time")
    else:
        return findsmallestpath(Cities, start, end, "safe")


def findsmallestpath(Cities, start, end, cost_function):
    fringe = [Cities[start]]
    Cities[start].gscore = 0

    hscore = 0
    while fringe:
        current = fringe.pop(fringe.index(min(fringe, key=lambda t: t.fscore)))
        current.visited = 1
        if current.name == end:
            return reconstructPath(current, start)
        for neighbor in current.neighbors:
            if cost_function == "segments":
                cost = 1
                hscore = 0
            elif cost_function =="distance":
                cost = neighbor.distance
                hscore = heuristic3(Cities, neighbor.city, end)
            elif cost_function == "time":
                cost = neighbor.timetaken
                hscore = heuristic3(Cities, neighbor.city, end)/ neighbor.speedlimit # dividing distance by the speed limit
            else:
                cost = neighbor.accidents
                hscore = 0
            if neighbor.city not in fringe:
                if neighbor.city.visited == 1:
                    if neighbor.city.gscore > current.gscore + cost:
                        neighbor.city.cameFrom = current
                        neighbor.city.gscore = current.gscore + cost
                        neighbor.city.fscore = current.gscore + hscore
                else:
                    neighbor.city.cameFrom = current
                    neighbor.city.gscore = current.gscore + cost
                    neighbor.city.fscore = current.gscore + hscore
                    fringe.append(neighbor.city)
            else:
                if neighbor.city.gscore > current.gscore + cost:
                    neighbor.city.cameFrom = current
                    neighbor.city.gscore = current.gscore + cost
                    neighbor.city.fscore = current.gscore + hscore
    return ""



    #    route_taken = [("Martinsville,_Indiana","IN_37 for 19 miles"),
    #                   ("Jct_I-465_&_IN_37_S,_Indiana","IN_37 for 25 miles"),
    #                   ("Indianapolis,_Indiana","IN_37 for 7 miles")]

    #    return {"total-segments" : len(route_taken),
    #            "total-miles" : 51,
    #            "total-hours" : 1.07949,
    #            "total-expected-accidents" : 0.000051,
    #            "route-taken" : route_taken}


# Please don't modify anything below this line
if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise(Exception("Error: expected 3 arguments"))

    (_, start_city, end_city, cost_function) = sys.argv
    if cost_function not in ("segments", "distance", "time", "safe"):
        raise(Exception("Error: invalid cost function"))

    result = get_route(start_city, end_city, cost_function)

    # Pretty print the route
    print("Start in %s" % start_city)
    for step in result["route-taken"]:
        print("  Then go to %s via %s" % step)

    print("\n Total segments: %6d" % result["total-segments"])
    print("    Total miles: %10.3f" % result["total-miles"])
    print("    Total hours: %10.3f" % result["total-hours"])
    print("Total accidents: %15.8f" % result["total-expected-accidents"])


