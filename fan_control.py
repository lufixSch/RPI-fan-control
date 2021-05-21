#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import time
import atexit
import RPi.GPIO as GPIO

# Configuration
FAN_PIN = 18            # BCM pin used to drive PWM fan
WAIT_TIME = 1           # [s] Time to wait between each refresh
PWM_FREQ = 25           # [kHz] 25kHz for Noctua PWM control

# Configurable temperature and fan speed
MIN_TEMP = 40
MIN_TEMP_DEAD_BAND = 5
MAX_TEMP = 70
FAN_LOW = 1
FAN_HIGH = 100
FAN_OFF = 0
FAN_MAX = 100


def getCpuTemperature():
    """Get CPU's temperature"""
    res = os.popen('cat /sys/class/thermal/thermal_zone0/temp').readline()

    return float(res)/1000


def setFanSpeed(speed):
    """Set fan speed"""
    fan.start(speed)
    return()


def handleFanSpeed(temperature, handle_dead_zone):
    """Handle fan speed"""

    # Turn off the fan if lower than lower dead band
    if handle_dead_zone:
        setFanSpeed(FAN_OFF)
        return

    # Run fan at calculated speed if being in or above dead zone not having passed lower dead band
    if (not handle_dead_zone) and temperature < MAX_TEMP:
        step = float(FAN_HIGH - FAN_LOW)/float(MAX_TEMP - MIN_TEMP)
        temperature -= MIN_TEMP
        setFanSpeed(FAN_LOW + (round(temperature) * step))
        return

    # Set fan speed to MAXIMUM if the temperature is above MAX_TEMP
    if temperature > MAX_TEMP:
        setFanSpeed(FAN_MAX)
        return


def handleDeadZone(temperature):
    """Handle dead zone bool"""

    if temperature > (MIN_TEMP + MIN_TEMP_DEAD_BAND/2):
        return False
    # if temperature < (MIN_TEMP - MIN_TEMP_DEAD_BAND/2):
    #    return False

    return True


def resetFan():
    """Reset fan to 100% by cleaning GPIO ports"""
    GPIO.cleanup()  # resets all GPIO ports used by this function


try:
    # Setup GPIO pin
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FAN_PIN, GPIO.OUT, initial=GPIO.LOW)
    fan = GPIO.PWM(FAN_PIN, PWM_FREQ)
    # setFanSpeed(FAN_OFF)
    # Handle fan speed every WAIT_TIME sec
    while True:
        temp = getCpuTemperature()
        handleFanSpeed(temp, handleDeadZone(temp))
        time.sleep(WAIT_TIME)

except KeyboardInterrupt:  # trap a CTRL+C keyboard interrupt
    resetFan()

atexit.register(resetFan)
