from copy import deepcopy

from optimisation.algorithm import MAX_FLYWHEEL_CAPACITY, get_sun_energy


def simulate_day_naive(
    day, ticks, satisfy_end=True, use_flywheel=False, export_extra=False
):
    costs = []
    flywheel_amt = 0
    day = deepcopy(day)

    for tick in ticks:
        sun_energy = get_sun_energy(tick)
        total_energy = sun_energy

        if use_flywheel:
            total_energy += flywheel_amt
            flywheel_amt = 0

        total_energy -= tick.demand

        for deferable in day.deferables:
            match = deferable.end if satisfy_end else deferable.start
            if match == tick.tick:
                total_energy -= deferable.energy

        cost = 0
        if total_energy < 0:
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

    return sum(costs)
