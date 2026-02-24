from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from DataAnalysis.preprocessing.APIDataHandlerFactory import APIDataHandlerFactory

from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from os import getenv

from dotenv import load_dotenv
load_dotenv()

TYPEOFGRAPH = "line"


class OrdersAmount(DescriptiveAnalysis):
    """ Trend of Orders Growth
    """
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/orders")

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

        try:
            data.sort(key=lambda i: i['orderDate']) # Sort by orderDate
        except AttributeError as e:
            print("Attribute Error: ", e)
            return None

        if year:
            return self._getYearlyGrowth(data, showzeros)
        
        elif month:
            return self._getMonthlyGrowth(data, showzeros)
        
        else:
            return self._getGrowthByDays(data, last_days, showzeros)
        

    def report(self):
        pass

    def _getYearlyGrowth(self, data: list, showzeros: bool = False) -> dict:
        """
        gets the yearly growth of the orders
        
        
        Args:
            data (list): List of dictionaries containing the data
            showzeros (bool) : If True, shows the years with zero growth
            
        Returns:
            dict: Dictionary containing the growth and cumulative growth data
        """

        yearlygrowth = defaultdict(int)
        cumulative_growth = {}
        total = 0 

        try:
            for i in data:
                if i['orderDate'] <= datetime.now():
                    year = i['orderDate'].year
                    
                    yearlygrowth[year] += 1
                    total += 1
                    
                    cumulative_growth[year] = total
        except Exception as e:
            print("Error in _getYearlyGrowth: ", e)
        
        try:
            if showzeros:
                df_growth = pd.DataFrame.from_dict(yearlygrowth, orient='index', columns=['growth'])
                df_cumulative_growth = pd.DataFrame.from_dict(cumulative_growth, orient='index', columns=['cumulative_growth'])

                df_growth.index = df_growth.index.astype(int)
                df_cumulative_growth.index = df_cumulative_growth.index.astype(int)

                start_year = df_growth.index.min()
                end_year = datetime.now().year - 1

                year_range = range(start_year, end_year + 1)

                df_growth_filled = df_growth.reindex(year_range, fill_value=0)
                df_cumulative_growth_filled = df_cumulative_growth.reindex(year_range)

                df_cumulative_growth_filled.ffill(inplace=True)
                df_cumulative_growth_filled.fillna(0, inplace=True)
                df_growth_filled.ffill(inplace=True)
                df_growth_filled.fillna(0, inplace=True)

                yearlygrowth = df_growth_filled['growth'].to_dict()
                cumulative_growth = df_cumulative_growth_filled['cumulative_growth'].to_dict()

        except Exception as e:
            print("Error in _getYearlyGrowth with showzeros: ", e)

        return {"growth": dict(yearlygrowth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}
    
    def _getMonthlyGrowth(self, data: list, showzeros: bool = False) -> dict:
        """
        gets the monthly growth of the orders

        Args:
            data (list): List of dictionaries containing the data
            showzeros (bool) : If True, shows the months with zero growth
        
        Returns:
            dict: Dictionary containing the growth and cumulative growth data
        """

        monthlygrowth = defaultdict(int)
        cumulative_growth = {}
        total = 0

        try:

            for i in data:
                month = i['orderDate'].strftime("%Y-%m")
                if i['orderDate'] <= datetime.now():
                    total += 1

                    cumulative_growth[month] = total
                    monthlygrowth[month] += 1
        except Exception as e:
            print("Error in _getMonthlyGrowth: ", e)

        try:

            if showzeros:
                df_growth = pd.DataFrame.from_dict(monthlygrowth, orient='index', columns=['growth'])
                df_cumulative_growth = pd.DataFrame.from_dict(cumulative_growth, orient='index', columns=['cumulative_growth'])
                    
                full_date_range = pd.date_range(start=df_growth.index.min(), end=datetime.now() - pd.DateOffset(months=1) , freq='MS')
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

        except Exception as e:
            print("Error in _getMonthlyGrowth with showzeros: ", e)
        
        return {"growth": dict(monthlygrowth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}
    
    def _getGrowthByDays(self, data: list, last_days: int, showzeros: bool = False) -> dict:
        """
        gets the growth of the orders by the number of days

        Args:
            data (list): List of dictionaries containing the data
            last_days (int): Number of days to consider
            showzeros (bool) : If True, shows the days with zero growth

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
                if i['orderDate'].date() <= datetime.now().date():
                    total += 1
                    cumulative_growth[i['orderDate'].date()] = total

                    if last_days > 0 and showzeros is False:
                        if i['orderDate'].date() >= datetime.now().date() - timedelta(days=last_days):
                            growth[i['orderDate'].date()] += 1
                    elif showzeros or last_days == 0:
                        growth[i['orderDate'].date()] += 1
        except Exception as e:
            print("Error in _getGrowthByDays: ", e)
            

        try:    
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
            elif last_days > 0:
                cumulative_growth = {k: v for k, v in cumulative_growth.items() if k >= datetime.now().date() - timedelta(days=last_days)}
        
        except Exception as e:
            print("Error in _getGrowthByDays with showzeros: ", e)
        
        return {"growth": dict(growth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}