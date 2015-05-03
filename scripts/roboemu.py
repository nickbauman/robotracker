# to be run in a REPL
import requests, time, json, random, math
from collections import namedtuple, OrderedDict

HOST = "test-app-id"
DEBUG = False

ROBO_EVENTS_POST_URL = "http://{}/robot-event".format(HOST)

GO_NE_SW = '/'
GO_NW_SE = '\\'
GO_LR = '-'
GO_UD = '|'
START = 'o'
END = 'x'

MOVES = [GO_NE_SW, GO_NW_SE, GO_LR, GO_UD]

SEARCH_DIRECTIONS = OrderedDict(n=(0, 1), e=(1, 0), s=(0, -1), w=(-1, 0), nw=(-1, 1), ne=(1, 1), se=(1, -1), sw=(-1, -1))

MAP = [
    '     --                  ',
    '    /  \    ---          ',
    '   /    \  /   \         ',
    '   \     --     ----     ',
    '    \               |    ',
    '  ---                --  ',
    ' /                     \ ',
    'o                       x',
]

SPYHOUSE_COFFEE = [44.9914983, -93.2602495]

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
        return self.destination_point if self.destination_point is not None else self.source_point

    def temperature(self):
        return random.choice(Step.TEMP_RANGE_C)

    def lux(self):
        return random.choice(Step.LIGHT_RANGE_LUX)

    def _get_distance_coord_distance_change(self):
        """
        Returns the delta difference for lat an lon going at a 45 degree angle from the source point in any direction.

        Discussion:
        If your displacements aren't too great (less than a few kilometers) and you're not right at the poles, use the
        quick and dirty estimate that 111,111 meters (111.111 km) in the y direction is 1 degree (of latitude) and
        111,111 * cos(latitude) meters in the x direction is 1 degree (of longitude).

        :return: delta latitude float, delta longitude float
        """

        if self.ascii_coord.symbol == GO_NE_SW or self.ascii_coord.symbol == GO_NW_SE:
            # Calculate pythagorean distance instead of great-circle calculation (we're only moving several meters after all)
            hypotenuse_squared = Step.STEP_DISTANCE_M * Step.STEP_DISTANCE_M
            legs_length = math.sqrt(hypotenuse_squared / 2.0)  # legs are equidistant because 45 degree change
            lat_change = legs_length / 111111.0
            lon_change = legs_length / (111111.0 * math.cos(self.source_point.lon))
        elif self.ascii_coord.symbol == GO_UD:
            lat_change = Step.STEP_DISTANCE_M / 111111.0
            lon_change = 0.0
            if self.previous.ascii_coord.y > self.ascii_coord.y:
                # Go down
                lat_change *= -1
        elif self.ascii_coord.symbol == GO_LR:
            lat_change = 0.0
            lon_change = Step.STEP_DISTANCE_M / (111111.0 * math.cos(self.source_point.lon)) - .002912
            if self.previous.ascii_coord.x > self.ascii_coord.x:
                # go right
                lon_change *= -1
        else:
            raise ValueError("cannot understand direction symbol '{}'".format(self.ascii_coord.symbol))
        return lat_change, lon_change

    def __call__(self, *args, **kwargs):
        slat = self.source_point[0]
        slon = self.source_point[1]
        p("{}, {}".format(slat, slon))
        if self.ascii_coord.symbol == END:
            p("END")
            return False  # do nothing, falsely; you've completed the journey.
        elif self.ascii_coord.symbol == START:
            p("START")
            self.destination_point = Point(slat, slon)
            return True  # do nothing, you're at the beginning of the map
        elif self.ascii_coord.symbol in MOVES:  # /
            p('MOVE {}'.format(self.ascii_coord))
            lat_change, lon_change = self._get_distance_coord_distance_change()
            self.destination_point = Point(lat=slat + lat_change, lon=slon + lon_change)
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
    steps = []

    lines = map_structure
    for i, row in enumerate(lines):
        p("{}: {}".format(i, row))
    p("  {}".format("".join([str(n) for n in (list(range(10)) * 3)])))

    # find the starting point while creating a LUT for all other moves
    start_xy = None
    move_lut = {"traversed": []}
    for x, row in enumerate(lines):
        for y, column in enumerate(row):
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
        steps.insert(0, step)
        did = step()  # move

        try:
            while did:
                p("NEXT")
                step = Step(ascii_map_coord=_gen_next_ascii_coord(steps[0], move_lut), previous_step=step)
                steps.insert(0, step)
                did = step()  # keep moving
        except LookupError:
            print("generated {} maps steps".format(len(steps)))
    else:
        raise ValueError("map has no start step!")

    return steps


def render_as_json(robot_id, location, temperature, brightness):
    return json.dumps({'robot_id': robot_id, 'loc': location, 'temps': temperature, 'luxes': brightness})


def robo_walkabout(robot_id=1234, starting_point=SPYHOUSE_COFFEE, map=MAP, sample_rate_per_minute=20):
    my_robot_url = ROBO_EVENTS_POST_URL
    last_location = starting_point
    pause_seconds = 60 / sample_rate_per_minute
    steps = gen_steps_from_map(starting_point, map)
    for destination in steps:
        last_location = destination.location()  # based on map
        temperature = destination.temperature()  # random
        brightness = destination.lux()  # random
        message = render_as_json(robot_id, last_location, temperature, brightness)
        requests.post(my_robot_url, json=message)
        time.sleep(pause_seconds)
    return last_location


