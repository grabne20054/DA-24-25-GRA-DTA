from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from DataAnalysis.DataCollector import DataCollector
from DataAnalysis.db.models.CustomerSignup import CustomerSignupRepository
from DataAnalysis.db.models.queryparams import CustomerSignup as CustomerSignupParams
from DataAnalysis.descriptive.dependencies import showZeros, calculate_percentage_growth

from datetime import datetime, timedelta
from collections import defaultdict


from dotenv import load_dotenv
load_dotenv()

TYPEOFGRAPH = "line"


class CustomerSignup(DataCollector):
    """ Trend of Customer Growth
    """
    def __init__(self) -> None:
        super().__init__()

    def collect(self) -> list[CustomerSignupParams]:
        """
        Collects data from the DB

        Returns:
            list: List of dictionaries containing the data
        """
        try:
            return CustomerSignupRepository(self.db).get()
        except ConnectionRefusedError as e:
            print("Connection refused: ", e)
        except ConnectionError as e:
            print("Connection error: ", e)
        except Exception as e:
            print("Error: ", e)

    def perform(self, last_days: int = 0, year: bool = False, month: bool = False, showzeros: bool = False,percentage: bool = False, cumulative: bool = False) -> dict:
        """
        Perform the analysis

        Args:
            last_days (int, optional): Number of days to consider. Defaults to 0.
            year (bool, optional): If True, returns the yearly growth. Defaults to False.
            month (bool, optional): If True, returns the monthly growth. Defaults to False.
            showzeros (bool, optional): If True, shows the days with zero growth. Defaults to False.
            cumulative (bool, optional): If True, cumulative growth is not calculated. Defaults to False.
            percentage (bool, optional): If True, shows the percentage of growth in relation to the previous period. Defaults to False.

        Returns:
            dict: Dictionary containing growth as dictionary and cumulative growth data as dictionary

        Raises:
            ValueError: If the number of days is less than zero
        """
        self.cumulative = cumulative

        data = self.collect()
        if data == None:
            raise Exception("No data found")
        
        if last_days < 0:
            raise ValueError("The number of days should be greater than zero")

        try:
            data.sort(key=lambda i: i.signedUp) # Sort by signedUp date
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

    def _getYearlyGrowth(self, data: list[CustomerSignupParams], showzeros: bool = False, percentage: bool = False) -> dict:
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
                if i.signedUp <= datetime.now():
                    year = i.signedUp.year
                    
                    yearlygrowth[year] += 1
                    if self.cumulative:
                        total += 1
                        
                        cumulative_growth[year] = total
        except Exception as e:
            print("Error in _getYearlyGrowth total growth: ", e)
        
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
            print("Error in _getYearlyGrowth showzeros: ", e)

        return {"growth": calculate_percentage_growth(dict(yearlygrowth)) if percentage else dict(yearlygrowth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}

    def _getMonthlyGrowth(self, data: list[CustomerSignupParams], showzeros: bool = False, percentage: bool = False) -> dict:
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
                month = i.signedUp.strftime("%Y-%m")

                if i.signedUp <= datetime.now():
                    if self.cumulative:
                        total += 1
                        cumulative_growth[month] = total
                    
                    monthlygrowth[month] += 1
        except Exception as e:
            print("Error in _getMonthlyGrowth total growth: ", e)
            
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
            print("Error in _getMonthlyGrowth showzeros: ", e)

        return {"growth": calculate_percentage_growth(dict(monthlygrowth)) if percentage else dict(monthlygrowth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}

    def _getGrowthByDays(self, data: list[CustomerSignupParams], last_days: int, showzeros: bool = False, percentage: bool = False) -> dict:
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
                    if i.signedUp.date() <= datetime.now().date():
                        if self.cumulative:
                            total += 1
                            cumulative_growth[i.signedUp.date()] = total

                        if last_days > 0 and showzeros is False:
                            if i.signedUp.date() >= datetime.now().date() - timedelta(days=last_days):
                                growth[i.signedUp.date()] += 1
                        elif showzeros or last_days == 0:
                            growth[i.signedUp.date()] += 1
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
            else:
                if last_days > 0:
                    cumulative_growth = {k: v for k, v in cumulative_growth.items() if k >= datetime.now().date() - timedelta(days=last_days)}
       
        except Exception as e:
            print("Error in _getGrowthByDays showzeros: ", e)

        return {"growth": calculate_percentage_growth(dict(growth)) if percentage else dict(growth), "cumulative_growth": cumulative_growth, "typeofgraph": TYPEOFGRAPH}
