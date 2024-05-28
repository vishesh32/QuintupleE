import time

import numpy as np

# from gen_data import getTicksForDay
from optimisation.models import Tick
from optimisation.policy import PolicyNetwork, ValueNetwork

import torch
from torch import nn, optim
import matplotlib.pyplot as plt
from copy import deepcopy

MAX_DEFERABLES = 3
MPP = 4
TICK_LENGTH = 300 / 60
GAMMA = 0.99
STACKED_NUM = 10
MAX_FLYWHEEL_CAPACITY = 50
MAX_IMPORT_EXPORT = 100

STATE_SIZE = (
    MAX_DEFERABLES * 3 + 1 + 5 + STACKED_NUM * 3
)  # 1 for flywheel_amt, 5 for cur tick info, 3 for each past tick
ACTION_SIZE = (
    1 + 1 + MAX_DEFERABLES
)  # 1 for buy/sell, 1 for store/release, 1 for each deferable

# Penalties
EXCEED_FLYWHEEL_PENALTY = 0
NEGATIVE_ALLOCATION_PENALTY = 0
OVER_ALLOCATION_PENALTY = 0
NEGATIVE_ENERGY_PENALTY = 0


def simulate_day_naive(day, ticks, use_flywheel=False, export_extra=False):
    costs = []
    flywheel_amt = 0
    for tick in ticks:
        power = (tick.sun / 100) * MPP
        sun_energy = power * TICK_LENGTH  # sun in percentage to joules per tick

        total_energy = sun_energy

        if use_flywheel:
            total_energy += flywheel_amt
            flywheel_amt = 0

        total_energy -= tick.demand

        for deferable in day.deferables:
            if deferable.start == tick.tick:
                total_energy -= deferable.energy

        if total_energy < 0:
            cost = -total_energy * tick.sell_price
        elif use_flywheel:
            flywheel_amt = min(MAX_FLYWHEEL_CAPACITY, flywheel_amt + total_energy)
        elif export_extra:
            cost = total_energy * tick.buy_price  # Export extra energy

        costs.append(cost)

    return sum(costs)


def tick_to_history(i, ticks, yest_ticks, STACKED_NUM):
    tick: Tick = ticks[i]
    cur = [tick.tick, tick.demand, tick.sun, tick.buy_price, tick.sell_price]
    for j in range(1, STACKED_NUM + 1):
        if i - j < 0 and abs(i - j) <= len(yest_ticks):
            prev = yest_ticks[i - j]
            cur.extend(tick_to_vect(prev))
            # cur.extend([0, 0, 0])
        elif i - j >= 0:
            prev = ticks[i - j]
            cur.extend(tick_to_vect(prev))
        else:
            cur.extend([0, 0, 0])

    return cur


def cur_tick_to_vect(tick):
    return [tick.tick, tick.demand, tick.sun, tick.buy_price, tick.sell_price]


# PENALTIES IN ACTION: Flywheel store/release invalid, Negative/over allocation


def get_sun_energy(tick, MPP):
    return (tick.sun / 100) * MPP * TICK_LENGTH


def buy_sell_to_cost(imp_exp_amt, tick):
    if imp_exp_amt < 0:
        return imp_exp_amt * tick.buy_price
    else:
        return imp_exp_amt * tick.sell_price


def update_flywheel_amt(day_state, release_store_amt):
    cur_flywheel_amt = day_state["flywheel_amt"]
    penalty = 0

    # If release amount > flywheel amount, set release amount to flywheel amount and penalise
    if release_store_amt > cur_flywheel_amt:
        penalty += (release_store_amt - cur_flywheel_amt) * EXCEED_FLYWHEEL_PENALTY
        release_store_amt = cur_flywheel_amt

    # Else if store amount + cur_flywheel_amt > capacity, set release_store_amt to capacity - cur_flywheel_amt and penalise
    elif (
        release_store_amt < 0
        and -release_store_amt + cur_flywheel_amt > MAX_FLYWHEEL_CAPACITY
    ):
        penalty += (
            -release_store_amt + cur_flywheel_amt - MAX_FLYWHEEL_CAPACITY
        ) * EXCEED_FLYWHEEL_PENALTY
        release_store_amt = MAX_FLYWHEEL_CAPACITY - cur_flywheel_amt

    # If release_store > 0, draw energy and subtract from flywheel_amt
    day_state["flywheel_amt"] -= release_store_amt

    return release_store_amt, penalty


# def check_deferable_demands(day_state, tick):
#     # Check total deferable demands
#     total_energy_next_tick = 0
#     for d in day_state["deferables"]:


# Problem: Deferable demands not being satisfied in time, too much energy needed at the end of the day
def update_deferable_demands(day_state, action, tick):
    deferables = day_state["deferables"]
    energy_spent = 0
    penalty = 0

    allocations = []
    for i in range(len(deferables)):
        d = deferables[i]
        if d.start > tick.tick:
            allocations.append(0)
            continue

        allocation = action[i + 2].item()
        # print(f"D{i}:", round(d.energy, 3), "A:", round(allocation, 3))
        if d.end == tick.tick and d.energy > 0:
            print("Deferable demand not satisfied:", d.energy, d.start, d.end)
            energy_spent += d.energy
            allocations.append(d.energy)
            d.energy = 0

        elif allocation < 0:
            penalty += -allocation * NEGATIVE_ALLOCATION_PENALTY
            allocations.append(0)
            continue

        elif allocation > d.energy:
            energy_spent += d.energy
            allocations.append(d.energy)
            penalty += (allocation - d.energy) * OVER_ALLOCATION_PENALTY

        else:
            energy_spent += allocation
            allocations.append(allocation)
            d.energy -= allocation

    return energy_spent, penalty, allocations


