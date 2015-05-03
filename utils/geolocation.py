from math import radians, cos, sin, asin, sqrt


def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance (in meters) between two points on the earth specified in decimal degrees,
    (lon1, lat1) and (lon2, lat2).

    :param lon1: The first longitude value, in decimal degrees.
    :param lat1: the first latitude value, in decimal degrees.
    :param lon2: The second longitude value, in decimal degrees.
    :param lat2: The second latitude value, in decimal degrees.
    :return: The distance between (lon1, lat1) and (lon2, lat2) in feet.
    """
    lon1 = radians(lon1)
    lat1 = radians(lat1)
    lon2 = radians(lon2)
    lat2 = radians(lat2)

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371.0 # 6371 km is the radius of the Earth
    return (c * r) * 1000 # meters