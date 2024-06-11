from pydantic import BaseModel
from typing import List
from optimisation.models import *

class AlgoDecisions(BaseModel):
	day: int
	tick: int
	power_import: float
	power_store: float
	deferables_supplied: List[float]

class TickOutcomes(BaseModel):
	day: int
	tick: int
	cost: float
	avg_pv_energy: float
	storage_soc: float
	avg_import_energy: float
	avg_export_energy: float
	avg_red_energy: float
	avg_blue_energy: float
	avg_yellow_energy: float
	avg_grey_energy: float