import logging
import time
from typing import Any, Optional

from django.core.management.base import BaseCommand, CommandParser
from monitor.influx import Influx

from monitor.mqtt import MQTT, Client, MQTTMessage

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Consume MQTT events and update data sources"

    influx: Influx

    def handle(self, *args, **options) -> None:
        self.influx = Influx()

        mqtt = MQTT()
        mqtt.connect()
        mqtt.subscribe("+/rms", self.on_rms)
        mqtt.client.loop_forever()

    def on_rms(self, client: Client, userdata: Optional[Any], msg: MQTTMessage):
        payload = msg.payload.decode()
        topic = msg.topic
        log.debug("Received %s from %s", payload, topic)

        location = topic.split("/")[0]

        point = self.influx.point("audio").tag("location", location).field("rms", int(payload))
        self.influx.write(point)
