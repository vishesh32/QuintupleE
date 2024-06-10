import machine
import ubinascii
from wifi import init
import json

# uncomment this line to import the helper functions
# and line 60
# from helper_functions import get_desired_power

TOPIC = "pico"
SERVER_TOPIC = "server"
UI_TOPIC = "ui"

MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_BROKER = "18.130.108.45"
MQTT_BROKER_PORT = 1883

# data format example for irradiance:

class MClient:
    def __init__(self, topic=TOPIC):
        init()

        from umqtt.simple import MQTTClient

        client = MQTTClient(
            client_id=MQTT_CLIENT_ID,
            server=MQTT_BROKER,
            port=MQTT_BROKER_PORT,
            keepalive=1000,
        )

        print("Connecting to broker")

        client.set_callback(self.on_mqtt_msg)
        client.connect()

        self.client = client
        self.client.subscribe(topic)
        print(f"Waiting for messages on {topic}")

        self.topic = topic
        self.desired_power = 0
        self.power_req = 0
    
    def on_mqtt_msg(self, topic, msg):
        # topic_str = topic.decode()
        msg_str = msg.decode()

        # print(f"topic: {topic_str} | msg_str: {msg_str}")

        data = json.loads(msg_str)
        if data["target"] == "snd/storage":
            self.desired_power = data["payload"]
            # print(f"desired_power: {self.desired_power}")
        elif data["target"] == "snd/load":
            self.power_req = data["payload"]
            print(f"power_req: {self.power_req}")

    def check_msg(self):
        self.client.check_msg()

    def get_desired_power(self):
        self.check_msg()
        # return get_desired_power(self.desired_power)
    
    def send_external_grid(self, import_p, export_p):
        self.client.publish(SERVER_TOPIC, json.dumps({"target": "external-grid", "payload":{"import_power": import_p, "export_power": export_p}}))

    def send_load_power(self, power):
        self.client.publish(SERVER_TOPIC, json.dumps({"target": "load", "payload": power}))

    def send_shunt_current(self, current):
        self.client.publish(UI_TOPIC, json.dumps({"target": "load-current", "payload": current}))

    def get_power_req(self):
        self.check_msg()
        return self.power_req

# try:
#     main()

# except Exception as e:
#     print(e)
#     print("\n\n\n")
#     machine.reset()
