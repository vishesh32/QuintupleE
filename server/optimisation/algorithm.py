import time

import numpy as np

# from gen_data import getTicksForDay
from optimisation.models import Tick
from optimisation.policy import PolicyNetwork, ValueNetwork

from optimisation.price_lstm import init_price_lstm
from optimisation.utils import import_export_to_cost
import torch
from torch import nn, optim
import matplotlib.pyplot as plt
from copy import deepcopy

MAX_DEFERABLES = 3
MPP = 4

GAMMA = 0.99
STACKED_NUM = 15
MAX_FLYWHEEL_CAPACITY = 50
MAX_IMPORT_EXPORT = 100


ACTION_SIZE = (
    1 + 1 + MAX_DEFERABLES
)  # 1 for buy/sell, 1 for store/release, 1 for each deferable

# Penalties
EXCEED_FLYWHEEL_PENALTY = 0
NEGATIVE_ALLOCATION_PENALTY = 0
OVER_ALLOCATION_PENALTY = 0
NEGATIVE_ENERGY_PENALTY = 0
DEFERABLE_DEADLINE_PENALTY = 0

# Allocation
ALLOCATION_BIAS = 0
ALLOCATION_ABSOLUTE = 1
ALLOCATION_MULTIPLIER = 1
TICK_LENGTH = 5
SUN_TICK_LENGTH = 5

# HYPERPARAMETERS
FUTURE_TICKS = 0

HISTORY_TICK_SIZE = 1
STATE_SIZE = (
    MAX_DEFERABLES * 3 + 1 + 5 + STACKED_NUM * HISTORY_TICK_SIZE + FUTURE_TICKS
)  # 1 for flywheel_amt, 5 for cur tick info, 3 for each past tick, 1 for each future price


# Try 1 past price and 1 future price?
price_lstm = init_price_lstm()


def cur_tick_to_vect(tick):
    return [tick.tick, tick.demand, tick.sun, tick.buy_price, tick.sell_price]


def hist_tick_to_vect(tick):
    # return [tick.sun, tick.buy_price, tick.sell_price]
    return [tick.sell_price]


def history_ticks_to_vect(history, STACKED_NUM):
    hist = []
    for i in range(STACKED_NUM):
        index = -1 - i
        if index < -len(history) or history[index] is None:
            hist.extend([0, 0, 0])
        else:
            hist.extend(hist_tick_to_vect(history[index]))
    return hist


def get_sun_energy(tick):
    return (tick.sun / 100) * MPP * SUN_TICK_LENGTH


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


def update_deferable_demands(day_state, action, tick, print_info=False):
    deferables = day_state["deferables"]
    energy_spent = 0
    penalty = 0

    allocations = []
    for i in range(len(deferables)):
        d = deferables[i]
        if d.start > tick.tick:
            allocations.append(0)
            continue

        allocation = (ALLOCATION_BIAS + action[i + 2].item()) * ALLOCATION_MULTIPLIER
        if ALLOCATION_ABSOLUTE == 1:
            allocation = abs(allocation)

        if d.end == tick.tick and d.energy > 0:
            # if d.energy > 10:
            #     penalty += d.energy * DEFERABLE_DEADLINE_PENALTY
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
            d.energy = 0
            penalty += (allocation - d.energy) * OVER_ALLOCATION_PENALTY
        else:
            energy_spent += allocation
            allocations.append(allocation)
            d.energy -= allocation

    return energy_spent, penalty, allocations


# LATEST
def environment_step(action, tick, day_state, print_info=False):
    total_penalty = 0

    # 1. Get total sun energy
    sun_energy = get_sun_energy(tick)
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

    if imp_exp_amt > MAX_IMPORT_EXPORT:
        imp_exp_amt = MAX_IMPORT_EXPORT
    elif imp_exp_amt < -MAX_IMPORT_EXPORT:
        imp_exp_amt = -MAX_IMPORT_EXPORT

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

    cost = import_export_to_cost(imp_exp_amt, tick)

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


def load_policy_network_checkpoint(filename):
    checkpoint = torch.load(filename)
    policy_network = PolicyNetwork(STATE_SIZE, ACTION_SIZE)
    policy_network.mean_net.load_state_dict(checkpoint["mean_net"])
    policy_network.logstd = checkpoint["logstd"]
    return policy_network, checkpoint["min"], checkpoint["min_index"]


def compute_returns(rewards, gamma=0.99):
    # rewards = (
    #     torch.tensor(rewards, dtype=torch.float32)
    #     if isinstance(rewards, torch.tensor)
    #     else rewards
    # )
    # rewards = rewards - rewards.mean()

    returns = []
    R = 0

    for r in reversed(rewards):
        R = r + gamma * R
        returns.insert(0, R)

    returns = torch.tensor(returns, dtype=torch.float32)
    mean = returns.mean()
    std = returns.std()

    returns = (returns - mean) / (std + 1e-8)  # Normalize returns

    return returns


def compute_loss(log_probs, returns):
    # returns = torch.tensor(returns)
    returns = (
        torch.tensor(returns) if not isinstance(returns, torch.Tensor) else returns
    )

    loss = 0
    for log_prob, G in zip(log_probs, returns):
        loss += -log_prob * G
    return loss
