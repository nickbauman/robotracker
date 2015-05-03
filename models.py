from google.appengine.ext import ndb


class Robot(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    robot_id = ndb.StringProperty(required=True)


NATURES = ['tmp', 'lux']


class Event(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    robot_id = ndb.StringProperty(required=True)
    location = ndb.GeoPtProperty(indexed=False)
    readings = ndb.FloatProperty(required=True, indexed=False, repeated=True)
    nature = ndb.StringProperty(choices=NATURES, required=True)
