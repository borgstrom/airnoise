from dataclasses import dataclass, field
from typing import Any

import paho.mqtt.client as mqtt

import logging

log = logging.getLogger(__name__)


@dataclass
class MQTT:
    host: str
    username: str
    password: str

    client: mqtt.Client = field(init=False)

    def __post_init__(self):
        log.info("Creating MQTT client")
        self.client = mqtt.Client()
        self.client.username_pw_set(self.username, self.password)

    def connect(self) -> None:
        log.info(f"Connecting to {self.host}")
        self.client.connect(self.host)

    def publish(self, topic: str, payload: Any):
        self.client.publish(
            topic=f"{self.username}/topic",
            payload=payload,
        )
