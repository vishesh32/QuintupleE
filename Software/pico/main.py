import machine
import ubinascii
from wifi import init
import json

TOPIC = "snd"

MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_BROKER = "0.tcp.eu.ngrok.io"
MQTT_BROKER_PORT = 19663

irradiance = -1

# data format example for irradiance:
# { name: "irradiance", payload: 10 }
def on_mqtt_msg(topic, msg):
    topic_str = topic.decode()
    msg_str = msg.decode()

    print(f"topic: {topic_str} | msg_str: {msg_str}")

    data = json.loads(msg_str)
    if data["name"] == "irradiance":
        irradiance = data["payload"]
        print(f"irradiance: {irradiance}")


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

    client.subscribe(TOPIC)

    print(f"Waiting for messages on {TOPIC}")
    client.publish(TOPIC, "Hello from Pico")
    while True:
        client.check_msg()


try:
    main()

except Exception as e:
    print(e)
    print("\n\n\n")
    machine.reset()
