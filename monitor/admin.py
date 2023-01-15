from django.contrib.gis import admin

from monitor.models import Flight, FlightData, Location


class FlightDataInline(admin.TabularInline):
    model = FlightData


class FlightAdmin(admin.GISModelAdmin):
    list_display = ("icao_24bit_hex", "flight_name", "first_seen", "last_seen")
    ordering = ("-last_seen",)
    inlines = (FlightDataInline,)


admin.site.register(Location)
admin.site.register(Flight, FlightAdmin)
