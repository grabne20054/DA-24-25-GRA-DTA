from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from DataAnalysis.preprocessing.APIDataHandlerFactory import APIDataHandlerFactory

from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from os import getenv

from dotenv import load_dotenv
load_dotenv()

TYPEOFGRAPH = "line"


class CustomerSignup(DescriptiveAnalysis):
    """ Trend of Customer Growth
    """
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/customers")

    def collect(self) -> list:
        """
        Collects data from the API

        Returns:
            list: List of dictionaries containing the data
        """
        try:
            return self.handler.start()
        except ConnectionRefusedError as e:
            print("Connection refused: ", e)

        except ConnectionError as e:
            print("Connection error: ", e)
        except Exception as e:
            print("Error: ", e)

    def perform(self, last_days: int = 0, year: bool = False, month: bool = False, showzeros: bool = False, machine_learning: bool = False, percentage: bool = False) -> dict:
        """
        Perform the analysis

        Args:
            last_days (int, optional): Number of days to consider. Defaults to 0.
            year (bool, optional): If True, returns the yearly growth. Defaults to False.
            month (bool, optional): If True, returns the monthly growth. Defaults to False.
            showzeros (bool, optional): If True, shows the days with zero growth. Defaults to False.
            machine_learning (bool, optional): If True, cumulative growth is not calculated. Defaults to False.
            percentage (bool, optional): If True, shows the percentage of growth in relation to the previous period. Defaults to False.

        Returns:
            dict: Dictionary containing growth as dictionary and cumulative growth data as dictionary

        Raises:
            ValueError: If the number of days is less than zero
        """
        self.machine_learning = machine_learning

        data = self.collect()
        if data == None:
            raise Exception("No data found")
        
        if last_days < 0:
            raise ValueError("The number of days should be greater than zero")

        try:
            data.sort(key=lambda i: i['signedUp']) # Sort by signedUp date
        except AttributeError as e:
            print("Attribute Error: ", e)
            return e
        
        try:

            if year:
                return self._getYearlyGrowth(data, showzeros, percentage)
            
            elif month:
                return self._getMonthlyGrowth(data, showzeros, percentage)
            
            else:
                return self._getGrowthByDays(data, last_days, showzeros, percentage)

        except ValueError as e:
            return e

    def report(self):
        pass

    def _getYearlyGrowth(self, data: list, showzeros: bool = False, percentage: bool = False) -> dict:
        """
        gets the yearly growth of the customers
        
        
        Args:
            data (list): List of dictionaries containing the data
            showzeros (bool) : If True, shows the years with zero growth
            percentage (bool) : If True, shows the percentage of growth in relation to the previous period

        Returns:
            dict: Dictionary containing the growth and cumulative growth data
        """

        yearlygrowth = defaultdict(int)
        cumulative_growth = {}
        total = 0 
        try:
            for i in data:
                if i['signedUp'] <= datetime.now():
                    year = i['signedUp'].year
                    
                    yearlygrowth[year] += 1
                    if not self.machine_learning:
                        total += 1
                        
                        cumulative_growth[year] = total
        except Exception as e:
            print("Error in _getYearlyGrowth total growth: ", e)
        
        try:
            if showzeros:
                yearlygrowth, cumulative_growth = self._showzeros(
                    growth=yearlygrowth, cumulative_growth=cumulative_growth,
                    end=datetime.now().year,
                    freq='YS',
                    format='%Y'
                )
        except Exception as e:
            print("Error in _getYearlyGrowth showzeros: ", e)

        return {"growth": self._calculate_percentage_growth(dict(yearlygrowth)) if percentage else dict(yearlygrowth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}

    def _getMonthlyGrowth(self, data: list, showzeros: bool = True, percentage: bool = False) -> dict:
        """
        gets the monthly growth of the customers

        Args:
            data (list): List of dictionaries containing the data
            showzeros (bool) : If True, shows the months with zero growth
            percentage (bool) : If True, shows the percentage of growth in relation to the previous period
        
        Returns:
            dict: Dictionary containing the growth and cumulative growth data
        """

        monthlygrowth = defaultdict(int)
        cumulative_growth = {}
        total = 0
        try:
            for i in data:
                month = i['signedUp'].strftime("%Y-%m")

                if i['signedUp'] <= datetime.now():
                    if not self.machine_learning:
                        total += 1
                        cumulative_growth[month] = total
                    
                    monthlygrowth[month] += 1
        except Exception as e:
            print("Error in _getMonthlyGrowth total growth: ", e)
            
        try:
            if showzeros:
                monthlygrowth, cumulative_growth = self._showzeros(
                    growth=monthlygrowth, cumulative_growth=cumulative_growth,
                    end=datetime.now(),
                    freq='MS',
                    format='%Y-%m'
                )

        except Exception as e:
            print("Error in _getMonthlyGrowth showzeros: ", e)

        return {"growth": self._calculate_percentage_growth(dict(monthlygrowth)) if percentage else dict(monthlygrowth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}

    def _getGrowthByDays(self, data: list, last_days: int, showzeros: bool = False, percentage: bool = False) -> dict:
        """
        gets the growth of the customers by the number of days

        Args:
            data (list): List of dictionaries containing the data
            last_days (int): Number of days to consider
            showzeros (bool): If True, shows the days with zero growth
            percentage (bool) : If True, shows the percentage of growth in relation to the previous period

        Returns:
            dict: Dictionary containing the growth and cumulative growth data

        Raises:
            ValueError: If the number of days is less than zero
        """
        
        growth = defaultdict(int)
        total = 0

        cumulative_growth = {}

        if last_days < 0:
                raise ValueError("The number of days should be greater than zero")

        try:
            for i in data:
                    if i['signedUp'].date() <= datetime.now().date():
                        if not self.machine_learning:
                            total += 1
                            cumulative_growth[i['signedUp'].date()] = total

                        if last_days > 0 and showzeros is False:
                            if i['signedUp'].date() >= datetime.now().date() - timedelta(days=last_days):
                                growth[i['signedUp'].date()] += 1
                        elif showzeros or last_days == 0:
                            growth[i['signedUp'].date()] += 1
        except Exception as e:
            print("Error in _getGrowthByDays: ", e)
        
        try:
            if showzeros:
                growth, cumulative_growth = self._showzeros(
                    growth=growth, cumulative_growth=cumulative_growth,
                    end=datetime.now(), freq='D',
                    format="%Y-%m-%d", last_days=last_days)
            else:
                if last_days > 0:
                    cumulative_growth = {k: v for k, v in cumulative_growth.items() if k >= datetime.now().date() - timedelta(days=last_days)}
       
        except Exception as e:
            print("Error in _getGrowthByDays showzeros: ", e)

        return {"growth": self._calculate_percentage_growth(dict(growth)) if percentage else dict(growth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}

    def _showzeros(self, growth: defaultdict, cumulative_growth: dict, end: datetime, freq: str, format: str, last_days: int = 0) -> tuple:
        """
        Fills in the missing dates with zero growth and forward fills the cumulative growth values.

        Args:
            growth (defaultdict): A defaultdict containing the growth data.
            cumulative_growth (dict): A dictionary containing the cumulative growth data.
            end (datetime): The end date for the date range.
            freq (str): The frequency for the date range (e.g., 'D' for daily, 'MS' for monthly start, 'YS' for yearly start).
            format (str): The date format to use for parsing and formatting dates (e.g., "%Y-%m-%d" for daily, "%Y-%m" for monthly, "%Y" for yearly).
            last_days (int, optional): The number of last days to consider for filtering the growth data. Only applicable when growth is calculated by days. Defaults to 0, which means no filtering.

        Returns:
            tuple: A tuple containing the updated growth and cumulative growth dictionaries with missing dates filled in and cumulative growth forward filled.
    
        Raises:
            ValueError: If the date format is invalid or if the end date is before the start date.
            KeyError: If the growth or cumulative growth data is missing for a specific date.
        """

        df_growth = pd.DataFrame.from_dict(growth, orient='index', columns=['growth'])
        df_cumulative_growth = pd.DataFrame.from_dict(cumulative_growth, orient='index', columns=['cumulative_growth'])

        df_growth.index = pd.to_datetime(df_growth.index.astype(str), format=format)
        end = pd.to_datetime(end, format=format)

        full_date_range = pd.date_range(start=df_growth.index.min(), end=end, freq=freq)
    
        df_growth_filled = df_growth.reindex(full_date_range, fill_value=0)
        df_growth_filled.index = df_growth_filled.index.strftime(format)
        df_growth_filled.update(df_growth)

        if format == "%Y":
            full_date_range = full_date_range.year
            df_cumulative_growth_filled = df_cumulative_growth.reindex(full_date_range)

            df_cumulative_growth_filled.ffill(inplace=True)
            df_cumulative_growth_filled.fillna(0, inplace=True)
        elif format == "%Y-%m":
            full_date_range = full_date_range.year.astype(str) + '-' + full_date_range.month.astype(str).str.zfill(2)
            df_cumulative_growth_filled = df_cumulative_growth.reindex(full_date_range)

            df_cumulative_growth_filled.ffill(inplace=True)
            df_cumulative_growth_filled.fillna(0, inplace=True)
        else:

            df_cumulative_growth_filled = df_cumulative_growth.reindex(full_date_range)
            df_cumulative_growth_filled.index = df_cumulative_growth_filled.index.strftime(format)
            df_cumulative_growth_filled.update(df_cumulative_growth)
            
            df_cumulative_growth_filled.replace(0, pd.NA, inplace=True)
            df_cumulative_growth_filled.ffill(inplace=True)
            df_cumulative_growth_filled.replace(pd.NA, 0, inplace=True)

            if last_days > 0:
                growth = df_growth_filled['growth'].iloc[-last_days:].to_dict()
                cumulative_growth = df_cumulative_growth_filled['cumulative_growth'].iloc[-last_days:].to_dict()
            elif last_days == 0:
                growth = df_growth_filled.to_dict()['growth']
                cumulative_growth = df_cumulative_growth_filled.to_dict()['cumulative_growth']

        return growth, cumulative_growth
    
    def _calculate_percentage_growth(self, growth: dict) -> dict:
        """
        Calculates the percentage growth in relation to the previous period.

        Args:
            growth (dict): A dictionary containing the growth data.

        Returns:
            dict: A dictionary containing the percentage growth and growth data.
            Example: {
                "2023": [0, 100],
                "2024": [100.0, 200]
            }
        """
        first_item = True
        try:
            percentage_growth = {}
            key_list = list(growth.keys())
            for i in range(len(key_list)):
                key = key_list[i]
                if first_item:
                    percentage_growth[key] = 0
                    first_item = False
                else:
                    previous_key = key_list[i-1]
                    if growth[previous_key] == 0:
                        percentage_growth[key] = 0
                    else:
                        percentage_growth[key] = round((growth[key] - growth[previous_key]) / growth[previous_key] * 100, 1)
            
            df = pd.DataFrame.from_dict(percentage_growth, orient='index', columns=['percentage_growth'])

            df_growth = pd.DataFrame.from_dict(growth, orient='index', columns=['growth'])

            df_combined = pd.concat([df, df_growth], axis=1)

            result = df_combined.apply(lambda row: [row["percentage_growth"], row["growth"]], axis=1).to_dict()

            return result
        except Exception as e:
            print("Error in _calculate_percentage_growth: ", e)
            return {}
