import json
import logging
from dataclasses import dataclass
import time
from typing import Optional

import click
from geopy import distance

from audio import Audio
from mqtt import MQTT

log = logging.getLogger()


@dataclass(frozen=True)
class Context:
    debug: bool
    audio: Audio
    mqtt: MQTT


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.option("--mqtt-host", required=True)
@click.option("--mqtt-username", required=True)
@click.option("--mqtt-password", required=True)
@click.pass_context
def main(
    ctx: click.Context,
    debug: bool,
    mqtt_host: str,
    mqtt_username: str,
    mqtt_password: str,
):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(module)s:%(lineno)d %(message)s",
    )

    ctx.obj = Context(
        debug=debug,
        audio=Audio(),
        mqtt=MQTT(
            host=mqtt_host,
            username=mqtt_username,
            password=mqtt_password,
        ),
    )


@main.command()
@click.pass_obj
def list_audio_devices(ctx: Context):
    devices = ctx.audio.list_input_devices()
    for idx, name in devices.items():
        click.echo(f"{idx}: {name}")


@main.command()
@click.option("--device-index", type=int, required=False)
@click.pass_obj
def rms(ctx: Context, device_index: Optional[int] = None):
    ctx.mqtt.connect()

    for data, rms in ctx.audio.data_and_rms(input_device_index=device_index):
        ctx.mqtt.publish("rms", rms)
        ctx.mqtt.publish("audio", data)
        log.debug("rms: %s", rms)


@main.command()
@click.argument("aircraft_json")
@click.argument("our_lat", type=float)
@click.argument("our_lon", type=float)
@click.pass_obj
def aircraft(ctx: Context, aircraft_json: str, our_lat: float, our_lon: float):
    ctx.mqtt.connect()

    our_lat_lon = (our_lat, our_lon)
    last_now = 0
    last_messages = 0
    while True:
        time.sleep(1)

        with open(aircraft_json, mode="r") as f:
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
                f"{flight['hex']} ({flight.get('flight')}) distance: {dist.miles}"
            )

            ctx.mqtt.publish("flight", json.dumps(flight))


if __name__ == "__main__":
    try:
        main(auto_envvar_prefix="AIRNOISE")
    except KeyboardInterrupt:
        pass
