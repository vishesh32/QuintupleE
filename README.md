# Quintuple E

## Software Folder

- broker/mosquitto.conf - contains the configuration file for the mosquitto broker.

- dashboard - contains the code for the UI

    - app - contains the code for each page
    
    - app/actions.ts - contains functions for the Next.js server actions

    - components - custom UI elements used throughout the dashboard

    - helper - contains code used to get and process graph data and data from the MQTT broker

- pico_simulation - MQTT client used to test the UI and backend service

- server/main.py - runs the algorithm for the backend service

- server/external - contains optimisations to fetch data and sync with the external web server

- server/optimisation - contains files to run the optimisation algorithm

- trend_prediction - contains notebooks on tests we ran with the data generated from the external web server

- trend_prediction/price_prediction - contains models built to predict the buy price from the external web server

## Hardware

- Each hardware subsystem has its own folder with the code running on the Pico W

- Server Comms - contains code to run on all picos:

    - Server Comms/mqtt_client.py - to connect, receive and send messages with the MQTT broker
    
    - Server Comms/wifi.py - to connect the Pico W to the internet

## Videos

- [Grid UI Video](https://youtu.be/6DRRmUU25tM?si=uK3EfAKqUYMd-oMA) - Explanation of the grid UI used in the dashboard.

- [MPPT Explanation Video](https://youtu.be/Mqih-1-pDE8?si=VUjKUSX0d-B3s6bj) - Explanation of the MPPT used in demo.
