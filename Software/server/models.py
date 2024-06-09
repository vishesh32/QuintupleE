from pydantic import BaseModel
from typing import List
from optimisation.models import *

class SMPS(BaseModel):
	SMPS: str
	power_in: int
	power_out: int

class AlgoDecn(BaseModel):
	day: int
	tick: int
	energy_import: int
	energy_store: int
	deferables_supplied: List[int]
	cost: int