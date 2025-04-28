from pydantic import BaseModel
from typing import List, Any

class TestQuery(BaseModel):
    query: str


class Occupancy(BaseModel):
    current_rate: Any
    quarterly_change: Any
    annual_change: Any
    five_year_peak: Any
    five_year_trough: Any
    five_year_average: Any
    five_year_average_annual_change: Any


class Rent(BaseModel):
    monthly_rent: Any
    rent_per_square_foot: Any
    quarterly_change: Any
    annual_change: Any
    five_year_peak_in_annual_change: Any
    five_year_trough_in_annual_change: Any
    five_year_average_annual_change: Any


class OneYearForecast(BaseModel):
    annual_supply: Any
    annual_demand: Any
    occupancy: Any
    annual_occupancy_change: Any
    annual_rent_change: Any
    annual_revenue_change: Any
    annual_job_change: Any


class MarketSnapshot(BaseModel):
    quarter: Any
    year: Any
    state: Any
    market: Any
    market_text: Any
    occupancy: Occupancy
    rent: Rent
    one_year_forecast: OneYearForecast

    @staticmethod
    def get_schema():
        return """
        {
            quarter,
            year,
            state,
            market,
            market_text,
            occupancy {
                current_rate,
                quarterly_change,
                annual_change,
                five_year_peak,
                five_year_trough,
                five_year_average,
                five_year_average_annual_change
            },
            rent {
                monthly_rent,
                rent_per_square_foot,
                quarterly_change,
                annual_change,
                five_year_peak_in_annual_change,
                five_year_trough_in_annual_change,
                five_year_average_annual_change
            },
            one_year_forecast {
                annual_supply,
                annual_demand,
                occupancy,
                annual_occupancy_change,
                annual_rent_change,
                annual_revenue_change,
                annual_job_change
            }
        }        
        """


class Submarket(BaseModel):
    submarket_key: Any
    name: Any


class SubmarketList(BaseModel):
    list: List[Submarket]

    @staticmethod
    def get_schema():
        return "{submarket_key, name}"


class Zipcode(BaseModel):
    zipcode: Any
    state: Any
    market: Any
    submarket: Any


class ZipcodeList(BaseModel):
    list: List[Zipcode]

    @staticmethod
    def get_schema():
        return "{zipcode, state, market, submarket}"

class SubmarketOccupancy(BaseModel):
    current_rate: Any
    quarterly_change: Any
    annual_change: Any
    five_year_peak: Any
    five_year_trough: Any
    five_year_average: Any

class SubmarketRent(BaseModel):
    monthly_rent: Any
    rent_per_square_foot: Any
    quarterly_change: Any
    annual_change: Any
    five_year_peak_in_annual_change: Any
    five_year_trough_in_annual_change: Any
    five_year_average_annual_change: Any


class SubmarketOneYearForecast(BaseModel):
    annual_supply: Any
    annual_demand: Any
    occupancy: Any
    annual_occupancy_change: Any


class SubmarketSnapshot(BaseModel):
    quarter: Any
    year: Any
    state: Any
    market: Any
    submarket: Any
    occupancy: SubmarketOccupancy
    rent: SubmarketRent
    one_year_forecast: SubmarketOneYearForecast

    @staticmethod
    def get_schema():
        return """
        {
            quarter,
            year,
            state,
            market,
            submarket,
            occupancy {
                current_rate,
                quarterly_change,
                annual_change,
                five_year_peak,
                five_year_trough,
                five_year_average
            },
            rent {
                monthly_rent,
                rent_per_square_foot,
                quarterly_change,
                annual_change,
                five_year_peak_in_annual_change,
                five_year_trough_in_annual_change,
                five_year_average_annual_change
            },
            one_year_forecast {
                annual_supply,
                annual_demand,
                occupancy,
                annual_occupancy_change
            }
        }        
        """

