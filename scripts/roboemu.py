# to be run in a REPL
import requests, time, json, random, math
from collections import namedtuple, OrderedDict
from utils import web

HOST = "localhost"
PORT = "8080"
DEBUG = True

ROBO_EVENTS_POST_URL = "http://{}:{}{}".format(HOST, PORT, web.build_uri('robot-event-post'))

GO_NE_SW = '/'
GO_NW_SE = '\\'
GO_LR = '-'
GO_UD = '|'
START = 'o'
END = 'x'

MOVES = [GO_NE_SW, GO_NW_SE, GO_LR, GO_UD]

SEARCH_DIRECTIONS = OrderedDict(n=(0, 1), e=(1, 0), s=(0, -1), w=(-1, 0), nw=(-1, 1), ne=(1, 1), se=(1, -1),
    sw=(-1, -1))

MAP = [
    '     --                  ',
    '    /  \    ---          ',
    '   /    \  /   \         ',
    '   \     --     ----     ',
    '    \               |    ',
    '  ---                --x ',
    ' /                       ',
    'o                        ',
]

SPYHOUSE_COFFEE = [44.9983059, -93.2467148]

Point = namedtuple('Point', ['lat', 'lon'], verbose=False)
AsciiMapCoord = namedtuple('AsciiMapCoord', ['x', 'y', 'symbol'], verbose=False)


class Step(object):
    STEP_DISTANCE_M = 100.0
    VALID_TYPES = ['start', 'end', None]
    TEMP_RANGE_C = [float(s) for s in range(-40, 40)]
    LIGHT_RANGE_LUX = [float(s) for s in range(1, 100000, 500)]

    ascii_coord = None
    source_point = None
    destination_point = None
    type = None
    next = None
    previous = None

    def __init__(self, ascii_map_coord, previous_step=None, source_point=None):
        if ascii_map_coord.symbol == START:
            self.type = 'start'
        elif ascii_map_coord.symbol == END:
            self.type = 'end'
        else:
            self.type = None
        self.ascii_coord = ascii_map_coord
        if None is source_point:
            self.source_point = previous_step.location()
            self.previous = previous_step
        elif None is previous_step:
            self.source_point = source_point
        else:
            raise ValueError("must supply either a 'source_point' or a 'previous_step'")
        self.type = type

    def set_next(self, step):
        self.next = step

    def location(self):
        return self.destination_point

    def temperature(self):
        return random.choice(Step.TEMP_RANGE_C)

    def lux(self):
        return random.choice(Step.LIGHT_RANGE_LUX)

    def determine_destination_point(self):
        """
        Returns the delta difference for lat an lon going at a 45 degree angle from the source point in any direction.

        Discussion:
        If your displacements aren't too great (less than a few kilometers) and you're not right at the poles, use the
        quick and dirty estimate that 111,111 meters (111.111 km) in the y direction is 1 degree (of latitude) and
        111,111 * cos(latitude) meters in the x direction is 1 degree (of longitude).

        :return: delta latitude float, delta longitude float
        """
        slat = self.source_point[0]
        slon = self.source_point[1]
        lat_neg = -1 if slat < 0 else 1
        lon_neg = -1 if slon < 0 else 1
        if self.ascii_coord.symbol == GO_NE_SW or self.ascii_coord.symbol == GO_NW_SE:
            # Calculate pythagorean distance instead of great-circle calculation (we're only moving several meters)
            hypotenuse_squared = Step.STEP_DISTANCE_M * Step.STEP_DISTANCE_M
            legs_length = math.sqrt(hypotenuse_squared / 2.0)  # legs are equidistant because 45 degree change
            lat_change = legs_length / 111111.0
            lon_change = legs_length / (111111.0 * math.cos(self.source_point.lon))
            if self.ascii_coord.symbol == GO_NE_SW:  # forward slash /
                if self.previous.ascii_coord.y > self.ascii_coord.y:
                    p("we're going SW")
                    lat_change *= (-1 * lat_neg)
                    lon_change *= (-1 * lon_neg)
                else:
                    p("we're going NE")
            else:  # back slash \
                if self.previous.ascii_coord.y > self.ascii_coord.y:
                    p("we're going SE")
                    lat_change *= (-1 * lat_neg)
                else:
                    p("we're going NW")
                    lon_change *= (-1 * lon_neg)
        elif self.ascii_coord.symbol == GO_UD:
            lat_change = Step.STEP_DISTANCE_M / 111111.0
            lon_change = 0.0
            if self.previous.ascii_coord.y > self.ascii_coord.y:
                p("we're going S")
                lat_change *= (-1 * lat_neg)
            else:
                p("we're going N")
        elif self.ascii_coord.symbol == GO_LR:
            lat_change = 0.0
            lon_change = Step.STEP_DISTANCE_M / (111111.0 * math.cos(self.source_point.lon))
            if self.previous.ascii_coord.x < self.ascii_coord.x:
                p("we're going E")
                lon_change *= (-1 * lon_neg)
            else:
                p("we're going W")
        else:
            raise ValueError("cannot understand direction symbol '{}'".format(self.ascii_coord.symbol))
        return Point(lat=slat + lat_change, lon=slon + lon_change)

    def __call__(self, *args, **kwargs):
        if self.ascii_coord.symbol == END:
            p("END")
            return False  # do nothing, falsely; you've completed the journey.
        elif self.ascii_coord.symbol == START:
            p("START")
            self.destination_point = Point(self.source_point[0], self.source_point[1])
            return True  # truly do nothing, you're at the beginning of the map
        elif self.ascii_coord.symbol in MOVES:  # /
            p('MOVE {}'.format(self.ascii_coord))
            self.destination_point = self.determine_destination_point()
            return True
        else:
            raise ValueError("don't know how to read symbol '{}'".format(self.ascii_coord.symbol))


