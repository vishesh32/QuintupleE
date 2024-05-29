import requests
from time import sleep
from parallel_get import parallel_get

import asyncio
import paho.mqtt.client as paho
import json
import sys
from optimisation.algorithm import (
    get_sun_energy,
    load_policy_network_checkpoint,
    predict,
)
from optimisation.utils import get_ema
from optimisation.gen_data import getDayData, getTickData
from optimisation.models import Day, Tick
import time


client = None
# tick = -1

SUN_TOPIC = "external/sun"
HTTP_PERIOD = 1


filename = "server/optimisation/checkpoints/pn_epochs1500_trajruns_10_ema100.pth"
policy_network = load_policy_network_checkpoint(filename)

# Test prediction
day_id = 0
tick_id = 0
day: Day = getDayData(day_id)

env = {
    "flywheel_amt": 0,
    "deferables": day.deferables,
}
history = []
overall_cost = 0
costs_per_day = []

RUN_BROKER = True
RUN_ALGO = False


def get_day_and_tick():

    # # TODO: make this run in parallel
    # sun_data = requests.get("https://icelec50015.azurewebsites.net/sun").json()
    # price_data = requests.get("https://icelec50015.azurewebsites.net/price").json()
    # demand_data = requests.get("https://icelec50015.azurewebsites.net/demand").json()
    # deferables_data = requests.get(
    #     "https://icelec50015.azurewebsites.net/deferables"
    # ).json()

    sun_data, price_data, demand_data, deferables_data = asyncio.run(
        parallel_get(
            "https://icelec50015.azurewebsites.net/",
            ["/sun", "/price", "/demand", "/deferables"],
        )
    )

    day = Day.model_validate({"day": price_data["day"], "deferables": deferables_data})

    tick = Tick.model_validate(
        {
            "tick": price_data["tick"],
            "sun": sun_data["sun"],
            "demand": demand_data["demand"],
            "sell_price": price_data["sell_price"],
            "buy_price": price_data["buy_price"],
            "day": price_data["day"],
        }
    )

    return day, tick


prev_tick = None
cost_per_day = 0
costs = []
try:
    if RUN_BROKER:
        client = paho.Client(paho.CallbackAPIVersion.VERSION2)

        # client.username_pw_set(username="quintuplee", password="solar1")

        if client.connect("localhost", 1883, keepalive=120) != 0:
            raise Exception("Failed to connect to the broker")

        print("Connected to broker")

    while True:
        day, tick = get_day_and_tick()

        if prev_tick and prev_tick.tick == tick.tick and prev_tick.day == tick.day:
            continue

        if prev_tick and prev_tick.tick == 59:
            env["deferables"] = day.deferables

        # part that runs the start of every new tick
        if RUN_ALGO:
            print("Day:", tick.day, "Tick:", tick.tick)
            print("Sun energy:", round(get_sun_energy(tick, 4), 3))
            print("Flywheel Amt:", round(env["flywheel_amt"], 3))
            print("Inst D:", round(tick.demand, 3))
            print(
                "Deferrable D:",
                [[round(d.energy, 3), d.start, d.end] for d in env["deferables"]],
            )
            # print(f"Published to {SUN_TOPIC} | {str(sun_data)}")
            cost, actions = predict(policy_network, env, tick, history)
            cost_per_day += cost
            MPP = 4

            print("Imp / Exp:", round(actions["import_export"], 3))
            print("Rel / Sto:", round(actions["release_store"], 3))
            print("Allocations:", [round(a, 3) for a in actions["allocations"]])
            print("Buy price:", round(tick.buy_price, 3))
            print("Sell price:", round(tick.sell_price, 3))
            print("Cost: ", cost)
            print("-" * 20)
            print()

            if tick.tick == 59:
                costs.append(cost_per_day)
                ema_costs = get_ema(costs, 100)
                print("Total cost for day:", cost_per_day)
                print("Average cost per day:", sum(costs) / len(costs))
                print("EMA (100) cost per day:", ema_costs[-1])
                print("-" * 20)
                print()

        if RUN_BROKER:
            client.publish(SUN_TOPIC, json.dumps({"sun": tick.sun}), 0)
            print("Published to broker")

        prev_tick = tick
        sleep(HTTP_PERIOD)


except Exception as e:
    print("Error: ", e)

    if client:
        client.disconnect()
