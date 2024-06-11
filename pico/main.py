import network
import machine
from time import sleep
import network
import ssl
import ubinascii
from wifi import init
import json

SUN_TOPIC = "snd/sun"

MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_BROKER = "0.tcp.eu.ngrok.io"
MQTT_BROKER_PORT = 19663

sun = -1


def on_mqtt_msg(topic, msg):
    topic_str = topic.decode()
    msg_str = msg.decode()

    print(f"topic: {topic_str} | msg_str: {msg_str}")

    if topic_str == SUN_TOPIC:
        data = json.loads(msg_str)
        sun = data["sun"]
        print(f"sun: {sun}")


def mqtt_init():

    # from lib.simple import MQTTClient
    from umqtt.simple import MQTTClient

    client = MQTTClient(
        client_id=MQTT_CLIENT_ID,
        server=MQTT_BROKER,
        port=MQTT_BROKER_PORT,
        keepalive=1000,
    )

    print("Connecting to broker")

    client.set_callback(on_mqtt_msg)
    client.connect()

    print("Connected to broker")

    return client


def main():
    init()
    client = mqtt_init()

    client.subscribe(SUN_TOPIC)

    print(f"Waiting for messages on {SUN_TOPIC}")
    client.publish(SUN_TOPIC, "Hello from Pico")
    while True:
        client.check_msg()


try:
    main()

except Exception as e:
    print(e)
    print("\n\n\n")
    machine.reset()
