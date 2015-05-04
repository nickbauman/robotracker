from google.appengine.ext import ndb
from restler.decorators import ae_ndb_serializer


class Robot(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    robot_id = ndb.StringProperty(required=True)


NATURES = ['tmp', 'lux']


@ae_ndb_serializer
class Event(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    robot_id = ndb.StringProperty(required=True)
    location = ndb.GeoPtProperty(indexed=False)
    readings = ndb.FloatProperty(indexed=False, repeated=True)
    nature = ndb.StringProperty(choices=NATURES, required=True)
