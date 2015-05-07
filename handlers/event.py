import json, logging
from webapp2 import RequestHandler

from google.appengine.ext import ndb

from json_serialization import EVENT_STRATEGY
from restler.serializers import json_response

from models import Robot, Event

from django.template import add_to_builtins
add_to_builtins('agar.django.templatetags')


class EventHandler(RequestHandler):
    def get(self, robot_id):
        robot = Robot.query(Robot.robot_id == robot_id).get()
        if None is robot:
            self.response.set_status(404, "robot not found")
            return
        events = Event.query(Event.robot_id == robot.robot_id).order(-Event.created).fetch(200)
        logging.info("found {} events for {}".format(len(events), robot_id))
        json_response(self.response, events, strategy=EVENT_STRATEGY)

    def post(self):
        body = json.loads(self.request.body)
        robot_id = body.get('robot_id')
        if not robot_id:
            self.response.set_status(400, "Bad Request. missing robot_id value")
            return
        robot = Robot.query(Robot.robot_id == str(robot_id)).get()
        if None is robot:
            # be nice and make a robot
            robot = Robot(robot_id=str(robot_id))
            robot.put()
        coords = body.get('loc')
        location = None
        if coords and len(coords) == 2 and type(coords[0]) == float and type(coords[1] == float):
            location = ndb.GeoPt(coords[0], coords[1])
        luxes = body.get('luxes')
        saved_events = []
        if None is not luxes and len(luxes) > 0:
            event = Event(robot_id=robot.robot_id, location=location, nature='lux', readings=luxes)
            event.put()
            saved_events.append(event)
        temps = body.get('temps')
        if None is not temps and len(temps) > 0:
            event = Event(robot_id=robot.robot_id, location=location, nature='tmp', readings=temps)
            event.put()
            saved_events.append(event)
            json_response(self.response, saved_events, EVENT_STRATEGY)
