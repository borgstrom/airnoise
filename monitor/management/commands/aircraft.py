import logging

from django.core.management.base import BaseCommand
from monitor.dump1090 import get_close_aircraft
from monitor.mqtt import MQTT

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Read dump1090 aircraft.json and send data"

    def handle(self, *args, **options) -> None:
        mqtt = MQTT()
        mqtt.connect()
        for flight in get_close_aircraft():
            mqtt.publish("flight", flight)
