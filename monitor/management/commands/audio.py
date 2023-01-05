import logging

from django.core.management.base import BaseCommand, CommandError, CommandParser

from monitor.audio import Audio
from monitor.mqtt import MQTT

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Monitor audio level via a soundcard"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--list-devices",
            action="store_true",
            help="List the available audio devices and exit",
        )

        parser.add_argument(
            "--device-index",
            type=int,
            default=0,
            help="The index of the audio device to use",
        )

    def handle(
        self,
        list_devices: bool = False,
        device_index: int = 0,
        *args,
        **options,
    ) -> None:
        audio = Audio()
        mqtt = MQTT()

        if list_devices:
            devices = audio.list_input_devices()
            for idx, name in devices.items():
                self.stdout.write(f"{idx}: {name}")
            return

        mqtt.connect()
        for data, rms in audio.data_and_rms(input_device_index=device_index):
            log.debug("rms: %s", rms)
            mqtt.publish("rms", rms)
            mqtt.publish("audio", data)
