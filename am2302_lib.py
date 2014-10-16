'''
Synchronous and Asynchronous(TBD) functions to
read data from AM2302 humidity/temperature sensor.
Return (OK) : python object containing result
Return (read fail): null

Note:
The sensor data stream is a little flakey so it may take
multiple reads to get a valid answer.
The CRC check will make sure you only get good readings.
The function will try N times before giving up.
It will use a back-off algorithm adding 1 second between tries.
'''

import RPi.GPIO as GPIO
import time

DEBUG = False       # set true to get debug printout

AM2302_GPIO = 4     # data i/o pin BCM numbering
MAX_RETRIES = 10    # maximum number for retires before give up
RETRY_INCREMENT = 1 # seconds to add for every retry (backoff)

def bin2dec(string_num):
    return int(string_num, 2)

def getBit(data, startIx):
    '''
    extract data bit by scanning buffer for a framing pattern
    start at given index
      skip leading 0's
      1,2 or 3 1's = 0 bit
      4 or more 1's = 1 bit
      stop on first 0
    return stop index and resulting bit value as: "0" or "1"
    '''
    ix = startIx
    while data[ix] == 0:
        ix = ix + 1    
    bitValue = "0"
    bitCount = 0
    while data[ix] == 1:
        bitCount = bitCount + 1
        ix = ix + 1
    if bitCount > 3:
        bitValue = "1"
    if DEBUG:
        print('getBit[',startIx,'-',ix,']: ',bitValue)
    return (ix, bitValue)

def getReading():

    # set RPi to GPIO pin reference mode
    GPIO.setmode(GPIO.BCM)

    good_read = False
    retry_wait = 2      # initial retry wait
    for i in range(MAX_RETRIES):
        X = doReadCycle(retry_wait)
        if X[0]:
            good_read = True
            break
        retry_wait = retry_wait + RETRY_INCREMENT

    GPIO.cleanup(AM2302_GPIO)
    if good_read:
        if DEBUG:
            print('Reading: ', X)
        return X
    else:
        if DEBUG:
            print('Read failed')
        return X

def doReadCycle(wait):
    data_buffer = []
    if DEBUG:
        print('waiting (sec.): ', wait)
    time.sleep(wait)
    # send start read signal and switch to input mode
    GPIO.setup(AM2302_GPIO,GPIO.OUT)
    GPIO.output(AM2302_GPIO,GPIO.LOW)
    time.sleep(0.010)   # 10mSec start signal
    GPIO.setup(AM2302_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # get a buffer full of data
    for i in range(400):
        data_buffer.append(GPIO.input(AM2302_GPIO))
    dataT = time.time()
    if DEBUG:
        print ('data: ', data_buffer)

    humidityBits = ""
    temperatureBits = ""

    try:
        # skip start bit
        x = getBit(data_buffer, 0)
        
        # get humidity bits
        for i in range(16):
            x = getBit(data_buffer, x[0])
            humidityBits = humidityBits + x[1]

        # get temperature bits
        for i in range(16):
            x = getBit(data_buffer, x[0])
            temperatureBits = temperatureBits + x[1]

        # compute CRC (sum 4 bytes modulo 256 = crc byte)
        crcSum = 0
        crcError = False
        dataError = False
        x = getBit(data_buffer, 0)   # skip start bit
        for j in range(4):
            sumBits = ""
            for i in range(8):
                x = getBit(data_buffer, x[0])
                sumBits = sumBits + x[1]
            if DEBUG:
                print ('sumBits: ', sumBits)
            crcSum = crcSum + bin2dec(sumBits)
        crcSum = crcSum % 256 # truncate to 8 bits
        crcBits = ""
        for i in range(8):
            x = getBit(data_buffer, x[0])
            crcBits = crcBits + x[1]
        if DEBUG:
            print('crcBits: ', crcBits)
        crc = bin2dec(crcBits)
        if crcSum != crc:
            print('CRC Error -- crcSum: ', crcSum, ' crc: ', crc)
            crcError = True
    except:
        print ('Data Length Error')
        dataError = True

    if not dataError and not crcError:
        Humidity = bin2dec(humidityBits)
        Temperature = bin2dec(temperatureBits)
        reading = {}
        reading['local_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        reading['source_date'] = int(time.time()*1000)
        reading['humidity'] = Humidity/10.0
        reading['temperature_c'] = Temperature/10.0
        reading['temperature_f'] = round(((Temperature * 9) / 5) / 10.0 + 32.0, 1)
        return (True, reading)
    else:
        return (False, {})

# for testing standalone
#tryOne = getReading()
#print('tryOne: ', tryOne)

