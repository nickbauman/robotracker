from restler.serializers import ModelStrategy

from models import Event

EVENT_FIELDS = ['created', 'location', 'readings', 'nature']
EVENT_STRATEGY = ModelStrategy(Event) + EVENT_FIELDS