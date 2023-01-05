from django.contrib.gis.db import models


class Flight(models.Model):
    icao_24bit_hex = models.CharField(
        max_length=16,
    )
    flight_name = models.CharField(
        max_length=32,
        blank=True,
    )
    squawk_code = models.CharField(
        max_length=16,
        blank=True,
    )
    first_seen = models.DateTimeField(
        auto_now_add=True,
    )
    last_seen = models.DateTimeField(
        auto_now=True,
    )


class FlightData(models.Model):
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="data",
    )
    added = models.DateTimeField(
        auto_now_add=True,
    )
    rms = models.IntegerField()
    point = models.PointField()
    altitude = models.PositiveIntegerField()
