"use client"

import mqtt from "mqtt";
// const mqtt = require('mqtt');

class MQTTClient{
    private client: any;

    constructor(address: string = 'localhost', port: number = 9001){
        this.client = mqtt.connect(`ws://${address}:${port}`);
        this.client.on('connect', () => console.log("Connected to MQTT Broker"));
        this.client.on('error', (err: any) => console.error(err));
        this.client.on('message', (topic: any, payload: any) => {
            const msg = payload.toString();
            console.log(`Received message on topic ${topic}: ${msg}`);
        })

        this.client.subscribe('rcv/sun', (err: any) => {
            if(err) console.error(err);
        });
    }
}

export { MQTTClient }