import sys
from optimisation.algorithm import (
    get_sun_energy,
    load_policy_network_checkpoint,
    predict,
)
from optimisation.gen_data import getDayData, getTickData
from optimisation.models import Day, Tick
import time

filename = "server/optimisation/checkpoints/pn_epochs1000_trajruns_10_ema100.pth"
policy_network = load_policy_network_checkpoint(filename)

# Test prediction
day_id = 5723033
tick_id = 0
day: Day = getDayData(day_id)

env = {
    "flywheel_amt": 0,
    "deferables": day.deferables,
}
history = []
cost_per_day = 0
costs = []


while True:
    time.sleep(0)
    tick = getTickData(day_id, tick_id)
    # cost, actions = predict(policy_network, env, tick, history)

    # overall_cost += cost

    # print("Cost:", cost)
    # print("Overall cost:", overall_cost)
    # print("Imp / Exp:", actions["import_export"])
    # print("Rel / Sto:", actions["release_store"])
    # print("Allocations:", [round(a, 3) for a in actions["allocations"]])
    # print("-" * 20)
    # print()
    # time.sleep(2)
    print("Day:", tick.day, "Tick:", tick.tick)
    print("Sun energy:", round(get_sun_energy(tick, 4), 3))
    print("Flywheel Amt:", round(env["flywheel_amt"], 3))
    print("Inst D:", round(tick.demand, 3))
    print(
        "Deferrable D:",
        [[round(d.energy, 3), d.start, d.end] for d in day.deferables],
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

    if tick_id == 59:
        tick_id = 0
        day_id += 1
        day = getDayData(day_id)
        env["deferables"] = day.deferables
        costs.append(cost_per_day)
        break
    else:
        tick_id += 1
