import logging
from dataclasses import dataclass

import click

from audio import Audio

log = logging.getLogger()


@dataclass(frozen=True)
class Context:
    debug: bool
    audio: Audio


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def main(ctx: click.Context, debug: bool):
    ctx.obj = Context(
        debug=debug,
        audio=Audio(),
    )

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)


@main.command()
@click.pass_context
def list_audio_devices(ctx: click.Context):
    devices = ctx.obj.audio.list_input_devices()
    for idx, name in devices.items():
        click.echo(f"{idx}: {name}")


if __name__ == "__main__":
    main()
