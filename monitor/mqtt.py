import logging
from queue import Queue
from threading import Lock, Thread
import time
from typing import Any, Callable, Dict, Optional

import paho.mqtt.client as mqtt

import settings

log = logging.getLogger(__name__)

# Expose things so they can be imported and used for typing
MQTTMessage = mqtt.MQTTMessage
Client = mqtt.Client


class MQTT:
    client: Client
    thread: Thread
    queue: Queue
    lock: Lock
    subscriptions: Dict[str, Callable[[MQTTMessage], None]]

    def __init__(self):
        log.info("Creating MQTT client")
        self.subscriptions = {}
        self.queue = Queue()
        self.lock = Lock()
        self.thread = Thread(target=self.message_handler, daemon=True)
        self.thread.start()

        self.client = mqtt.Client()
        self.client.loop_start()
        self.client.enable_logger()
        self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        self.connect()

    def connect(self) -> None:
        if self.client.is_connected():
            return

        log.info(f"Connecting to {settings.MQTT_HOST}")
        self.client.connect(settings.MQTT_HOST)
        while not self.client.is_connected():
            time.sleep(0.1)

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

    def message_handler(self):
        log.info("Message handler starting")
        while True:
            subscription, msg = self.queue.get()
            with self.lock:
                callback = self.subscriptions.get(subscription, None)
            if callback:
                try:
                    callback(msg)
                except Exception:
                    log.exception(
                        "Failed to handle message in subscription: %s -> %s",
                        subscription,
                        msg,
                    )

    def subscribe(self, subscription: str, callback: Callable[[MQTTMessage], None]):
        def handle(client: Client, userdata: Optional[Any], msg: MQTTMessage):
            self.queue.put((subscription, msg))

        with self.lock:
            self.subscriptions[subscription] = callback

        self.client.message_callback_add(subscription, handle)
        self.client.subscribe(subscription)
