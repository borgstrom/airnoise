import influxdb_client
from influxdb_client.client.write_api import ASYNCHRONOUS, SYNCHRONOUS

import settings


class Influx:
    client: influxdb_client.InfluxDBClient
    write_api: influxdb_client.WriteApi

    def __init__(self):
        self.client = influxdb_client.InfluxDBClient(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG,
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def point(self, name: str) -> influxdb_client.Point:
        return influxdb_client.Point(name)

    def write(self, record):
        self.write_api.write(bucket=settings.INFLUXDB_BUCKET, org=settings.INFLUXDB_ORG, record=record,)
