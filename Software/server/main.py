import requests
from time import sleep

import asyncio
from db.mongo_client import DBClient
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
from external.parallel_get import get_day_and_tick
from external.sync import sync_with_server
from utils import print_preaction, print_postaction

mqtt_client: MClient | None = None

# reduce this time if internet is slow
WAIT = 4.5


# ALGORITHM SETUP
filename = (
    "server/optimisation/checkpoints/06_e5000_r50_am2_rm0_im10_sta20_abs1_tre1.pth"
)
policy_network, min, min_epoch = load_policy_network_checkpoint(filename)

env = {"flywheel_amt": 0, "deferables": None, "history": []}
history = []
daily_costs = []
overall_cost = 0

# CONTROL VARIABLES
RUN_BROKER = True
RUN_ALGO = True
DB_LOG = False

setpoint = 0.3
prev_tick = None
prev_day = None


if __name__ == "__main__":
    if DB_LOG:
        db_client = DBClient()

    if RUN_BROKER:
        mqtt_client = MClient()

    # Sync with external server
    _, tick = get_day_and_tick(TICK_LENGTH)
    day, tick = sync_with_server(tick.tick, TICK_LENGTH)

    while True:
        # this is the start of the next tick
        start = time.time()

        if not env["deferables"] or tick.tick == 0:
            # print("New day")
            env["deferables"] = day.deferables
            print(f"Cost for day: {tick.day - 1}: {sum(daily_costs)}")

        # part that runs the start of every new tick
        if RUN_ALGO:
            print_preaction(tick, env)
            cost, actions = predict(policy_network, env, tick, history)
            daily_costs.append(cost)
            print_postaction(actions, tick, cost)

            # if tick.tick == 59:
            #     costs.append(cost_per_day)
            #     ema_costs = get_ema(costs, 100)
            #     print("Total cost for day:", cost_per_day)
            #     print("Average cost per day:", sum(costs) / len(costs))
            #     print("EMA (100) cost per day:", ema_costs[-1])
            #     print("-" * 20)
            #     print()

        # add data to the database for each new day and algorithms decsions
        if DB_LOG:

            # only write the previous tick data
            if prev_tick != None:
                tick_outcomes = mqtt_client.get_outcome_model(tick.day, tick.tick)
                # TODO: get data for algo decisions

                if tick_outcomes != None:
                    db_client.insert_tick_outcomes(tick_outcomes)
                    db_client.insert_tick(prev_tick)

                    # db_client.insert_algo_decision()
                else:
                    print("could not write to database, tickoutcomes is empty")
            
            # write data for a new day
            if prev_tick != None and prev_tick.tick == 0:
                db_client.insert_day(prev_day)
            elif prev_day == None:
                db_client.insert_day(day)

            # reset the data stored from previous tick
            db_client.reset_db_data()

        prev_tick = tick
        prev_day = day

        # Finds the exact start of the next tick
        delay = time.time() - start
        sleep(WAIT - delay)
        day, tick = sync_with_server(tick.tick, TICK_LENGTH)


# if RUN_BROKER:
#     # send data to correct circuit component here
#     # mqtt_client.send_sun_data(tick.sun)
#     # mqtt_client.send_storage_smps(algo_sim.energy_store)
#     # mqtt_client.send_ext_grid_smps(algo_sim.energy_import)
#     mqtt_client.send_load(1, setpoint)
#     print("Published to broker")
#     print(list(mqtt_client.db_data.values()))
