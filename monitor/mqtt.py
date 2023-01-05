from dataclasses import dataclass, field
from typing import Any

import paho.mqtt.client as mqtt

import logging

import settings

log = logging.getLogger(__name__)

# Expose things so they can be imported and used for typing
MQTTMessage = mqtt.MQTTMessage
Client = mqtt.Client


class MQTT:
    client: mqtt.Client

    def __init__(self):
        log.info("Creating MQTT client")
        self.client = mqtt.Client()
        self.client.enable_logger()
        self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

    def connect(self) -> None:
        log.info(f"Connecting to {settings.MQTT_HOST}")
        self.client.connect(settings.MQTT_HOST)

    def publish(self, topic: str, payload: Any):
        def do_publish(retry: bool = False):
            ret = self.client.publish(
                topic=f"{settings.MQTT_USERNAME}/{topic}",
                payload=payload,
            )
            if ret.rc == mqtt.MQTT_ERR_SUCCESS:
                return

            if retry:
                log.error(f"Failed to publish, MQTT error code: {ret.rc}")
                return

            self.client.disconnect()
            self.connect()
            do_publish(retry=True)

        do_publish()

    def subscribe(self, subscription: str, callback):
        self.client.message_callback_add(subscription, callback)
        self.client.subscribe(subscription)
