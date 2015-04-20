# to be run in a REPL
import requests, time, json, random, math
from collections import namedtuple

HOST = "test-app-id"

ROBO_EVENTS_POST_URL = "http://{}/robot-event".format(HOST)

GO_NE_SW = '/'
GO_NW_SE = '\\'
GO_LR = '_'
GO_UD = '|'
START = 'o'
END = 'x'

MAP = """
      __
     /  \
    /    \      /\__
    \     |____/    \
     \               \_
   ___\                |
  /                    x
 /
o
"""

print MAP

SPYHOUSE_COFFEE = [44.9914983, -93.2602495]

Point = namedtuple('Point', ['lat', 'lon'], verbose=True)
AsciiMapCoord = namedtuple('AsciiMapCoord', ['x', 'y'], verbose=True)


class Step(object):
    STEP_DISTANCE_M = 10.0
    VALID_TYPES = ['start', 'end', None]
    TEMP_RANGE_C = [float(s) for s in range(-40, 40)]
    LIGHT_RANGE_LUX = [float(s) for s in range(1, 100000, 500)]

    map_symbol = None
    ascii_coord = None
    source_point = None
    destination_point = None
    type = None
    next = None
    previous = None

    def __init__(self, map_symbol, ascii_map_coord, previous_step):
        if map_symbol == START:
            self.type = 'start'
        elif map_symbol == END:
            self.type = 'end'
        else:
            self.type = None
        self.ascii_coord = ascii_map_coord
        self.map_symbol = map_symbol
        self.source_point = previous_step.location()
        self.type = type

    def set_next(self, step):
        self.next = step

    def location(self):
        return self.destination_point if self.destination_point is not None else self.source_point

    def temperature(self):
        return random.choice(Step.TEMP_RANGE_C)

    def lux(self):
        return random.choice(Step.LIGHT_RANGE_LUX)

    def _get_angled_distance_coord_distance_change(self):
        """
        Returns the delta difference for lat an lon going at a 45 degree angle from the source point in any direction.

        Discussion:
        If your displacements aren't too great (less than a few kilometers) and you're not right at the poles, use the
        quick and dirty estimate that 111,111 meters (111.111 km) in the y direction is 1 degree (of latitude) and
        111,111 * cos(latitude) meters in the x direction is 1 degree (of longitude).

        :return: delta latitude float, delta longitude float
        """

        # Calculate pythagorean distance instead of great-circle calculation (we're only moving several meters after all)
        hypotenuse_squared = Step.STEP_DISTANCE_M * Step.STEP_DISTANCE_M
        legs_length = math.sqrt(hypotenuse_squared / 2.0) # legs are equidistant because 45 degree change

        lat_change = legs_length / 111111.0
        lon_change = legs_length / (111111.0 * math.cos(self.source_point.lon))
        return lat_change, lon_change

    def __call__(self, *args, **kwargs):
        slat = self.source_point.lat
        slon = self.source_point.lon
        if self.map_symbol == END or self.next is None:
            return False # do nothing, falsely; you've completed the journey.
        elif self.map_symbol == START:
            return True # do nothing, you're at the beginning of the map
        elif self.map_symbol == GO_NE_SW: # /
            lat_change, lon_change = self._get_angled_distance_coord_distance_change()
            # NE or SW?
            if self.previous.ascii_coord.y < self.ascii_coord.y:
                # we're above previous, we're going NE
                self.destination_point = Point(lat=slat + lat_change, lon=slon + lon_change)
            else:
                # we're below previous, we're going SW
                self.destination_point = Point(lat=slat - lat_change, lon=slon - lon_change)
        elif self.map_symbol == GO_NW_SE: # \
            lat_change, lon_change = self._get_angled_distance_coord_distance_change()
            # NW or SE?
            if self.previous.ascii_coord.y < self.ascii_coord.y:
                # we're above previous, we're going NW
                self.destination_point = Point(lat=slat + lat_change, lon=slon - lon_change)
            else:
                # we're below previous, we're going SE
                self.destination_point = Point(lat=slat - lat_change, lon=slon + lon_change)
        elif self.map_symbol == GO_LR:
            pass
        elif self.map_symbol == GO_UD:
            pass
        else:
            raise ValueError("don't know how to read symbol '{}'".format(self.map_symbol))


def gen_steps_from_map(starting_point, map):
    return []


def render_as_json(robot_id, location, temperature, brightness):
    return json.dumps({'robot_id': robot_id, 'loc': location, 'temp': temperature, 'lum': brightness})


def robo_walkabout(robot_id=1234, starting_point=SPYHOUSE_COFFEE, map=MAP, sample_rate_per_minute=20):
    my_robot_url = "{}/{}".format(ROBO_EVENTS_POST_URL, robot_id)
    last_location = starting_point
    pause_seconds = 60 / sample_rate_per_minute
    steps = gen_steps_from_map(starting_point, map)
    for destination in steps:
        last_location = destination.location()  # based on map
        temperature = destination.temperature()  # random
        brightness = destination.brightness()  # random
        message = render_as_json(robot_id, last_location, temperature, brightness)
        requests.post(my_robot_url, json=message)
        time.sleep(pause_seconds)
    return last_location


