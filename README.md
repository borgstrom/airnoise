# AirNoise

# Setup dump1090

RTL SDR used: [ADSBexchange.com Blue R820T2 RTL2832U, 0.5 PPM TCXO ADS-B SDR w/Amp and 1090 Mhz Filter](https://www.amazon.com/dp/B09F2ND4R6)

Run `lsusb` to find the RTL SDR card and add a udev rule by creating `/etc/udev/rules.d/20.rtl-sdr.rules`:

```
# Bus 001 Device 006: ID 0bda:2832 Realtek Semiconductor Corp. RTL2832U DVB-T
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2832", GROUP="adm", OWNER="dump1090", MODE="0666", SYMLINK+="rtl_sdr"
```

On Ubuntu install the `dump1090-mutability` package.

1. Disable all network ports.
1. Set max distance to 100NM
1. Extra options: `--modeac --mlat`
1. Everything else was left default

Restart the service (`sudo service dump1090-mutability restart`) and ensure data is being written to `/run/dump1090-mutability/aircraft.json`


# Adding mqtt user

```
docker run --rm -it -v ${PWD}/mosquitto/config:/mosquitto/config eclipse-mosquitto:2 mosquitto_passwd /mosquitto/config/password.txt XXXX
```

# Setup MQTT credentials in `.env`

Add a `.env` file with the contents:

```
AIRNOISE_MQTT_HOST=localhost
AIRNOISE_MQTT_USERNAME=XXXX
AIRNOISE_MQTT_PASSWORD=YYYY
```
