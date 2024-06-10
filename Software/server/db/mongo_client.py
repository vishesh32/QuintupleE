from pymongo import MongoClient


class DBClient:

    def __init__(self):
        self.client = MongoClient(
            "mongodb+srv://smartgrid_user:OzVu9hnKiaJULToP@autodocs.kwrryjv.mongodb.net/?retryWrites=true&w=majority&appName=Autodocs"
        )
        db = self.client["smartgrid"]
        self.day_db = db["days"]
        self.tick_db = db["ticks"]
        self.comp_db = db["component-states"]
        self.algo_decs = db["algo-decisions"]

    def insert_day(self, day):
        self.day_db.insert_one(day.model_dump())

    def insert_tick(self, tick):
        self.tick_db.insert_one(tick.model_dump())

    def insert_component_states(self, day, tick, comp_vals):
        self.comp_db.insert_many(
            [
                {"day": day.day, "tick": tick.tick, **val.model_dump()}
                for val in comp_vals
            ]
        )
