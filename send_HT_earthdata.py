#! /usr/bin/env python3
'''
Read and send AM2302 humidity/temperature to earthdata
'''

import requests
import json
import datetime
import time
import am2302_lib
import RPi.GPIO as GPIO

url = 'https://api.earthdata.io/v0'
print('using url: ', url)

DEVICE_ID = '53f647b20de296b9342d8e39'
user_login = {'username':'<USERNAME>','password':'<PASSWORD>'}

# setup activity LED
LED = 18
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# create a session object for REST messages
s = requests.Session()
s.headers.update({'content-type':'application/json'})

# login
r = s.post(url + '/login', data=json.dumps(user_login))
print('login status: ', r.status_code, ' text: ', r.text)

# example to get and print devices that user owns
r = s.get(url + '/devices')
print('get devices status: ', r.status_code)
devices = json.loads(r.text)
print('devices: ', devices)
for d in devices:
    print('name: ', d['name'], ' id: ', d['id'])

# send AM2302 device data
data_url = '/device-data/' + DEVICE_ID

# loop sending data forever
while True:
    X = am2302_lib.getReading()
    if X[0]:
        GPIO.setup(LED, GPIO.OUT)
        GPIO.output(LED, GPIO.HIGH)
        json_data = json.dumps(X[1])
        r = s.post(url + data_url, data=json_data)
        if r.status_code == 200:
            print('device-data return: ', r.text)
        elif r.status_code == 401:
            r = s.post(url + '/login', data=json.dumps(user_login))
            print('login status: ', r.status_code, ' text: ', r.text)
            if r.status_code != 200:
                print('login error: ', r.status_code, ' text: ', r.text)
                exit(1)
        else:
            print('un-recoverable error: ', r.status_code, ' text: ', r.text)
            exit(1)
        time.sleep(1.0)
        GPIO.output(LED, GPIO.LOW)
    else:
        ts = datetime.datetime.now().isoformat()
        print(ts, ' AM2302 READ FAILURE')
    time.sleep(58.0)    # sleep for 1 minute minus nominal sensor read time of 2 seconds

