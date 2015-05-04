from webapp2 import RequestHandler
from google.appengine.ext import ndb
from agar.django.templates import render_template

from models import Robot

from django.template import add_to_builtins
add_to_builtins('agar.django.templatetags')

class RobotHandler(RequestHandler):
    def get(self, robot_id):
        robot = Robot.query(Robot.robot_id == robot_id).get()
        if None is robot:
            self.response.set_status(404, "robot not found")
            return
        # CALLING ALL ROBOTS!
        all_robot_keys = Robot.query().order(Robot.created).fetch(keys_only=True)
        all_robots = ndb.get_multi(all_robot_keys) # all gets seed memcache
        context = {"tracked_robot": robot, "robots": all_robots}
        print context
        render_template(self.response, 'index.html', context)
