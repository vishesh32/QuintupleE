import paho.mqtt.client as paho
import json
from pydantic import BaseModel

# required to not recieve same msg as one sent
RCV = "rcv/"
SND = "snd/"

SUN_TOPIC = "sun"
EXT_GRID_TOPIC = "external-grid"
STORAGE_TOPIC = "storage"

class SMPS(BaseModel):
	SMPS: str
	power_in: int
	power_out: int

class MClient():
    def __init__(self, broker_addr="localhost", broker_port=1883, keepalive=120):
        self.client = paho.Client(paho.CallbackAPIVersion.VERSION2)
        self.client.on_connect = handle_connect
        self.client.on_message = handle_msg

        # client.username_pw_set(username="quintuplee", password="solar1")

        if self.client.connect(broker_addr, broker_port, keepalive=keepalive) != 0:
            raise Exception("Failed to connect to Broker")
        else:
            self.client.loop_start()
        
    def send_sun_data(self, smps: SMPS):
        self.client.publish(RCV+SUN_TOPIC, json.dumps(**smps.model_dump()), 0)

    def send_ext_grid_smps(self, smps: SMPS):
        self.client.publish(RCV+EXT_GRID_TOPIC, json.dumps(**smps.model_dump()), 0)

    def send_storage_smps(self, smps: SMPS):
        self.client.publish(RCV+STORAGE_TOPIC, json.dumps(**smps.model_dump()), 0)

    def end(self):
        self.client.disconnect()
    
    # TODO: add a way to monitor the load

def handle_connect(client, userdata, flags, rc, o):
    if rc != 0: raise Exception("Failed to connect to Broker")

    client.subscribe(SND+SUN_TOPIC)
    client.subscribe(SND+EXT_GRID_TOPIC)
    client.subscribe(SND+STORAGE_TOPIC)

    print("Connected to Broker")

def handle_msg(client, userdata, message):
    # when it recieves data from the server
    # send a response on the effect of the change
    print(f"Message received: {message.payload.decode()} on topic {message.topic}")