def p(message):
    if DEBUG:
        print(message)


def look(x, y, direction, move_lut):
    offsets = SEARCH_DIRECTIONS.get(direction)
    new_x = x + offsets[0]
    new_y = y + offsets[1]
    banner = "========================="
    travesal = "was {}".format(move_lut['traversed'][-1] if len(move_lut['traversed']) > 0 else "")
    next = "at {},{} looking {} at {},{}".format(x, y, direction, new_x, new_y)
    move_sym = move_lut.get((new_x, new_y), False)
    if move_sym and move_sym in MOVES:
        p(banner)
        p(travesal)
        p(next)
        result = move_lut.pop((new_x, new_y))
        move_lut['traversed'].append((result, (new_x, new_y)))
        new_move = AsciiMapCoord(x=new_x, y=new_y, symbol=move_sym)
        return new_move
    return False


def _gen_next_ascii_coord(last_step, move_lut):
    last_coord = last_step.ascii_coord
    x = last_coord.x
    y = last_coord.y
    for d in SEARCH_DIRECTIONS.keys():
        asci_coord = look(x, y, d, move_lut)
        if asci_coord:
            return asci_coord
    raise LookupError("map ends")


def gen_steps_from_map(starting_point, map_structure):
    if DEBUG:
        for i, row in enumerate(map_structure):
            p("{}: {}".format(i, row))
        p("   {}".format("".join([str(n) for n in (list(range(10)) * 3)])))

    steps = []

    # find the starting point and create a LUT for all other moves
    start_xy = None
    move_lut = {"traversed": []}
    y_mantissa = range(len(map_structure))
    y_mantissa.reverse()
    for y, row in zip(y_mantissa, map_structure):
        for x, column in enumerate(row):
            if column:
                xy_coord = AsciiMapCoord(x=x, y=y, symbol=column)
                if column in MOVES:
                    move_lut[(x, y)] = column
                if None is start_xy and column == START:
                    start_xy = xy_coord
    # gen steps
    if None is not start_xy:
        p("START {}".format(start_xy))
        step = Step(ascii_map_coord=start_xy, source_point=starting_point)
        steps.append(step)
        did = step()  # move

        try:
            while did:
                p("NEXT")
                step = Step(ascii_map_coord=_gen_next_ascii_coord(steps[-1], move_lut), previous_step=step)
                steps.append(step)
                did = step()  # keep moving
        except LookupError:
            print("generated {} maps steps".format(len(steps)))
    else:
        raise ValueError("map has no start step!")

    return steps


def render_as_json(robot_id, location, temperature, brightness):
    return {'robot_id': robot_id, 'loc': location, 'temps': temperature, 'luxes': brightness}


def robo_walkabout(robot_id=1234, endpoint=ROBO_EVENTS_POST_URL, starting_point=SPYHOUSE_COFFEE, map=MAP,
        sample_rate_per_minute=20):
    last_location = starting_point
    pause_seconds = 60 / sample_rate_per_minute
    steps = gen_steps_from_map(starting_point, map)
    for destination in steps:
        last_location = destination.location()  # based on map
        temperature = destination.temperature()  # random
        brightness = destination.lux()  # random
        message = {'robot_id': robot_id, 'loc': last_location, 'temps': [temperature], 'luxes': [brightness]}
        response = requests.post(endpoint, json=message)
        assert 200 == response.status_code, "expected 200 but received {}".format(response.status_code)
        time.sleep(pause_seconds)
    return last_location
