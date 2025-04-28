import copy
import json
import logging
import os
from app.core.realpage.parsers.split_markets import split_pdf_by_submarkets
from app.core.realpage.parsers.extract_historical_data import extract_historical_data
from app.core.realpage.parsers.extract_zip_codes import extract_zip_codes

from app.infrastructure.adapters.gpt_adapter import GPTAdapter
from app.infrastructure.frameworks.openai.assistants.realpage_assistant import RealpageAssistant
from app.repositories.realpage_repository import RealpageRepository
from app.schemas.realpage_schema import MarketSnapshot, SubmarketList, ZipcodeList, SubmarketSnapshot, SubmarketReport
from app.utils.file_manager import FileManager
from app.utils.json import get_json_from_text, validate_json, repair_json, json_use_func, sanitize_json
from app.utils.schema_validator import object_validator, list_validator


def history_validator(schema, json_object):
    schema = {
        "market_parameter", "period", "total", "eff", "1br", "2br", "3br", "2000", "1990", "1980", "1970",
        "pre-1970", "low-rise", "mid-rise", "high-rise", "quarter", "year", "state", "market", "submarket"
    }
    for entry in json_object:
        for field in schema:
            if field not in entry:
                return False
    return json_object


class RealpageService:
    def __init__(self):
        self.adapter = None
        self.file_manager = None
        self.repository = None
        self.file = None
        self.submarkets_directory = None

    def find_in_file(self, file, request_message):
        """
        Find data in Realpage Test file with Open AI Assistant.
        This method is used to test the functionality of searching for information in a file.
        """
        self.adapter = GPTAdapter()
        self.file = file

        assistant = RealpageAssistant()
        assistant.upload_file(file)

        self.adapter.use_assistant(
            assistant.assistant
        )

        response_message = self.adapter.send_message(request_message)

        json_str = get_json_from_text(response_message)
        parsed_json = validate_json(json_str)

        if not parsed_json:
            parsed_json = repair_json(json_str)

        self.clear(assistant)

        return {
            "response_message": response_message,
            "json": parsed_json
        }

    def output_directory(self, directory: str):
        self.file_manager = FileManager(directory)

    def read(self, file, submarkets_directory=None):
        if not self.file_manager:
            raise ValueError("Output directory not initialized")

        self.file = file
        self.adapter = GPTAdapter()
        self.submarkets_directory = submarkets_directory

        assistant = RealpageAssistant()
        assistant.upload_file(file)

        self.adapter.use_assistant(
            assistant.assistant
        )

        file_status = self.read_file()
        self.clear(assistant)

        return file_status

    def read_file(self):
        # File Status is used to determine whether the file was processed with errors or without.
        # Files with errors are moved to folder /incomplete after processing.
        file_status = True
        try:
            logging.info('Reading market snapshot')
            market_snapshot = self.read_market_snapshot(MarketSnapshot)
            file_status = file_status and bool(market_snapshot)

            logging.info('Reading submarkets')
            submarkets = self.read_submarkets(SubmarketList)
            market_directory = os.path.join(self.submarkets_directory, market_snapshot['market'])
            print("Reading market: ", market_snapshot['market'], flush=True)

            split_pdf_by_submarkets(submarkets, market_directory, self.file)

            for item in submarkets:
                parse_submarket_status = self.parse_submarket(item, file_status, market_snapshot, market_directory)

                if file_status:
                    file_status = parse_submarket_status

            print("Market: ", market_snapshot['market'], " finished", flush=True)
        except Exception as e:
            print("market parser error: ", e, flush=True)
            file_status = False

        return file_status

    def parse_submarket(self, item, file_status, market_snapshot, market_directory):
        try:
            print("Submarket: ", item['name'], flush=True)
            submarket_path = os.path.join(market_directory, str(item['submarket_key']))
            historical_data = extract_historical_data(submarket_path, item['submarket_key'])

            self.read_zipcodes(submarket_path, item, market_snapshot, ZipcodeList)

            res = self.read_submarket_snapshot(item['name'], SubmarketSnapshot)
            self.read_submarket_report(res, historical_data, SubmarketReport)
            file_status = file_status and bool(res)
        except Exception as e:
            print("Sub market parsing error: ", e, flush=True)
            file_status = False

        return file_status

    def read_market_snapshot(self, schema, save_json=True):
        request_message = f"Find in the document Executive Summary Snapshot and return it as JSON: {schema.get_schema()}. For 'market_text' please use summarized text titleled 'Overview' in the Executive Summary. Use integer for quarter value. For state value use two letter notation. Remove the state code starting with a comma from the market name."
        res = self.process_request_and_save(
            request_message,
            filename='snapshots',
            schema=schema,
            validator=object_validator,
            save_json=save_json
        )
        return res

    def read_submarkets(self, schema, save_json=True):
        request_message = f"Find all the submarket names in the document with their corresponding submarket keys and return them as a list in JSON format: {schema.get_schema()}"

        submarkets = self.process_request_and_save(
            request_message,
            filename='submarkets',
            schema=schema,
            validator=list_validator,
            save_json=save_json
        )

        return submarkets

    def read_zipcodes(self, submarket_path, item, market_snapshot, schema):

        res = self.parse_and_save(
            function_name=extract_zip_codes,
            args_dict={"path": submarket_path, "submarket": item, "market": market_snapshot},
            filename="zipcodes",
            directory=item['name'],
            schema=schema,
            validator=list_validator
        )
        return res

    def read_submarket_snapshot(self, submarket, schema):
        request_message = (f"Find in the document Submarket Overview Snapshot for '{submarket}' without METRO and "
                           f"return it as JSON: {schema.get_schema()}. Use integer for quarter value. For state value use two letter notation. Remove the state code starting with a comma from the market name.")

        res = self.process_request_and_save(
            request_message,
            filename="snapshots",
            directory=submarket,
            schema=schema,
            validator=object_validator
        )
        return res

    def get_values_from_historical_data(self, historical_data):
        last_quarter = max(historical_data['sample_existing_units'],
                           key=lambda x: (int(x[0].split()[1]), x[0].split()[0]))
        total_number_of_properties = last_quarter[1]

        last_quarter = max(historical_data['monthly_rent'],
                           key=lambda x: (int(x[0].split()[1]), x[0].split()[0]))
        one_bedroom_apartment = last_quarter[3]
        two_bedroom_apartment = last_quarter[4]
        three_bedroom_apartment = last_quarter[5]
        return total_number_of_properties, one_bedroom_apartment, two_bedroom_apartment, three_bedroom_apartment

    def read_submarket_report(self, submarket, historical_data, schema):
        print("Reading submarket report ==========================", flush=True)
        total_number_of_properties, one_bedroom_apartment, two_bedroom_apartment, three_bedroom_apartment = self.get_values_from_historical_data(
            historical_data)

        report = {
            'quarter': submarket['quarter'],
            'year': submarket['year'],
            'state': submarket['state'],
            'market': submarket['market'],
            'submarket': submarket['submarket'],
            'average_rental_rate': submarket['rent']['monthly_rent'],

            'annual_rent_growth': submarket['rent']['annual_change'],

            'current_vacancy': submarket['occupancy']['current_rate'],

            'inventory_of_properties': {
                'total_number_of_properties': total_number_of_properties,
                'breakdown_of_properties': ''
            },
            'average_monthly_rent': {
                'one_bedroom_apartment': one_bedroom_apartment,
                'two_bedroom_apartment': two_bedroom_apartment,
                'three_bedroom_apartment': three_bedroom_apartment
            }
        }
        self.validate_and_save(
            submarket=submarket['submarket'],
            data=report,
            filename="report",
            directory=submarket['submarket'],
            schema=schema,
            validator=object_validator
        )

        self.validate_and_save(
            submarket=submarket['submarket'],
            data=report,
            filename="rp_report",
            directory=submarket['submarket'],
            schema=schema,
            validator=object_validator
        )

    def read_completed_properties(self, submarket, schema):
        request_message = (f"Find in the document Properties Completed in the Last Four Quarters for '{submarket}' and "
                           f"return as list in JSON format: {schema.get_schema()}")

        self.process_request_and_save(
            request_message,
            filename="completed_properties",
            directory=submarket,
            schema=schema,
            validator=list_validator
        )

    def read_properties_under_construction(self, submarket, schema):
        request_message = (f"Find in the document Properties Under Construction for '{submarket}' and return as list "
                           f"in JSON format: {schema.get_schema()}")

        self.process_request_and_save(
            request_message,
            filename="properties_under_construction",
            directory=submarket,
            schema=schema,
            validator=list_validator
        )

    def read_historical_data(self, submarket, parameter, schema):
        request_message = (f"Find in the attached document table labeled as HISTORICAL DATA: '{submarket}'. There is a "
                           f"Market Parameter in the first column and 9 rows of period data for each Market "
                           f"Parameter. Please extract data for the '{parameter}' Market Parameter in relevant 9 rows "
                           f"and return it as a list of 9 objects in JSON format: {schema.get_schema()}")

        self.process_request_and_save(
            request_message,
            filename=f"historical-{parameter}",
            directory=submarket,
            schema=schema,
            validator=history_validator
        )

    def read_supply_demand(self, submarket, schema):
        request_message = (f"Find in the document table 'Supply/Demand' for submarket '{submarket}', extract data and "
                           f"return it as a list of 9 elements, one for each period in JSON format: {schema.get_schema()}")

        self.process_request_and_save(
            request_message,
            filename="supply_demands",
            directory=submarket,
            schema=schema,
            validator=list_validator
        )

    def read_sample_existing_units(self, submarket, schema):
        request_message = (f"Find 'Sample/Existing Units' data for the submarket '{submarket}' in the document for the "
                           f"last 9 periods and return it as a list in JSON format: {schema.get_schema()}")

        self.process_request_and_save(
            request_message,
            filename="sample_existing_units",
            directory=submarket,
            schema=schema,
            validator=list_validator
        )

    def validate_and_save(self, submarket, data, filename, directory=None, schema=None, validator=None):
        print("File name: ", filename, flush=True)
        print("Directory: ", directory, flush=True)
        content = self.file_manager.file_exists(
            filename, directory
        )

        if content:
            print(f"Submarket: {submarket} {filename} already exists", flush=True)
            return content

        if data:
            data = validator(schema, data)
        print(f"Submarket: {submarket} {filename} validated", flush=True)
        self.save_to_repository(
            data,
            filename
        )

        self.file_manager.save_json(
            data, filename, directory
        )
        print(f"Submarket: {submarket} {filename} saved", flush=True)

        return data

    def parse_and_save(self, function_name, args_dict, filename, directory=None, schema=None, validator=None,
                       save_json=True):
        print(f"function_name: {function_name} started", flush=True)

        content = self.file_manager.file_exists(
            filename, directory
        )
        if content:
            logging.info('Already parsed')
            return content

        response = function_name(**args_dict)

        parsed_json = {}

        # validating json schema
        if response:
            parsed_json = validator(schema, response)

        if not save_json:
            return parsed_json

        self.save_to_repository(
            parsed_json,
            filename
        )

        self.file_manager.save_json(
            parsed_json, filename, directory
        )
        print(f"function_name: {function_name} finished", flush=True)

        return parsed_json

    def process_request_and_save(self, request_message, filename, directory=None, schema=None, validator=None,
                                 save_json=True):
        content = self.file_manager.file_exists(
            filename, directory
        )
        if content:
            logging.info('Already parsed')
            return content

        logging.info(f"Request: {request_message}")

        response_message = self.adapter.send_message(request_message)
        logging.info(f"Response: {response_message}")

        json_str = get_json_from_text(response_message)
        if not json_str:
            logging.warning(response_message)
            return False

        # validating json structure
        parsed_json = validate_json(json_str)

        # trying to repair json structure
        if not parsed_json:
            parsed_json = repair_json(json_str)

        # validating json schema
        if parsed_json:
            logging.info(f"data to validate: {parsed_json}")
            parsed_json = validator(schema, parsed_json)

        if not save_json:
            return parsed_json

        if parsed_json:
            self.save_to_repository(
                parsed_json,
                filename
            )

            self.file_manager.save_json(
                parsed_json, filename, directory
            )
        else:
            self.file_manager.save_text(
                json_str, filename, directory
            )

        return parsed_json

    def save_to_repository(self, json_data, collection):
        data = copy.deepcopy(json_data)

        if isinstance(data, str):
            data = json.loads(data)

        cleared_data = json_use_func(
            data,
            sanitize_json
        )

        if not self.repository:
            self.repository = RealpageRepository()

        self.repository.save_data_to_collection(
            cleared_data, collection
        )

    def clear(self, assistant):
        assistant.clear()
        logging.info('... assistant cleared')
        self.adapter.clear()
        logging.info('... adapter cleared')
