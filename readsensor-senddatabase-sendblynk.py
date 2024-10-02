#!/usr/bin/python
import smbus2 as smbus
import time
import Adafruit_ADS1x15
import RPi.GPIO as GPIO
import MySQLdb
import BlynkLib
from BlynkTimer import BlynkTimer

# Blynk Auth Token
BLYNK_AUTH_TOKEN = 'M3dMkhIHgYMoOvQtz_9FDPuyS3cteKe0'

# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH_TOKEN)
timer = BlynkTimer()

# Constants for BH1750
DEVICE = 0x23  # Default device I2C address
ONE_TIME_HIGH_RES_MODE = 0x20

# Setup I2C bus
bus = smbus.SMBus(1)

# Setup GPIO for Ultrasonic Sensor
GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Create an ADC instance for LM35 (ADS1015 or ADS1115)
adc = Adafruit_ADS1x15.ADS1115(busnum=1)
analog_channel = 0

# Disable GPIO warnings (optional)
GPIO.setwarnings(False)

# Connect to MySQL database
db = MySQLdb.connect("localhost", "root", "rahasia", "sensor_data")
cursor = db.cursor()

# Functions to read from sensors
def convertToNumber(data):
    return ((data[1] + (256 * data[0])) / 1.2)

def readLight(addr=DEVICE):
    data = bus.read_i2c_block_data(addr, ONE_TIME_HIGH_RES_MODE, 2)
    return convertToNumber(data)

def distance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    TimeElapsed = StopTime - StartTime
    dist = (TimeElapsed * 34300) / 2

    return dist

def read_lm35_temperature():
    raw_value = adc.read_adc(analog_channel, gain=1)
    millivolts = (raw_value * 4.096) / 32767.0 * 1000
    temperature_celsius = millivolts / 10.0
    temperature_fahrenheit = (temperature_celsius * 9/5) + 32
    return temperature_celsius, temperature_fahrenheit

# Function to send sensor data to Blynk and save to database
def send_sensor_data():
    light_level = readLight()
    dist = distance()
    celsius, fahrenheit = read_lm35_temperature()

    # Send data to Blynk
    blynk.virtual_write(0, celsius)  # V0 for temperature
    blynk.virtual_write(1, dist)     # V1 for distance
    blynk.virtual_write(2, light_level)  # V2 for light intensity

    # Insert data into MySQL database
    query = """INSERT INTO sensor_readings (distance, light, temp) VALUES (%s, %s, %s)"""
    cursor.execute(query, (dist, light_level, celsius))
    db.commit()
    
    # Print to console for debugging
    print(f"Light Level: {light_level:.2f} lux")
    print(f"Distance: {dist:.2f} cm")
    print(f"Temperature: {celsius:.2f}°C ~ {fahrenheit:.2f}°F")

# Setup a timer to send data every 5 seconds
timer.set_interval(5, send_sensor_data)

# Main loop
try:
    while True:
        blynk.run()
        timer.run()
except KeyboardInterrupt:
    GPIO.cleanup()
    db.close()