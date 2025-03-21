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
        
    def perform(self, last_days: int = 0, year: bool = False, month: bool = False, showzeros: bool = False) -> dict:
        """
        Perform the analysis

        Args:
            last_days (int, optional): Number of days to consider. Defaults to 0.
            year (bool, optional): If True, returns the yearly growth. Defaults to False.
            month (bool, optional): If True, returns the monthly growth. Defaults to False.
            showzeros (bool, optional): If True, shows the days with zero growth. Defaults to False.

        Returns:
            dict: Dictionary containing growth as dictionary and cumulative growth data as dictionary#
        
        Raises:
            ValueError: If the number of days is less than zero
        """

        data = self.collect()
        if data == None:
            raise Exception("No data found")
        
        if last_days < 0:
            raise ValueError("The number of days should be greater than zero")

        try:
            data.sort(key=lambda i: datetime.strptime(i['signedUp'], "%Y-%m-%dT%H:%M:%S.%f")) # Sort by signedUp date
        except AttributeError as e:
            print("Attribute Error: ", e)
            return e
        
        try:

            if year:
                return self._getYearlyGrowth(data, showzeros)
            
            elif month:
                return self._getMonthlyGrowth(data, showzeros)
            
            else:
                return self._getGrowthByDays(data, last_days, showzeros)
            
        except ValueError as e:
            return e

    def report(self):
        pass

    def _getYearlyGrowth(self, data: list, showzeros: bool = False) -> dict:
        """
        gets the yearly growth of the customers
        
        
        Args:
            data (list): List of dictionaries containing the data
            showzeros (bool) : If True, shows the years with zero growth
            
        Returns:
            dict: Dictionary containing the growth and cumulative growth data
        """

        yearlygrowth = defaultdict(int)
        cumulative_growth = {}
        total = 0 

        for i in data:
            if datetime.strptime(i['signedUp'], "%Y-%m-%dT%H:%M:%S.%f") <= datetime.now():
                year = i['signedUp'].split("-")[0]
                
                yearlygrowth[year] += 1
                total += 1
                
                cumulative_growth[year] = total
        
        if showzeros:
            df_growth = pd.DataFrame.from_dict(yearlygrowth, orient='index', columns=['growth'])
            df_cumulative_growth = pd.DataFrame.from_dict(cumulative_growth, orient='index', columns=['cumulative_growth'])
                
            full_date_range = pd.date_range(start=df_growth.index.min(), end=datetime.now()- pd.DateOffset(years=1), freq='YS')
            year_index = full_date_range.strftime("%Y")
            
            df_growth_filled = df_growth.reindex(year_index, fill_value=0)
            df_growth_filled.index = df_growth_filled.index
            df_growth_filled.update(df_growth)
            
            df_cumulative_growth_filled = df_cumulative_growth.reindex(year_index, fill_value=0)
            df_cumulative_growth_filled.index = df_cumulative_growth_filled.index
            df_cumulative_growth_filled.update(df_cumulative_growth)

            df_cumulative_growth_filled.replace(0, pd.NA, inplace=True)
            df_cumulative_growth_filled.ffill(inplace=True)
            df_cumulative_growth_filled.replace(pd.NA, 0, inplace=True)

            yearlygrowth = df_growth_filled.to_dict()['growth']
            cumulative_growth = df_cumulative_growth_filled.to_dict()['cumulative_growth']

        return {"growth": dict(yearlygrowth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}
    
    def _getMonthlyGrowth(self, data: list, showzeros: bool = True) -> dict:
        """
        gets the monthly growth of the customers

        Args:
            data (list): List of dictionaries containing the data
            showzeros (bool) : If True, shows the months with zero growth
        
        Returns:
            dict: Dictionary containing the growth and cumulative growth data
        """

        monthlygrowth = defaultdict(int)
        cumulative_growth = {}
        total = 0

        for i in data:
            signed_up = datetime.strptime(i['signedUp'], "%Y-%m-%dT%H:%M:%S.%f")
            month = signed_up.strftime("%Y-%m")

            if signed_up <= datetime.now():
                total += 1
                cumulative_growth[month] = total
                
                monthlygrowth[month] += 1

        if showzeros:
            df_growth = pd.DataFrame.from_dict(monthlygrowth, orient='index', columns=['growth'])
            df_cumulative_growth = pd.DataFrame.from_dict(cumulative_growth, orient='index', columns=['cumulative_growth'])
                
            full_date_range = pd.date_range(start=df_growth.index.min(), end=datetime.now()- pd.DateOffset(months=1), freq='MS')
            month_index = full_date_range.strftime("%Y-%m")
            
            df_growth_filled = df_growth.reindex(month_index, fill_value=0)
            df_growth_filled.index = df_growth_filled.index
            df_growth_filled.update(df_growth)
            
            df_cumulative_growth_filled = df_cumulative_growth.reindex(month_index, fill_value=0)
            df_cumulative_growth_filled.index = df_cumulative_growth_filled.index
            df_cumulative_growth_filled.update(df_cumulative_growth)

            df_cumulative_growth_filled.replace(0, pd.NA, inplace=True)
            df_cumulative_growth_filled.ffill(inplace=True)
            df_cumulative_growth_filled.replace(pd.NA, 0, inplace=True)

            monthlygrowth = df_growth_filled.to_dict()['growth']
            cumulative_growth = df_cumulative_growth_filled.to_dict()['cumulative_growth']
        
        return {"growth": dict(monthlygrowth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}
    
    def _getGrowthByDays(self, data: list, last_days: int, showzeros: bool = False) -> dict:
        """
        gets the growth of the customers by the number of days

        Args:
            data (list): List of dictionaries containing the data
            last_days (int): Number of days to consider
            showzeros (bool): If True, shows the days with zero growth

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

        
        for i in data:
            i['signedUp'] = i['signedUp'].split("t")[0]

            if datetime.strptime(i['signedUp'], "%Y-%m-%d") <= datetime.now():
                total += 1
                cumulative_growth[i['signedUp']] = total

                if last_days > 0 and showzeros is False:
                    if (datetime.strptime(i['signedUp'], "%Y-%m-%d") >= datetime.now() - timedelta(days=last_days)):
                        growth[i['signedUp']] += 1
                elif showzeros or last_days == 0:
                    growth[i['signedUp']] += 1
        
        if showzeros:
            df_growth = pd.DataFrame.from_dict(growth, orient='index', columns=['growth'])
            df_cumulative_growth = pd.DataFrame.from_dict(cumulative_growth, orient='index', columns=['cumulative_growth'])
                
           
            full_date_range = pd.date_range(start=df_growth.index.min(), end=datetime.now() - pd.DateOffset(days=1), freq='D')
           
            df_growth_filled = df_growth.reindex(full_date_range, fill_value=0)
            df_growth_filled.index = df_growth_filled.index.strftime("%Y-%m-%d")
            df_growth_filled.update(df_growth)
            
            df_cumulative_growth_filled = df_cumulative_growth.reindex(full_date_range, fill_value=0)
            df_cumulative_growth_filled.index = df_cumulative_growth_filled.index.strftime("%Y-%m-%d")
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
        else:
            if last_days > 0:
                cumulative_growth = {k: v for k, v in cumulative_growth.items() if datetime.strptime(k, "%Y-%m-%d") >= datetime.now() - timedelta(days=last_days)}
        
        return {"growth": dict(growth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}