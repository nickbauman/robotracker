import env_setup; env_setup.setup()

from webapp2 import RequestHandler
from google.appengine.ext import ndb

from django.template import add_to_builtins
add_to_builtins('agar.django.templatetags')

from agar.django.templates import render_template
from models import Robot


class MainHandler(RequestHandler):
    def get(self):
        # CALLING ALL ROBOTS!
        all_robot_keys = Robot.query().order(Robot.created).fetch(keys_only=True)
        all_robots = ndb.get_multi(all_robot_keys) # all gets seed memcache
        render_template(self.response, 'index.html', {"robots": all_robots})

