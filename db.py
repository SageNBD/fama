from pymongo import MongoClient

class Mongo():

    def __init__(self, assets):
        self.client = MongoClient('localhost', 27017)
        assert('fama' in self.client.list_database_names())

        self.db = self.client.fama
        
        self.asset_collection = {} # Create collection for each asset
        for asset in assets:
            self.asset_collection[asset] = self.db[asset]
