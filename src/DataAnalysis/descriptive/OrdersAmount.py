from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from DataAnalysis.DataCollector import DataCollector
from DataAnalysis.db.models.OrderAmount import OrderAmountRepository
from DataAnalysis.db.models.queryparams import OrderAmount as OrderAmountParams
from DataAnalysis.descriptive.dependencies import showZeros, calculate_percentage_growth

from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from os import getenv

from dotenv import load_dotenv
load_dotenv()

TYPEOFGRAPH = "line"


class OrdersAmount(DataCollector, DescriptiveAnalysis):
    """ Trend of Orders Growth
    """
    def __init__(self) -> None:
        super().__init__()

    def collect(self) -> list[OrderAmountParams]:
        """
        Collects data from the DB

        Returns:
            list: List of dictionaries containing the data
        """
        try:
            return OrderAmountRepository(self.db).get()
        except ConnectionRefusedError as e:
            print("Connection refused: ", e)
        except ConnectionError as e:
            print("Connection error: ", e)
        except Exception as e:
            print("Error: ", e)

    def perform(self, last_days: int = 0, year: bool = False, month: bool = False, showzeros: bool = False, percentage: bool = False, cumulative: bool = False) -> dict:
        """
        Perform the analysis

        Args:
            last_days (int, optional): Number of days to consider. Defaults to 0.
            year (bool, optional): If True, returns the yearly growth. Defaults to False.
            month (bool, optional): If True, returns the monthly growth. Defaults to False.
            showzeros (bool, optional): If True, shows the days with zero growth. Defaults to False.
            cumulative (bool, optional): If True, cumulative growth is calculated. Defaults to False.
            percentage (bool, optional): If True, shows the percentage growth in relation to the previous period. Defaults to False.

        Returns:
            dict: Dictionary containing growth as dictionary and cumulative growth data as dictionary if percentage is False, otherwise growth as dictionary with percentage growth and cumulative growth as dictionary with cumulative growth data. The type of graph is also included in the dictionary.

s
        Raises:
            ValueError: If the number of days is less than zero
        """
        self.cumulative = cumulative

        data = self.collect()
        if data == None:
            raise Exception("No data found")

        try:
            data.sort(key=lambda i: i.orderDate) # Sort by orderDate
        except AttributeError as e:
            print("Attribute Error: ", e)
            return None

        if year:
            return self._getYearlyGrowth(data, showzeros, percentage)
        
        elif month:
            return self._getMonthlyGrowth(data, showzeros, percentage)
        
        else:
            return self._getGrowthByDays(data, last_days, showzeros, percentage)

    def report(self):
        pass

    def _getYearlyGrowth(self, data: list[OrderAmountParams], showzeros: bool = False, percentage: bool = False) -> dict:
        """
        gets the yearly growth of the orders
        
        
        Args:
            data (list): List of dictionaries containing the data
            showzeros (bool) : If True, shows the years with zero growth
            percentage (bool) : If True, shows the percentage growth in relation to the previous year
            
        Returns:
            dict: Dictionary containing the growth and cumulative growth data
        """

        yearlygrowth = defaultdict(int)
        cumulative_growth = {}
        total = 0 

        try:
            for i in data:
                if i.orderDate <= datetime.now():
                    year = i.orderDate.year

                    yearlygrowth[year] += 1
                    if self.cumulative:
                        total += 1
                        cumulative_growth[year] = total
        except Exception as e:
            print("Error in _getYearlyGrowth: ", e)
        
        try:
            if showzeros:
                yearlygrowth, cumulative_growth = showZeros(
                    growth=yearlygrowth, cumulative_growth=cumulative_growth if self.cumulative else None,
                    end=datetime.now().year,
                    freq='YS',
                    format='%Y',
                    cumulative=self.cumulative
                )
                
        except Exception as e:
            print("Error in _getYearlyGrowth with showzeros: ", e)

        return {"growth": calculate_percentage_growth(yearlygrowth) if percentage else dict(yearlygrowth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}

    def _getMonthlyGrowth(self, data: list[OrderAmountParams], showzeros: bool = False, percentage: bool = False) -> dict:
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
                month = i.orderDate.strftime("%Y-%m")

                if i.orderDate <= datetime.now():
                    if self.cumulative:
                        total += 1
                        cumulative_growth[month] = total

                    monthlygrowth[month] += 1
        except Exception as e:
            print("Error in _getMonthlyGrowth: ", e)

        try:
            if showzeros:
                monthlygrowth, cumulative_growth = showZeros(
                    growth=monthlygrowth, cumulative_growth=cumulative_growth if self.cumulative else None,
                    end=datetime.now(),
                    freq='MS',
                    format='%Y-%m',
                    cumulative=self.cumulative
                )

        except Exception as e:
            print("Error in _getMonthlyGrowth with showzeros: ", e)

        return {"growth": calculate_percentage_growth(monthlygrowth) if percentage else dict(monthlygrowth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}

    def _getGrowthByDays(self, data: list[OrderAmountParams], last_days: int, showzeros: bool = False, percentage: bool = False) -> dict:
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
                if i.orderDate.date() <= datetime.now().date():
                    if self.cumulative:
                        total += 1
                        cumulative_growth[i.orderDate.date()] = total

                    if last_days > 0 and showzeros is False:
                        if i.orderDate.date() >= datetime.now().date() - timedelta(days=last_days):
                            growth[i.orderDate.date()] += 1
                    elif showzeros or last_days == 0:
                        growth[i.orderDate.date()] += 1
        except Exception as e:
            print("Error in _getGrowthByDays: ", e)
            
        try:    
            if showzeros:
                growth, cumulative_growth = showZeros(
                    growth=growth, cumulative_growth=cumulative_growth if self.cumulative else None,
                    end=datetime.now(), freq='D',
                    format="%Y-%m-%d",
                    last_days=last_days,
                    cumulative=self.cumulative)
                
            elif last_days > 0:
                cumulative_growth = {k: v for k, v in cumulative_growth.items() if k >= datetime.now().date() - timedelta(days=last_days)}
        
        except Exception as e:
            print("Error in _getGrowthByDays with showzeros: ", e)

        return {"growth": calculate_percentage_growth(dict(growth)) if percentage else dict(growth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}
