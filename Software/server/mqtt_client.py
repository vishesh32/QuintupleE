import paho.mqtt.client as paho
import json
from models import TickOutcomes

# all the picos you can connect to
# sent a message to the pico using the PICO_TOPIC
# then in the message body, send the device in the target
# this is used in hardware as well
class Device:
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
    def __init__(self, broker_addr="18.130.108.45", broker_port=1883):
        self.client = paho.Client(paho.CallbackAPIVersion.VERSION2)
        self.client.on_connect = handle_connect
        self.client.on_message = self.handle_msg
        self.db_data = {}

        if self.client.connect(broker_addr, broker_port, keepalive=1000) != 0:
            raise Exception("Failed to connect to Broker")
        else:
            self.client.loop_start()

    def send_sun_data(self, sun_val):
        self.client.publish(PICO_TOPIC, json.dumps({"target": Device.PV_ARRAY , "payload": sun_val}), 2)

    # def send_external_grid(self, power):
    #     self.client.publish(PICO_TOPIC, json.dumps({"target": Device.EXTERNAL_GRID , "payload": power}), 2)

    def send_storage_power(self, power):
        self.client.publish(PICO_TOPIC, json.dumps({"target": Device.STORAGE, "payload": power}), 2)

    # transmit actual voltage div by 10
    def send_load_power(self, load: str, power):
        self.client.publish(PICO_TOPIC, json.dumps({"target": load, "payload": power}), 2)

    def end(self):
        self.client.disconnect()

    def reset_db_data(self):
        self.db_data = {}

    def handle_msg(self, client, userdata, message):
        msg_str = message.payload.decode()
        topic = message.topic
        print(f"Message received: {msg_str} on topic {topic}")

        data = json.loads(msg_str)

        if "target" not in data or "payload" not in data:
            raise Exception("Invalid message format")
        
        elif data["target"] == Device.EXTERNAL_GRID:
            import_power = data["payload"]["import_power"] 
            export_power = data["payload"]["export_power"]
            if import_power == None:
                self.db_data["export_power"] += [export_power]
            else:
                self.db_data["import_power"] += [import_power]


        elif data["target"] == Device.PV_ARRAY:
            pv_power = data["payload"]
            self.db_data["pv_power"] += [pv_power]
        
        elif data["target"] == Device.STORAGE:
            if data["payload"]["type"] == "soc":
                soc = data["payload"]["value"]
                # self.db_data["soc"] = soc
                self.add_to_dict("soc", soc)
            elif data["payload"]["type"] == "power":
                storage_power = data["payload"]["value"]
                # self.db_data["storage_power"] += [storage_power]
                self.add_to_dict("storage_power", storage_power)

        else:
            # then use target to check what type of load it is
            # target is storing it as a string
            load = data["target"]
            load_power = data["payload"]
            self.add_to_dict(load, load_power)
        
        print(self.db_data)

    def add_to_dict(self, key, value):
        if key in self.db_data:
            self.db_data[key] += [value]
        else:
            self.db_data[key] = [value]

    def get_outcome_model(self, day, tick):
        try:
            return TickOutcomes(
                day=day,
                tick=tick,
                cost=0, # check how to calculate this
                avg_pv_energy=self._get_avg(self.db_data["pv_power"]),
                storage_soc=self.db_data["soc"],
                avg_import_energy=self._get_avg(self.db_data["import_power"]),
                avg_export_energy=self._get_avg(self.db_data["export_power"]),
                avg_red_energy=self._get_avg(self.db_data[Device.LOADR]),
                avg_blue_energy=self._get_avg(self.db_data[Device.LOADB]),
                avg_yellow_energy=self._get_avg(self.db_data[Device.LOADY]),
                avg_grey_energy=self._get_avg(self.db_data[Device.LOADK])
            )
        except:
            print("failed to create object")
            return None
        
    def _get_avg(self, data):
        return sum(data) / len(data)
            



def handle_connect(client, userdata, flags, rc, o):
    if rc != 0:
        raise Exception("Failed to connect to broker")
    client.subscribe(SERVER_TOPIC)
    print("Connected to Broker")
