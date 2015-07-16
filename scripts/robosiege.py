import random
from threading import Thread

from roboemu import robo_walkabout, SPYHOUSE_COFFEE
from robomaps import MAP1, MAP2, MAP3, MAP4, MAP5, MAP6

EC2_CLOUD_HOST_EVENT_URL = "http://ec2-52-3-89-75.compute-1.amazonaws.com:8080/event/create"
MAPS = [MAP1, MAP2, MAP3, MAP4, MAP5, MAP6]

def siege():
    for robot_id in [random.randrange(10000,100000) for r in range(200)]:
        t = Thread(target=robo_walkabout, args=(robot_id, EC2_CLOUD_HOST_EVENT_URL, SPYHOUSE_COFFEE,
                                                random.choice(MAPS), 60))
        t.start()
        print "started new robot {}".format(robot_id)x