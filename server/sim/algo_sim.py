from models import AlgoDecn
from random import random

def gen_algo_data(day, tick):
    return AlgoDecn(
        day=day,
        tick=tick,
        energy_import=int(random()*50),
        energy_store=int(random()*50),
        deferables_supplied=[int(random()*50) for i in range(3)],
        cost=int(random()*100)
    )