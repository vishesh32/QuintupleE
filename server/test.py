import sys
from optimisation.algorithm import load_policy_network_checkpoint, predict
from optimisation.gen_data import getDayData, getTickData
from optimisation.models import Day, Tick
import time

filename = "server/optimisation/checkpoints/pn_epochs1000_trajruns_10_ema100.pth"
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

print(sys.path)
# while True:
#     tick = getTickData(day_id, tick_id)
#     cost, actions = predict(policy_network, env, tick, history)

#     overall_cost += cost

#     print("Cost:", cost)
#     print("Overall cost:", overall_cost)
#     print("Imp / Exp:", actions["import_export"])
#     print("Rel / Sto:", actions["release_store"])
#     print("Allocations:", [round(a, 3) for a in actions["allocations"]])
#     print("-" * 20)
#     print()
#     time.sleep(2)

#     if tick_id == 60:
#         tick_id = 0
#         day_id += 1
#         day = getDayData(day_id)
#         env["deferables"] = day.deferables
#         costs_per_day.append(overall_cost)
#     else:
#         tick_id += 1
