import network
import socket
from time import sleep
# from picozero import pico_temp_sensor, pico_led
import machine
import urequests

ssid = ''
password = ''

# requests library only works with HTTP
# not enough space on pico for SSL encryption & decryption
URL='http://587c-185-238-220-193.ngrok-free.app'

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

    res = urequests.get(URL)

    print(res.text)

    res.close()

try:
    connect()
    get_test()
except KeyboardInterrupt:
    machine.reset()