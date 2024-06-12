"use client"
import mqtt from "mqtt";

const picoTopic = "pico";
const serverTopic = "server";
const uiTopic = "ui";

const prec = 2;

class MQTTClient{
    private client: any;
    public pvArrayPower: number = 0;
    public loadPowers: number[] = [0,0,0,0];

    constructor(setCurrentPV: any, setLoadPowers: any, setImportPower: any, setExportPower: any, address: string = '18.130.108.45', port: number = 9001){
        this.client = mqtt.connect(`ws://${address}:${port}`);
        this.client.on('connect', () => console.log("Connected to MQTT Broker"));
        this.client.on('error', (err: any) => console.error(err));
        this.client.on('message', (topic: any, message: any) => {
            console.log(`Received message on topic ${topic}: ${message.toString()}`);
            const msgObj = JSON.parse(message.toString());

            // this is data that is to be sent and stored on the server
            if(topic === serverTopic && "target" in msgObj && "payload" in msgObj){
                // console.log("Received data from server")
                // send data to server
                switch(msgObj.target){
                    case Device.PV_ARRAY: {
                        // console.log("PV Array Power: ", msgObj.payload);
                        // this.pvArrayPower = msgObj.payload.toFixed(prec);
                        setCurrentPV(msgObj.payload.toFixed(prec));
                        // console.log("PV Array Power: ", this.pvArrayPower);
                        break;
                    }
                    case Device.LOADR: {
                        // this.loadPowers[0] = msgObj.payload.toFixed(prec);
                        setLoadPowers((prev: number[])=>{
                            const old = [...prev];
                            old[0] = msgObj.payload.toFixed(prec);
                            return old;
                        })
                        break;
                    }
                    case Device.LOADB: {
                        // this.loadPowers[1] = msgObj.payload.toFixed(prec);
                        setLoadPowers((prev: number[])=>{
                            const old = [...prev];
                            old[1] = msgObj.payload.toFixed(prec);
                            return old;
                        })
                        break;
                    }
                    case Device.LOADY: {
                        // this.loadPowers[2] = msgObj.payload.toFixed(prec);
                        setLoadPowers((prev: number[])=>{
                            const old = [...prev];
                            old[2] = msgObj.payload.toFixed(prec);
                            return old;
                        })
                        break;
                    }
                    case Device.LOADK: {
                        // this.loadPowers[3] = msgObj.payload.toFixed(prec);
                        setLoadPowers((prev: number[])=>{
                            const old = [...prev];
                            old[3] = msgObj.payload.toFixed(prec);
                            return old;
                        })
                        break;
                    }
                    case Device.STORAGE: {
                        if(msgObj.payload.import_power) setImportPower(msgObj.payload.import_power.toFixed(prec));
                        else setExportPower(msgObj.payload.export_power.toFixed(prec));
                        // console.log(msgObj.payload.import_power)
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

    send_load_power(val: number, load: string){
        this.client.publish(picoTopic, JSON.stringify({"target": load, "payload": val}));
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