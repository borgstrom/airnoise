from django.contrib.gis.db import models


class Location(models.Model):
    name = models.CharField(
        max_length=64,
    )

    def __str__(self) -> str:
        return self.name


class Flight(models.Model):
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
    )

    icao_24bit_hex = models.CharField(
        max_length=16,
    )
    flight_name = models.CharField(
        max_length=32,
        blank=True,
    )
    first_seen = models.DateTimeField(
        auto_now_add=True,
    )
    last_seen = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self) -> str:
        return f"{self.icao_24bit_hex} ({self.flight_name})"


class FlightData(models.Model):
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="data",
    )
    added = models.DateTimeField(
        auto_now_add=True,
    )
    squawk_code = models.CharField(
        max_length=16,
        blank=True,
    )
    rms = models.IntegerField()
    point = models.PointField()
    altitude = models.PositiveIntegerField()


class AudioBuffer(models.Model):
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
    )

    added = models.DateTimeField(
        auto_now_add=True,
    )
    data = models.BinaryField()
