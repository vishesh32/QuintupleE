"use client"

import mqtt from "mqtt";
// const mqtt = require('mqtt');

class MQTTClient{
    private client: any;

    constructor(address: string = '18.130.108.45', port: number = 9001){
        this.client = mqtt.connect(`ws://${address}:${port}`);
        this.client.on('connect', () => console.log("Connected to MQTT Broker"));
        this.client.on('error', (err: any) => console.error(err));
        this.client.on('message', (topic: any, message: any) => {
            const msgObj = JSON.parse(message.toString());
            console.log(`Received message on topic ${topic}: ${msgObj.toString()}`);

            if(topic === 'server'){
                
            }
        })

        this.client.subscribe('server', (err: any) => {
            if(err) console.error(err);
        });
        this.client.subscribe('ui', (err: any) => {
            if(err) console.error(err);
        });
    }
}

export { MQTTClient }