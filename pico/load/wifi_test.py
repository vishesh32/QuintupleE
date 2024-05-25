import network
import socket
from time import sleep
# from picozero import pico_temp_sensor, pico_led
import machine
import urequests as requests

ssid = ''
password = ''

URL='https://f766-146-169-205-109.ngrok-free.app/test'

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    print(f'connection: {wlan.isconnected()}\n\nIP: {wlan.ifconfig()}')

def get_test():
    res = requests.get(URL)
    print(res.text)

try:
    connect()
    get_test()
except KeyboardInterrupt:
    machine.reset()