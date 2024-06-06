import network
from time import sleep


ssid = 'DESKTOP-KLGKDPF 1457'
password = '371Mu9(0'

def init():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    print(f'connection: {wlan.isconnected()}\n\nIP: {wlan.ifconfig()}')

    import mip
    # mip.install('https://raw.githubusercontent.com/micropython/micropython-lib/b50d3462d783e4aab2f10d6b8117641244918f64/micropython/umqtt.simple/umqtt/simple.py')
    mip.install("umqtt.simple")

if __name__ == "__main__":
    init()