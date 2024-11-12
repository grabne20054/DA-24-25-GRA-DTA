from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from DataAnalysis.APIDataHandlerFactory import APIDataHandlerFactory

from datetime import datetime, timedelta
from collections import defaultdict


class CustomerSignup(DescriptiveAnalysis):
    """ Trend of Customer Growth
    """
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/customers")

    def collect(self) -> list:
        """
        Collects data from the API

        Returns:
            list: List of dictionaries containing the data
        """
        return self.handler.start()
        
    def perform(self, last_days: int = 0, year: bool = False, month: bool = False) -> dict:
        """
        Perform the analysis

        Args:
            last_days (int, optional): Number of days to consider. Defaults to 0.
            year (bool, optional): If True, returns the yearly growth. Defaults to False.
            month (bool, optional): If True, returns the monthly growth. Defaults to False.

        Returns:
            dict: Dictionary containing growth as dictionary and cumulative growth data as dictionary
        """
        data = self.collect()

        data.sort(key=lambda i: datetime.strptime(i['signedUp'], "%Y-%m-%dT%H:%M:%S.%f")) # Sort by signedUp date

        if year:
            return self._setYearlyGrowth(data)
        
        elif month:
            return self._setMonthlyGrowth(data)
        
        else:
            return self._setGrowthByDays(data, last_days)
        

    def report(self):
        pass

    def _setYearlyGrowth(self, data: list) -> dict:
        yearlygrowth = defaultdict(int)
        cumulative_growth = {}
        total = 0 

        for i in data:
            year = i['signedUp'].split("-")[0]
            
            yearlygrowth[year] += 1
            total += 1
            
            cumulative_growth[year] = total

        return {"growth": dict(yearlygrowth), "cumulative_growth": cumulative_growth}
    
    def _setMonthlyGrowth(self, data: list) -> dict:
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
    
    def _setGrowthByDays(self, data: list, last_days: int) -> dict:
        
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
            else:
                growth[i['signedUp']] += 1
                total += 1
                cumulative_growth[i['signedUp']] = total
        
        return {"growth": dict(growth), "cumulative_growth": cumulative_growth}