class InventoryOfProperties(BaseModel):
    total_number_of_properties: Any
    breakdown_of_properties: Any

    @staticmethod
    def get_schema():
        return """
        {
            total_number_of_properties,
            breakdown_of_properties
        }
        """



class AverageMonthlyRent(BaseModel):
    one_bedroom_apartment: Any
    two_bedroom_apartment: Any
    three_bedroom_apartment: Any


class SubmarketReport(BaseModel):
    quarter: Any
    year: Any
    state: Any
    market: Any
    submarket: Any
    average_rental_rate: Any
    annual_rent_growth: Any
    current_vacancy: Any
    inventory_of_properties: InventoryOfProperties
    average_monthly_rent: AverageMonthlyRent

    @staticmethod
    def get_schema():
        return """
        {
            quarter,
            year,
            state,
            market,
            submarket,        
            average_rental_rate,
            annual_rent_growth,
            current_vacancy,
            inventory_of_properties {
                total_number_of_properties,
                breakdown_of_properties            
            },
            average_monthly_rent {
                one_bedroom_apartment,
                two_bedroom_apartment,
                three_bedroom_apartment            
            }
        """


class SupplyAndDemand(BaseModel):
    quarterly_supply: Any
    annual_supply: Any
    annual_inventory_change: Any
    five_year_average_annual_supply: Any
    five_year_peak_in_annual_supply: Any
    five_year_trough_in_annual_supply: Any
    quarterly_demand: Any
    annual_demand: Any


class RevenueChange(BaseModel):
    quarterly_change: Any
    annual_change: Any
    five_year_peak_in_annual_change: Any
    five_year_trough_in_annual_change: Any
    five_year_average_annual_change: Any


class Supply(BaseModel):
    quarterly_supply: Any
    annual_supply: Any
    annual_demand: Any
    occupancy: Any
    annual_occupancy_change: Any


class Property(BaseModel):
    quarter: Any
    year: Any
    state: Any
    market: Any
    submarket: Any
    zipcode: Any
    name: Any
    address: Any
    developer: Any
    units: Any
    stories: Any
    start: Any
    finish: Any


class PropertyList(BaseModel):
    list: List[Property]

    @staticmethod
    def get_schema():
        return """
        {
            quarter,
            year,
            state,
            market,
            submarket,
            zipcode,
            name,
            address,
            developer,
            units,
            stories,
            start,
            finish
        }
        """


class HistoricalDataList(BaseModel):
    list: List[str]  # dummy field, class used only for getting string repr

    @staticmethod
    def get_schema():
        return """
        {
            market_parameter,
            period,
            total,
            eff,
            1br,
            2br,
            3br,
            2000,
            1990,
            1980,
            1970,
            pre-1970,
            low-rise,
            mid-rise,
            high-rise,
            quarter,
            year,
            state,
            market,
            submarket
        }
        """


class SubmarketSupplyDemand(BaseModel):
    period: Any
    quarter: Any
    year: Any
    state: Any
    market: Any
    submarket: Any
    supply_quarterly: Any
    supply_annual: Any
    demand_quarterly: Any
    demand_annual: Any
    inventory_change_quarterly: Any
    inventory_change_annual: Any


class SubmarketSupplyDemandList(BaseModel):
    list: List[SubmarketSupplyDemand]

    @staticmethod
    def get_schema():
        return """
        {
            period,
            quarter,
            year,
            state,
            market,
            submarket,
            supply_quarterly,
            supply_annual,
            demand_quarterly,
            demand_annual,
            inventory_change_quarterly,
            inventory_change_annual
        }
        """


class SampleExistingUnits(BaseModel):
    quarter: Any
    year: Any
    state: Any
    market: Any
    submarket: Any
    existing_units: Any
    sampled_units: Any
    percent_sampled: Any


class SampleExistingUnitsList(BaseModel):
    list: List[SampleExistingUnits]

    @staticmethod
    def get_schema():
        return """
        {
            quarter,
            year,
            state,
            market,
            submarket,
            existing_units,
            sampled_units,
            percent_sampled
        }
        """
