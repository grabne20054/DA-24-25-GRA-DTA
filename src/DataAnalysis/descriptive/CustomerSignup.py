from descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from preprocessing.APIDataHandlerFactory import APIDataHandlerFactory

from datetime import datetime, timedelta
from collections import defaultdict
from os import getenv

from dotenv import load_dotenv
load_dotenv()


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
        
    def perform(self, last_days: int = 0, year: bool = False, month: bool = False) -> dict:
        """
        Perform the analysis

        Args:
            last_days (int, optional): Number of days to consider. Defaults to 0.
            year (bool, optional): If True, returns the yearly growth. Defaults to False.
            month (bool, optional): If True, returns the monthly growth. Defaults to False.

        Returns:
            dict: Dictionary containing growth as dictionary and cumulative growth data as dictionary#
        
        Raises:
            ValueError: If the number of days is less than zero
        """

        data = self.collect()
        if data == None:
            raise Exception("No data found")

        try:
            data.sort(key=lambda i: datetime.strptime(i['signedUp'], "%Y-%m-%dT%H:%M:%S.%f")) # Sort by signedUp date
        except AttributeError as e:
            print("Attribute Error: ", e)
            return None

        if year:
            return self._getYearlyGrowth(data)
        
        elif month:
            return self._getMonthlyGrowth(data)
        
        else:
            return self._getGrowthByDays(data, last_days)
        

    def report(self):
        pass

    def _getYearlyGrowth(self, data: list) -> dict:
        """
        gets the yearly growth of the customers
        
        
        Args:
            data (list): List of dictionaries containing the data
            
        Returns:
            dict: Dictionary containing the growth and cumulative growth data
        """

        yearlygrowth = defaultdict(int)
        cumulative_growth = {}
        total = 0 

        for i in data:
            year = i['signedUp'].split("-")[0]
            
            yearlygrowth[year] += 1
            total += 1
            
            cumulative_growth[year] = total

        return {"growth": dict(yearlygrowth), "cumulative_growth": cumulative_growth}
    
    def _getMonthlyGrowth(self, data: list) -> dict:
        """
        gets the monthly growth of the customers

        Args:
            data (list): List of dictionaries containing the data
        
        Returns:
            dict: Dictionary containing the growth and cumulative growth data
        """

        monthlygrowth = defaultdict(int)
        cumulative_growth = {}
        total = 0

        for i in data:
            if datetime.strptime(i['signedUp'], "%Y-%m-%dT%H:%M:%S.%f").year == datetime.now().year:
                month = i['signedUp'].split("-")[1]
                monthlygrowth[month] += 1
                total += 1

                cumulative_growth[month] = total
        
        return {"growth": dict(monthlygrowth), "cumulative_growth": cumulative_growth}
    
    def _getGrowthByDays(self, data: list, last_days: int) -> dict:
        """
        gets the growth of the customers by the number of days

        Args:
            data (list): List of dictionaries containing the data
            last_days (int): Number of days to consider

        Returns:
            dict: Dictionary containing the growth and cumulative growth data

        Raises:
            ValueError: If the number of days is less than zero
        """
        
        growth = defaultdict(int)
        total = 0

        cumulative_growth = {}

        for i in data:
            i['signedUp'] = i['signedUp'].split("t")[0]
            if last_days > 0:
                if datetime.strptime(i['signedUp'], "%Y-%m-%d") >= datetime.now() - timedelta(days=last_days):
                    growth[i['signedUp']] += 1
                    total += 1

                    cumulative_growth[i['signedUp']] = total
            elif last_days == 0:
                growth[i['signedUp']] += 1
                total += 1
                cumulative_growth[i['signedUp']] = total
            elif last_days < 0:
                raise ValueError("The number of days should be greater than zero")
        
        return {"growth": dict(growth), "cumulative_growth": cumulative_growth}