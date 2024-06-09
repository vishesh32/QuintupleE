from pymongo import MongoClient

class DBClient:

    def __init__(self):
        self.client = MongoClient(
            "mongodb+srv://smartgrid_user:OzVu9hnKiaJULToP@autodocs.kwrryjv.mongodb.net/?retryWrites=true&w=majority&appName=Autodocs"
        )
        db = self.client["smartgrid"]
        self.day_db = db["days-live"]
        self.tick_db = db["ticks-live"]
        self.comp_db = db["component-states"]
        self.algo_decs = db["algo-decisions"]
