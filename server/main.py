import requests
from time import sleep
from parallel_get import parallel_get

import asyncio
from optimisation.algorithm import (
    TICK_LENGTH,
    get_sun_energy,
    load_policy_network_checkpoint,
    predict,
)
from optimisation.utils.gen_utils import get_ema
from optimisation.gen_data import getDayData, getTickData
from optimisation.models import Day, Tick
import time

from pymongo import MongoClient
from mqtt_client import MClient
from sim.algo_sim import gen_algo_data

mqtt_client: MClient | None = None
# tick = -1

# SUN_TOPIC = "external/sun"
HTTP_PERIOD = 1


filename = "server/optimisation/checkpoints/pn_epochs1500_trajruns_10_ema100.pth"
# policy_network = load_policy_network_checkpoint(filename)

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
DB_LOG = True


def get_day_and_tick():
    # TODO: add checks to make sure this does not take longer than 5s
    sun_data, price_data, demand_data, deferables_data = asyncio.run(
        parallel_get(
            "https://icelec50015.azurewebsites.net/",
            ["/sun", "/price", "/demand", "/deferables"],
        )
    )

    day = Day.model_validate({"day": price_data["day"], "deferables": deferables_data})

    tick = Tick.model_validate(
        {
            "tick": price_data["tick"] * TICK_LENGTH,
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
# try:
if DB_LOG:
    mongo_client = MongoClient(
        "mongodb+srv://smartgrid_user:OzVu9hnKiaJULToP@autodocs.kwrryjv.mongodb.net/?retryWrites=true&w=majority&appName=Autodocs"
    )
    db = mongo_client["smartgrid"]
    day_db = db["days-live"]
    tick_db = db["ticks-live"]
    comp_db = db["component-states"]
    algo_decs = db["algo-decisions"]

if RUN_BROKER:
    mqtt_client = MClient()

while True:
    day, tick = get_day_and_tick()

    if prev_tick and prev_tick.tick == tick.tick and prev_tick.day == tick.day:
        continue

    if prev_tick and prev_tick.tick == 59:
        env["deferables"] = day.deferables

    # TESTING ONLY
    # TODO: Remove this after testing
    algo_sim = gen_algo_data(day.day, tick.tick)

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

    # if RUN_BROKER:
    #     # send data to correct circuit component here
    #     mqtt_client.send_sun_data(tick.sun)
    #     mqtt_client.send_storage_smps(algo_sim.energy_store)
    #     mqtt_client.send_ext_grid_smps(algo_sim.energy_import)
    #     print("Published to broker")
    #     print(list(mqtt_client.db_data.values()))

    comp_vals = list(mqtt_client.db_data.values())

    # add data to the database for each new day and algorithms decsions
    if DB_LOG and len(comp_vals) > 0:
        if prev_tick == None or tick.day != prev_tick.day:
            day_db.insert_one(day.model_dump())

        tick_db.insert_one(tick.model_dump())
        comp_db.insert_many(
            [
                {"day": day.day, "tick": tick.tick, **val.model_dump()}
                for val in comp_vals
            ]
        )

        # write the algorithms decisions to the db
        # TESTING ONLY
        # generate random data to store
        algo_decs.insert_one(algo_sim.model_dump())

        print("Written to db")

    prev_tick = tick
    sleep(HTTP_PERIOD)


# except Exception as e:
#     print("Error: ", e)

#     if mqtt_client:
#         mqtt_client.end()