def run_simulation(ticks, yest_ticks, day, print_info=False):

    day_state = {"deferables": deepcopy(day.deferables), "flywheel_amt": 0}

    # print("Deferables: ", [[d.start, d.end] for d in day_state["deferables"]])

    log_probs = []
    rewards = []
    states = []

    total_penalty = 0
    total_cost = 0
    costs = []
    penalties = []
    for i, tick in enumerate(ticks):
        state = []

        # Add deferable demand info
        deferables = day_state["deferables"]
        for j in range(len(deferables)):
            d = deferables[j]
            state.extend([d.energy, d.start, d.end])

        # Add store/release info
        state.append(day_state["flywheel_amt"])

        # Add history
        state.extend(tick_to_history(i, ticks, yest_ticks, STACKED_NUM))

        # Run policy network
        action, log_prob = policy_network.get_action(torch.tensor(state))
        log_probs.append(log_prob)

        # Environment step
        cost, penalty = environment_step(action, tick, day_state, print_info=print_info)
        # total_penalty += penalty
        penalties.append(penalty)
        costs.append(cost)
        rewards.append(-(cost + penalty))
        states.append(state)

    return log_probs, rewards, costs, penalties, states


# LATEST
def environment_step(action, tick, day_state, print_info=False):
    total_penalty = 0

    # 1. Get total sun energy
    sun_energy = get_sun_energy(tick, MPP)
    total_energy = sun_energy

    # 2. Get energy bought/sold
    imp_exp_amt = action[0].item()
    total_energy += imp_exp_amt

    # 3. Get energy stored/released
    release_store_amt = action[1].item()
    release_store_amt, penalty = update_flywheel_amt(day_state, release_store_amt)
    total_penalty += penalty
    total_energy += release_store_amt

    # 4. Satisfy instantaneous demand
    total_energy -= tick.demand

    # 5. Satisfy deferable demands
    energy_spent, penalty, allocations = update_deferable_demands(
        day_state, action, tick
    )
    total_penalty += penalty
    total_energy -= energy_spent

    # 6. Buy more energy if total energy < 0
    if total_energy < 0:
        imp_exp_amt += -total_energy

    # todo: Limit max import / export amount
    if imp_exp_amt > MAX_IMPORT_EXPORT:
        imp_exp_amt = MAX_IMPORT_EXPORT
    elif imp_exp_amt < -MAX_IMPORT_EXPORT:
        imp_exp_amt = -MAX_IMPORT_EXPORT

    # TODO: Save rest of energy in flywheel
    if total_energy > 0:
        if total_energy > MAX_FLYWHEEL_CAPACITY - day_state["flywheel_amt"]:
            energy_to_sell = total_energy - (
                MAX_FLYWHEEL_CAPACITY - day_state["flywheel_amt"]
            )
            imp_exp_amt -= energy_to_sell

        release_store_amt -= min(
            MAX_FLYWHEEL_CAPACITY - day_state["flywheel_amt"], total_energy
        )
        day_state["flywheel_amt"] = min(
            MAX_FLYWHEEL_CAPACITY, day_state["flywheel_amt"] + total_energy
        )

    # TODO: OR sell energy
    cost = buy_sell_to_cost(imp_exp_amt, tick)

    if print_info:
        print("Tick: ", tick.tick)
        print("Sun E: ", round(sun_energy, 3))
        print("Imp/Exp: ", round(imp_exp_amt, 3))
        print("Cost: ", round(cost, 5))
        print("Rel/Sto: ", round(release_store_amt, 3))
        print("Ins D: ", round(tick.demand, 3))
        print("Def D: ", round(energy_spent, 3))
        print("E left: ", round(total_energy, 3))
        print("Penalty: ", round(total_penalty, 3))
        print("-" * 20)
        print()

    return (
        cost,
        total_penalty,
        {
            "import_export": imp_exp_amt,
            "release_store": release_store_amt,
            "allocations": allocations,
        },
    )


def hist_tick_to_vect(tick):
    return [tick.sun, tick.buy_price, tick.sell_price]


def history_ticks_to_vect(history, STACKED_NUM):
    hist = []
    for i in range(STACKED_NUM):
        index = -1 - i
        if index < -len(history):
            hist.extend([0, 0, 0])
        else:
            hist.extend(hist_tick_to_vect(history[index]))
    return hist


def predict(policy_network, env, tick, history):

    # Add deferable demand info
    deferables = env["deferables"]
    state = []
    for j in range(len(deferables)):
        d = deferables[j]
        state.extend([d.energy, d.start, d.end])

    # Add store/release info
    state.append(env["flywheel_amt"])

    # Add cur tick
    state.extend(cur_tick_to_vect(tick))

    # Add history
    state.extend(history_ticks_to_vect(history, STACKED_NUM))

    # Run policy network
    action, log_prob = policy_network.get_action(torch.tensor(state))

    cost, penalty, actions = environment_step(action, tick, env, print_info=False)

    return cost, actions
    # Environment step
    # total_penalty += penalty
    # penalties.append(penalty)
    # costs.append(cost)
    # rewards.append(-(cost + penalty))
    # states.append(state)


def load_policy_network_checkpoint(filename):
    checkpoint = torch.load(filename)
    policy_network = PolicyNetwork(STATE_SIZE, ACTION_SIZE)
    policy_network.mean_net.load_state_dict(checkpoint["mean_net"])
    policy_network.logstd = checkpoint["logstd"]
    return policy_network
