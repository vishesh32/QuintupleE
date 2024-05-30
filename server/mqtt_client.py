import paho.mqtt.client as paho
import json

# required to not recieve same msg as one sent
RCV = "rcv/"
SND = "snd/"

SUN_TOPIC = "sun"
EXT_GRID_TOPIC = "external-grid"
STORAGE_TOPIC = "storage"

class MClient():
    def __init__(self, broker_addr="localhost", broker_port="1883"):
        self.client = paho.Client(paho.CallbackAPIVersion.VERSION2)
        self.client.on_connect = handle_connect
        self.client.on_message = handle_msg

        # client.username_pw_set(username="quintuplee", password="solar1")

        if self.client.connect("localhost", 1883, keepalive=120) != 0:
            raise Exception("Failed to connect to Broker")
        else:
            self.client.loop_start()
        
    def send_sun_data(self, sun_val):
        self.client.publish(SND+SUN_TOPIC, json.dumps({"sun": sun_val}), 0)

    def send_ext_grid_smps(self, energy):
        self.client.publish(SND+EXT_GRID_TOPIC, json.dumps({"energy": energy}), 0)

    def send_storage_smps(self, energy):
        self.client.publish(SND+STORAGE_TOPIC, json.dumps({"energy": energy}), 0)

    def end(self):
        self.client.disconnect()
    
    # TODO: add a way to monitor the load


def handle_connect(client, userdata, flags, rc, o):
    if rc != 0: raise Exception("Failed to connect to Broker")

    client.subscribe(RCV+SUN_TOPIC)
    client.subscribe(RCV+EXT_GRID_TOPIC)
    client.subscribe(RCV+STORAGE_TOPIC)

    print("Connected to Broker")

def handle_msg(client, userdata, message):
    print(f"Message received: {message.payload.decode()} on topic {message.topic}")
    # when message recieved - write to DB