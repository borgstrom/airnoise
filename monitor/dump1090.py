import json
import logging
import time
from typing import Iterator

from geopy import distance

import settings

log = logging.getLogger(__name__)


def get_close_aircraft() -> Iterator[str]:
    our_lat_lon = (settings.LAT, settings.LON)
    last_now = 0
    last_messages = 0
    while True:
        time.sleep(1)

        with open(settings.DUMP1090_AIRCRAFT_JSON, mode="r") as f:
            aircraft = json.load(f)

        # Ensure both our messages and now have increased, otherwise we're just processing old data
        if aircraft["messages"] == last_messages:
            continue
        last_messages = aircraft["messages"]

        if aircraft["now"] == last_now:
            continue
        last_now = aircraft["now"]

        for flight in aircraft["aircraft"]:
            lat = flight.get("lat")
            lon = flight.get("lon")

            # We ignore any flights that are not reporting lat/lon
            if (not lat) or (not lon):
                continue

            flight_lat_lon = (lat, lon)

            dist = distance.distance(our_lat_lon, flight_lat_lon)

            # We only care about flights within 3 miles of our station
            if dist.miles > 3.0:
                continue

            log.debug(
                f"{flight['hex']} ({flight.get('flight')}) distance: {dist.miles} altitutde: {flight.get('altitude')}"
            )

            yield json.dumps(flight)
