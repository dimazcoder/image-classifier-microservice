from app.infrastructure.adapters.mongo_adapter import MongoAdapter


class RealpageRepository:
    def __init__(self):
        self.adapter = MongoAdapter(
            database_name='market_data'
        )

    def save_data_to_collection(self, data, collection):
        self.adapter.collection_name = self.map_collection(
            collection
        )
        if self.adapter.collection_name == 'snapshots':
            self.save_snapshot(data)
        elif self.adapter.collection_name == 'zipcodes':
            self.save_zipcodes(data)
        elif self.adapter.collection_name == 'properties':
            self.save_properties(data)
        elif self.adapter.collection_name == 'historical-data':
            self.save_historical_data(data)
        elif self.adapter.collection_name == 'supply_demands':
            self.save_supply_demands(data)
        elif self.adapter.collection_name == 'sample_existing_units':
            self.save_sample_existing_units(data)
        elif self.adapter.collection_name == 'report':
            self.save_report(data)

    def save_report(self, report_data):
        filter_criteria = {}
        self.filter_criteria(
            ['quarter', 'year', 'state', 'market', 'submarket'], report_data, filter_criteria
        )
        self.update_one(
            filter_criteria, report_data
        )

    def save_rp_report(self, report_data):
        filter_criteria = {}
        self.filter_criteria(
            ['quarter', 'year', 'state', 'market', 'submarket'], report_data, filter_criteria
        )
        self.update_one(
            filter_criteria, report_data
        )

    def save_supply_demands(self, supply_demands):
        for obj in supply_demands:
            filter_criteria = {}
            self.filter_criteria(
                ['quarter', 'year', 'state', 'market', 'submarket'], obj, filter_criteria
            )
            self.update_one(
                filter_criteria, obj
            )

    def save_sample_existing_units(self, existing_units):
        for obj in existing_units:
            filter_criteria = {}
            self.filter_criteria(
                ['quarter', 'year', 'state', 'market', 'submarket'], obj, filter_criteria
            )
            self.update_one(
                filter_criteria, obj
            )

    def map_collection(self, collection):
        if collection.startswith('historical-'):
            return 'historical-data'
        elif collection in ['completed_properties', 'properties_under_construction']:
            return 'properties'
        return collection

    def save_properties(self, properties):
        for prop in properties:
            filter_criteria = {}
            self.filter_criteria(
                ['zipcode', 'name'], prop, filter_criteria
            )
            self.update_one(
                filter_criteria, prop
            )

    def save_historical_data(self, historical_data):
        for data in historical_data:
            filter_criteria = {}
            self.filter_criteria(
                ['market_parameter', 'quarter', 'year', 'state', 'market', 'submarket'], data, filter_criteria
            )
            self.update_one(
                filter_criteria, data
            )

    def save_zipcodes(self, zipcodes):
        for zipcode in zipcodes:
            filter_criteria = {}
            self.filter_criteria(
                ['zipcode'], zipcode, filter_criteria
            )
            self.update_one(
                filter_criteria, zipcode
            )

    def save_snapshot(self, snapshot_data):
        filter_criteria = {}
        self.filter_criteria(
            ['quarter', 'year', 'state', 'market', 'submarket'], snapshot_data, filter_criteria
        )
        self.update_one(
            filter_criteria, snapshot_data
        )

    def update_one(self, filter_criteria, data):
        with self.adapter as adapter:
            return adapter.update_one(
                filter_criteria, {'$set': data}, upsert=True
            )

    def filter_criteria(self, keys, data, filter_criteria):
        for key in keys:
            if key in data:
                filter_criteria[key] = data.pop(key)
