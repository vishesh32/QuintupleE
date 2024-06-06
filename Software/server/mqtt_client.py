import paho.mqtt.client as paho
import json
from models import SMPS

# required to not recieve same msg as one sent
RCV = "rcv/"
SND = "snd/"

SUN_TOPIC = "sun"
EXT_GRID_TOPIC = "external-grid"
STORAGE_TOPIC = "storage"
LOAD_TOPICS = ["load1", "load2", "load3", "load4"]

MQTT_URL = "6ace09b77c4546d5bd66c724bc9abb0e.s1.eu.hivemq.cloud:8883"


class MClient:
    def __init__(self, broker_addr="localhost", broker_port="1883"):
        self.client = paho.Client(paho.CallbackAPIVersion.VERSION2)
        self.client.on_connect = handle_connect
        self.client.on_message = self.handle_msg
        self.db_data = {}

        # client.username_pw_set(username="quintuplee", password="solar1")
        # self.client.username_pw_set(username="your_username", password="your_password")
        self.client.username_pw_set(username="admin", password="QuintupleE1")
        self.client.tls_set(
            ca_certs=None,
            certfile=None,
            keyfile=None,
            cert_reqs=paho.ssl.CERT_REQUIRED,
            tls_version=paho.ssl.PROTOCOL_TLSv1_2,
            ciphers=None,
        )

        self.client.connect(
            "6ace09b77c4546d5bd66c724bc9abb0e.s1.eu.hivemq.cloud", 8883, keepalive=120
        )

        self.client.loop_start()
        # if self.client.connect("localhost", 1883, keepalive=120) != 0:
        #     raise Exception("Failed to connect to Broker")
        # else:
        #     self.client.loop_start()

    def send_sun_data(self, sun_val):
        self.client.publish(SND + SUN_TOPIC, json.dumps({"sun": sun_val}), 0)

    def send_ext_grid_smps(self, energy):
        self.client.publish(SND + EXT_GRID_TOPIC, json.dumps({"energy": energy}), 0)

    def send_storage_smps(self, energy):
        self.client.publish(SND + STORAGE_TOPIC, json.dumps({"energy": energy}), 0)

    # transmit actual voltage div by 10
    def send_load(self, load_num, setpoint):
        if not (load_num >= 1 and load_num <= 4):
            raise Exception("Invalid value for load_num, when sending data to the load")

        self.client.publish(
            SND + LOAD_TOPICS[load_num - 1], json.dumps({"setpoint": setpoint}), 2
        )

    def end(self):
        self.client.disconnect()

    def handle_msg(self, client, userdata, message):
        msg_str = message.payload.decode()
        topic = message.topic
        print(f"Message received: {message.payload.decode()} on topic {message.topic}")

        self.db_data[topic] = json.loads(msg_str, object_hook=lambda x: SMPS(**x))
        # when message recieved - write to DB


def handle_connect(client, userdata, flags, rc, o):
    if rc != 0:
        raise Exception("Failed to connect to broker")

    client.subscribe(RCV + SUN_TOPIC)
    client.subscribe(RCV + EXT_GRID_TOPIC)
    client.subscribe(RCV + STORAGE_TOPIC)
    for load in LOAD_TOPICS:
        client.subscribe(RCV + load)

    print("Connected to Broker")
