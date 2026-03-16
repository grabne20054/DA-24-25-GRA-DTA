from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from DataAnalysis.DataCollector import DataCollector
from DataAnalysis.db.models.InvoicesAmount import InvoicesAmountRepository
from DataAnalysis.db.models.queryparams import InvoicesAmount as InvoicesAmountParams
from DataAnalysis.descriptive.dependencies import showZeros, calculate_percentage_growth

from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from os import getenv

from dotenv import load_dotenv
load_dotenv()

TYPEOFGRAPH = "line"


class InvoicesAmount(DataCollector, DescriptiveAnalysis):
    """ Trend of Invoices Growth
    """
    def __init__(self) -> None:
        super().__init__()

    def collect(self) -> list[InvoicesAmountParams]:
        """
        Collects data from the DB

        Returns:
            list: List of dictionaries containing the data
        """
        try:
            return InvoicesAmountRepository(self.db).get()
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
            year (bool, optional): If True, returns the yearly amount. Defaults to False.
            month (bool, optional): If True, returns the monthly amount. Defaults to False.
            showzeros (bool, optional): If True, shows the days with zero amount. Defaults to False.
            percentage (bool, optional): If True, shows the percentage amount in relation to the previous period. Defaults to False.
            cumulative (bool, optional): If True, cumulative growth is calculated. Defaults to False.

        Returns:
            dict: Dictionary containing amount as dictionary and cumulative amount data as dictionary if percentage is False, otherwise amount as dictionary with percentage amount and cumulative amount as dictionary with cumulative amount data. The type of graph is also included in the dictionary.

s
        Raises:
            ValueError: If the number of days is less than zero
        """
        self.cumulative = cumulative

        data = self.collect()
        if data == None:
            raise Exception("No data found")

        try:
            data.sort(key=lambda i: i.paymentDate) # Sort by paymentDate
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

    def _getYearlyGrowth(self, data: list[InvoicesAmountParams], showzeros: bool = False, percentage: bool = False) -> dict:
        """
        gets the yearly amount of the invoices
        
        
        Args:
            data (list): List of dictionaries containing the data
            showzeros (bool) : If True, shows the years with zero amount
            percentage (bool) : If True, shows the percentage amount in relation to the previous year
            
        Returns:
            dict: Dictionary containing the amount and cumulative amount data
        """

        yearlyamount = defaultdict(int)
        cumulative_amount = {}
        total = 0 

        try:
            for i in data:
                if i.paymentDate <= datetime.now():
                    year = i.paymentDate.year

                    yearlyamount[year] += i.invoiceAmount
                    if self.cumulative:
                        total += i.invoiceAmount
                        cumulative_amount[year] = total
        except Exception as e:
            print("Error in _getYearlyGrowth: ", e)
        
        try:
            if showzeros:
                yearlyamount, cumulative_amount = showZeros(
                    growth=yearlyamount, cumulative_growth=cumulative_amount if self.cumulative else None,
                    end=datetime.now().year,
                    freq='YS',
                    format='%Y',
                    cumulative=self.cumulative
                )
                
        except Exception as e:
            print("Error in _getYearlyGrowth with showzeros: ", e)

        return {"amount": calculate_percentage_growth(yearlyamount) if percentage else dict(yearlyamount), "cumulative_amount": cumulative_amount, "typeofgraph": TYPEOFGRAPH}

    def _getMonthlyGrowth(self, data: list[InvoicesAmountParams], showzeros: bool = False, percentage: bool = False) -> dict:
        """
        gets the monthly amount of the invoices

        Args:
            data (list): List of dictionaries containing the data
            showzeros (bool) : If True, shows the months with zero amount
        
        Returns:
            dict: Dictionary containing the amount and cumulative amount data
        """

        monthlyamount = defaultdict(int)
        cumulative_amount = {}
        total = 0

        try:

            for i in data:
                month = i.paymentDate.strftime("%Y-%m")

                if i.paymentDate <= datetime.now():
                    if self.cumulative:
                        total += i.invoiceAmount
                        cumulative_amount[month] = total

                    monthlyamount[month] += i.invoiceAmount
        except Exception as e:
            print("Error in _getMonthlyGrowth: ", e)

        try:
            if showzeros:
                monthlyamount, cumulative_amount = showZeros(
                    growth=monthlyamount, cumulative_growth=cumulative_amount if self.cumulative else None,
                    end=datetime.now(),
                    freq='MS',
                    format='%Y-%m',
                    cumulative=self.cumulative
                )

        except Exception as e:
            print("Error in _getMonthlyGrowth with showzeros: ", e)

        return {"amount": calculate_percentage_growth(monthlyamount) if percentage else dict(monthlyamount), "cumulative_amount": cumulative_amount, "typeofgraph": TYPEOFGRAPH}

    def _getGrowthByDays(self, data: list[InvoicesAmountParams], last_days: int, showzeros: bool = False, percentage: bool = False) -> dict:
        """
        gets the amount of the invoices by the number of days

        Args:
            data (list): List of dictionaries containing the data
            last_days (int): Number of days to consider
            showzeros (bool) : If True, shows the days with zero amount

        Returns:
            dict: Dictionary containing the amount and cumulative amount data

        Raises:
            ValueError: If the number of days is less than zero
        """
        
        amount = defaultdict(int)
        total = 0

        cumulative_amount = {}

        if last_days < 0:
                raise ValueError("The number of days should be greater than zero")

        try:
            for i in data:
                if i.paymentDate.date() <= datetime.now().date():
                    if self.cumulative:
                        total += i.invoiceAmount
                        cumulative_amount[i.paymentDate.date()] = total

                    if last_days > 0 and showzeros is False:
                        if i.paymentDate.date() >= datetime.now().date() - timedelta(days=last_days):
                            amount[i.paymentDate.date()] += i.invoiceAmount
                    elif showzeros or last_days == 0:
                        amount[i.paymentDate.date()] += i.invoiceAmount
        except Exception as e:
            print("Error in _getGrowthByDays: ", e)
            
        try:    
            if showzeros:
                amount, cumulative_amount = showZeros(
                    growth=amount, cumulative_growth=cumulative_amount if self.cumulative else None,
                    end=datetime.now(), freq='D',
                    format="%Y-%m-%d",
                    last_days=last_days,
                    cumulative=self.cumulative)
                
            elif last_days > 0:
                cumulative_amount = {k: v for k, v in cumulative_amount.items() if k >= datetime.now().date() - timedelta(days=last_days)}
        
        except Exception as e:
            print("Error in _getGrowthByDays with showzeros: ", e)

        return {"amount": calculate_percentage_growth(dict(amount)) if percentage else dict(amount), "cumulative_amount": cumulative_amount, "typeofgraph": TYPEOFGRAPH}
