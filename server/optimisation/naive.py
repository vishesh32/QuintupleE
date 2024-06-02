from copy import deepcopy

from optimisation.algorithm import (
    MAX_FLYWHEEL_CAPACITY,
    MAX_IMPORT_ENERGY,
    get_sun_energy,
    MAX_ALLOCATION_TOTAL,
)
import matplotlib.pyplot as plt
import math

from optimisation.utils.deferables_utils import (
    satisfy_deferables,
    satisfy_deferables_start,
)
from optimisation.utils.gen_utils import cost_to_energy


def simulate_day_naive(
    day,
    ticks,
    satisfy_end=True,
    use_flywheel=False,
    export_extra=False,
    max_alloc_total=MAX_ALLOCATION_TOTAL,
):
    costs = []
    flywheel_amt = 0
    day = deepcopy(day)
    deferables = deepcopy(day.deferables)

    for tick in ticks:
        sun_energy = get_sun_energy(tick)
        total_energy = sun_energy

        if use_flywheel:
            total_energy += flywheel_amt
            flywheel_amt = 0

        total_energy -= tick.demand

        # print("total_energy:", total_energy)
        # print("inst_demand:", tick.demand)
        # print("deferables:", [round(d.energy, 3) for d in deferables])
        if not satisfy_end:
            allocations = satisfy_deferables_start(
                tick, deferables, total_energy, MAX_IMPORT_ENERGY
            )
            total_energy -= sum(allocations)
        else:
            allocations = satisfy_deferables(tick, deferables, max_alloc_total)
            total_energy -= sum(allocations)

        cost = 0

        if total_energy < 0:
            if total_energy < -MAX_IMPORT_ENERGY:
                print("Exceeded max import energy")
            cost = -total_energy * tick.sell_price

        elif use_flywheel:
            if flywheel_amt + total_energy > MAX_FLYWHEEL_CAPACITY:
                cost = (
                    -(flywheel_amt + total_energy - MAX_FLYWHEEL_CAPACITY)
                    * tick.buy_price
                )
            flywheel_amt = min(MAX_FLYWHEEL_CAPACITY, flywheel_amt + total_energy)
        elif export_extra:
            cost = -total_energy * tick.buy_price  # Export extra energy

        costs.append(cost)
        # import_amount = cost_to_energy(cost, tick.buy_price, tick.sell_price)

    return sum(costs)
