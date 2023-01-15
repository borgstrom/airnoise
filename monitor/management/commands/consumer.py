import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict

import schedule
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.utils import timezone

from monitor.influx import Influx
from monitor.models import AudioBuffer, Flight, Location
from monitor.mqtt import MQTT, MQTTMessage

log = logging.getLogger(__name__)

FLIGHT_INACTIVITY = timedelta(minutes=30)


class Command(BaseCommand):
    help = "Consume MQTT events and update data sources"

    influx: Influx

    _locations: Dict[str, Location]

    _lock = threading.Lock()
    last_rms = 0

    def handle(self, *args, **options) -> None:
        self._locations = {}
        self.influx = Influx()

        self.last_rms = 0

        mqtt = MQTT()
        mqtt.connect()
        mqtt.subscribe("+/rms", self.on_rms)
        mqtt.subscribe("+/flight", self.on_flight)
        mqtt.subscribe("+/audio", self.on_audio)

        schedule.every().hour.do(self.trim_audiobuffer)
        schedule.every().minute.do(self.finalize_flights)

        while True:
            schedule.run_pending()
            time.sleep(1.0)

    def inactive_flight_datetime(self) -> datetime:
        return timezone.now() - FLIGHT_INACTIVITY

    def trim_audiobuffer(self) -> None:
        one_hour_ago = timezone.now() - timedelta(hours=1)
        AudioBuffer.objects.filter(added__lt=one_hour_ago).delete()

    def finalize_flights(self) -> None:
        pass

    def get_location(self, msg: MQTTMessage) -> Location:
        with self._lock:
            name = msg.topic.split("/")[0]
            try:
                return self._locations[name]
            except KeyError:
                pass

            location, _ = Location.objects.get_or_create(name=name)
            self._locations[name] = location
            return self._locations[name]

    def on_rms(self, msg: MQTTMessage):
        location = self.get_location(msg)

        payload = int(msg.payload.decode())
        point = (
            self.influx.point("audio")
            .tag("location", location.name)
            .field("rms", payload)
        )
        self.influx.write(point)

        with self._lock:
            self.last_rms = payload

    def on_flight(self, msg: MQTTMessage):
        location = self.get_location(msg)

        payload = json.loads(msg.payload.decode())

        flight_id = payload.get("flight", "").strip()
        if not flight_id:
            return

        dist = float(payload["distance"])

        point = (
            self.influx.point("flight")
            .tag("location", location.name)
            .tag("flight", flight_id)
            .field("distance", dist)
            .field("altitude", payload["altitude"])
        )
        self.influx.write(point)

        try:
            flight = Flight.objects.get(
                location=location,
                icao_24bit_hex=payload["hex"],
                flight_name=flight_id,
                last_seen__gt=self.inactive_flight_datetime(),
            )
        except Flight.DoesNotExist:
            flight = Flight.objects.create(
                location=location,
                icao_24bit_hex=payload["hex"],
                flight_name=flight_id,
            )

        with self._lock:
            rms = self.last_rms

        altitude = int(payload.get("altitude", 0))

        flight.data.create(  # type: ignore -- why can't pylance resolve the data related_name?
            squawk_code=payload.get("squawk", ""),
            rms=rms,
            altitude=altitude if altitude > 0 else 0,
            point=Point(payload["lon"], payload["lat"]),
        )

    def on_audio(self, msg: MQTTMessage):
        location = self.get_location(msg)

        AudioBuffer.objects.create(
            location=location,
            data=msg.payload,
        )
