import paho.mqtt.client as paho
import json
from models import SMPS
from enum import Enum

# all the picos you can connect to
# sent a message to the pico using the PICO_TOPIC
# then in the message body, send the device in the target
# this is used in hardware as well
class Device(Enum):
    STORAGE = "storage"
    EXTERNAL_GRID = "external-grid"
    PV_ARRAY = "pv-array"
    LOADR="loadR"
    LOADY="loadY"
    LOADB="loadB"
    LOADK="loadK"

PICO_TOPIC = "pico"
SERVER_TOPIC = "server"

class MClient:
    def __init__(self, broker_addr="18.130.108.45", broker_port="1883"):
        self.client = paho.Client(paho.CallbackAPIVersion.VERSION2)
        self.client.on_connect = handle_connect
        self.client.on_message = self.handle_msg
        self.db_data = {}

        # self.client.username_pw_set(username="admin", password="QuintupleE1")
        # self.client.tls_set(
        #     ca_certs=None,
        #     certfile=None,
        #     keyfile=None,
        #     cert_reqs=paho.ssl.CERT_REQUIRED,
        #     tls_version=paho.ssl.PROTOCOL_TLSv1_2,
        #     ciphers=None,
        # )

        # self.client.loop_start()
        if  self.client.connect(broker_addr, broker_port, keepalive=1000) != 0:
            raise Exception("Failed to connect to Broker")
        else:
            self.client.loop_start()

    def send_sun_data(self, sun_val):
        self.client.publish(PICO_TOPIC, json.dumps({"target": Device.PV_ARRAY.value, "payload": sun_val}), 2)

    # def send_external_grid(self, power):
    #     self.client.publish(PICO_TOPIC, json.dumps({"target": Device.EXTERNAL_GRID.value, "payload": power}), 2)

    def send_storage_power(self, power):
        self.client.publish(PICO_TOPIC, json.dumps({"target": Device.STORAGE, "payload": power}), 2)

    # transmit actual voltage div by 10
    def send_load_power(self, load: Device, power):
        self.client.publish(PICO_TOPIC, json.dumps({"target": Device.STORAGE, "payload": power}), 2)

    def end(self):
        self.client.disconnect()

    def handle_msg(self, client, userdata, message):
        msg_str = message.payload.decode()
        topic = message.topic
        print(f"Message received: {msg_str} on topic {topic}")

        data = json.loads(msg_str)

        if "target" not in data or "payload" not in data:
            raise Exception("Invalid message format")
        
        elif data["target"] == Device.EXTERNAL_GRID.value:
            import_power = data["payload"]["import_power"] 
            export_power = data["payload"]["export_power"]

        elif data["target"] == Device.PV_ARRAY.value:
            pv_power = data["payload"]
        
        elif data["target"] == Device.STORAGE.value:
            if data["payload"]["type"] == "soc":
                soc = data["payload"]["value"]
            elif data["payload"]["type"] == "power":
                power = data["payload"]["value"]

        else:
            # then use target to check what type of load it is
            # target is storing it as a string
            load = data["target"]
            load_power = data["payload"]
            pass
            



def handle_connect(client, userdata, flags, rc, o):
    if rc != 0:
        raise Exception("Failed to connect to broker")
    client.subscribe(SERVER_TOPIC)
    print("Connected to Broker")
