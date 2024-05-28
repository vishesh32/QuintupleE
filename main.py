import requests
from time import sleep
import paho.mqtt.client as paho
import json

client = None
tick = -1

SUN_TOPIC = "external/sun"
HTTP_PERIOD = 1

try:
    client = paho.Client(paho.CallbackAPIVersion.VERSION2)

    if client.connect("localhost", 1883, keepalive=120) != 0:
        raise Exception("Failed to connect to the broker")

    while True:
        # TODO: make this run in parallel
        sun_data = requests.get("https://icelec50015.azurewebsites.net/sun").json()
        price_data = requests.get("https://icelec50015.azurewebsites.net/price").json()
        demand_data = requests.get("https://icelec50015.azurewebsites.net/demand").json()
        deferables_data = requests.get("https://icelec50015.azurewebsites.net/deferables").json()

        if tick == sun_data["tick"]: continue

        # part that runs the start of every new tick
        tick = sun_data["tick"]
        client.publish(SUN_TOPIC, json.dumps(sun_data), 0)
        print(f'Published to {SUN_TOPIC} | {str(sun_data)}')
        sleep(HTTP_PERIOD)


except Exception as e:
    print(e)

    if client:
        client.disconnect()