from pymongo import MongoClient
from models import *

class DBClient:

    def __init__(self):
        self.client = MongoClient(
            "mongodb+srv://smartgrid_user:OzVu9hnKiaJULToP@autodocs.kwrryjv.mongodb.net/?retryWrites=true&w=majority&appName=Autodocs"
        )
        db = self.client["smartgrid"]
        self.day_db = db["days"]
        self.tick_db = db["ticks"]
        self.outcomes_db = db["outcomes"]
        self.algo_decs = db["algo-decisions"]

    def insert_day(self, day: Day):
        self.day_db.insert_one(day.model_dump())

    def insert_tick(self, tick: Tick):
        self.tick_db.insert_one(tick.model_dump())

    def insert_algo_decision(self, algo_decision: AlgoDecisions):
        self.algo_decs.insert_one(algo_decision.model_dump())

    def insert_tick_outcomes(self, tick_outcomes: TickOutcomes):
        self.outcomes_db.insert_one(tick_outcomes.model_dump())
