"use client"
import mqtt from "mqtt";

const picoTopic = "pico";
const serverTopic = "server";
const uiTopic = "ui";

class MQTTClient{
    private client: any;
    public pvArrayPower: number = 0;

    constructor(address: string = '18.130.108.45', port: number = 9001){
        this.client = mqtt.connect(`ws://${address}:${port}`);
        this.client.on('connect', () => console.log("Connected to MQTT Broker"));
        this.client.on('error', (err: any) => console.error(err));
        this.client.on('message', (topic: any, message: any) => {
            const msgObj = JSON.parse(message.toString());
            console.log(`Received message on topic ${topic}: ${msgObj.toString()}`);

            // this is data that is to be sent and stored on the server
            if(topic === serverTopic && "target" in msgObj && "payloads" in msgObj){
                // send data to server
                switch(msgObj.target){
                    case Device.PV_ARRAY: {
                        this.pvArrayPower = msgObj.payloads;
                        break;
                    }
                }
            }
        })

        this.client.subscribe(serverTopic, (err: any) => {
            if(err) console.error(err);
        });
        this.client.subscribe(uiTopic, (err: any) => {
            if(err) console.error(err);
        });
    }

    send_irradiance(val: number){
        this.client.publish(picoTopic, JSON.stringify({"target": Device.PV_ARRAY, "payload": val}));
    }

    send_storage_power(val: number){
        this.client.publish(picoTopic, JSON.stringify({"target": Device.STORAGE, "payload": val}));
        console.log("here")
    }
}

// Devices, taken from the MQTT pico client
enum Device {
    STORAGE = "storage",
    EXTERNAL_GRID = "external-grid",
    PV_ARRAY = "pv-array",
    LOADR="loadR",
    LOADY="loadY",
    LOADB="loadB",
    LOADK="loadK"
}

export { MQTTClient, Device }