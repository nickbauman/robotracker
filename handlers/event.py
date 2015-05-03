from webapp2 import RequestHandler
from agar.django.templates import render_template
from models import Robot, Event


class EventHandler(RequestHandler):
    def get(self, robot_id):
        robot = Robot.query(robot_id == robot_id).get()
        if None is robot:
            self.response.set_status(404, "robot not found")
            return
        events = Event.query(Event.robot_id == robot.robot_id).order(-Event.created).fetch(200)
        t = 'main.html'
        context = {"robot": robot, "events": events}
        render_template(self.response, t, context)

    def post(self):
        robot_id = self.request.params.get('robot_id')
        robot = Robot.query(robot_id == robot_id).get()
        if None is robot:
            self.response.set_status(404, "robot not found")
            return
        location = self.request.params.getall('loc')
        luxes = self.request.params.getall('luxes')
        if None is not luxes and len(luxes) > 0:
            event = Event(robot_id=robot.robot_id, location=location, nature='lux', readings=luxes)
            event.put()
        temps = self.request.params.getall('temps')
        if None is not temps and len(temps) > 0:
            event = Event(robot_id=robot.robot_id, location=location, nature='tmp', readings=temps)
            event.put()
        self.response.headers['content-type'] = 'text/json'
        self.response.write('{"luxes": {}, "temps": {}}'.format(len(luxes), len(temps)))
        