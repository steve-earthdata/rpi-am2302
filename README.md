rpi-am2302
==========

Raspberry Pi based example using Python to publish sensor data to the earthdata.io api.  An AM2302 humidity/temperature sensor is utilized in this example.

The following is a data sample as it is retrieved (GET) from the earthdata.io api and includes the automatically added attributes:

```
  {
    "temperature_c": 25.1,
    "humidity": 48,
    "temperature_f": 77.2,
    "local_time": "2014-10-15 22:51:18",
    "source_date": 1413438678407,
    "device_id": "53f647b20de296b9342d8e39",
    "user_id": 6,
    "server_date": 1413438678454
  },
```
