import logging
from dataclasses import dataclass
from typing import Optional

import click

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
@click.pass_context
def list_audio_devices(ctx: click.Context):
    devices = ctx.obj.audio.list_input_devices()
    for idx, name in devices.items():
        click.echo(f"{idx}: {name}")


@main.command()
@click.option("--device-index", type=int, required=False)
@click.pass_context
def rms(ctx: click.Context, device_index: Optional[int] = None):
    ctx.obj.mqtt.connect()
    for val in ctx.obj.audio.rms(input_device_index=device_index):
        ctx.obj.mqtt.publish("rms", val)
        log.debug("rms: %s", val)


if __name__ == "__main__":
    main(auto_envvar_prefix="AIRNOISE")
