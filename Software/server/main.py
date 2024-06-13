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
from mqtt_client import MClient, Device
from external.parallel_get import get_day_and_tick
from external.sync import sync_with_server
from utils import print_preaction, print_postaction
from models import AlgoDecisions

mqtt_client: MClient | None = None

# reduce this time if internet is slow
WAIT = 4.5


# ALGORITHM SETUP
filename = (
    "optimisation/checkpoints/06_e5000_r50_am2_rm0_im10_sta20_abs1_tre1.pth"
)
policy_network, min, min_epoch = load_policy_network_checkpoint(filename)

env = {"flywheel_amt": 0, "deferables": None, "history": []}
history = []
daily_costs = []
overall_cost = 0

# CONTROL VARIABLES
RUN_BROKER = True
RUN_ALGO = True
DB_LOG = True

setpoint = 0.3
prev_tick = None
prev_day = None
prev_actions = None


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
            actions["import_export"] = actions["import_export"] * 0.1 * 0.2
            actions["release_store"] = actions["release_store"] * 0.1 * 0.2
            actions["allocations"] = [a * 0.1 * 0.2 for a in actions["allocations"]]

            print(f"\n\n\nsending this to storage {actions['release_store']}\n\n\n")

            daily_costs.append(cost)
            # print_postaction(actions, tick, cost)

            # if tick.tick == 59:
            #     costs.append(cost_per_day)
            #     ema_costs = get_ema(costs, 100)
            #     print("Total cost for day:", cost_per_day)
            #     print("Average cost per day:", sum(costs) / len(costs))
            #     print("EMA (100) cost per day:", ema_costs[-1])
            #     print("-" * 20)
            #     print()

        # send data to picos
        if RUN_BROKER and mqtt_client != None and mqtt_client.manual == False:
            # divide by to convert to power
            mqtt_client.send_storage_power(-1*actions["release_store"]/5)

            # sending the irradiance
            mqtt_client.send_sun_data(tick.sun)

            # Red is instant deferrable
            mqtt_client.send_load_power(Device.LOADR, tick.demand/4)

            # 3 extra defferables are grey, yellow, blue
            mqtt_client.send_load_power(Device.LOADB, actions["allocations"][0])
            mqtt_client.send_load_power(Device.LOADK, actions["allocations"][1])
            mqtt_client.send_load_power(Device.LOADY, actions["allocations"][2])

        # add data to the database for each new day and algorithms decsions
        if DB_LOG and mqtt_client.manual == False:

            # only write the previous tick data
            if prev_tick != None:
                full_tick = mqtt_client.get_full_tick(prev_tick, prev_actions["import_export"], prev_actions["release_store"], prev_actions["allocations"])
                # calc cost
                avg_import = mqtt_client._get_avg(mqtt_client.db_data["import_power"])
                avg_export = mqtt_client._get_avg(mqtt_client.db_data["export_power"])
                cost = avg_import*5*tick.sell_price + avg_export * avg_export*5*tick.buy_price

                # change cost in tick_outcomes
                full_tick.cost = cost

                if full_tick != None:
                    db_client.insert_tick(full_tick)
                else:
                    print("could not write to database, full_tick is empty")
            
            # write data for a new day
            if prev_tick != None and prev_tick.tick == 0:
                db_client.insert_day(prev_day)
            elif prev_day == None:
                db_client.insert_day(day)

            # reset the data stored from previous tick
            mqtt_client.reset_db_data()

        prev_tick = tick
        prev_day = day
        prev_actions = actions

        # Finds the exact start of the next tick
        delay = time.time() - start
        sleep(WAIT - delay)
        day, tick = sync_with_server(tick.tick, TICK_LENGTH)
