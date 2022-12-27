# AirNoise

# Adding mqtt user

```
docker run --rm -it -v ${PWD}\mqtt\config:/mosquitto/config eclipse-mosquitto:2 mosquitto_passwd /mosquitto/config/password.txt mqtt1
```