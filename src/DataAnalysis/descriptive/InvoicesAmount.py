from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from DataAnalysis.DataCollector import DataCollector
from DataAnalysis.db.models.InvoicesAmount import InvoicesAmountRepository
from DataAnalysis.db.models.queryparams import InvoicesAmount as InvoicesAmountParams

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
                yearlyamount, cumulative_amount = self._showzeros(
                    amount=yearlyamount, cumulative_amount=cumulative_amount if self.cumulative else None,
                    end=datetime.now().year,
                    freq='YS',
                    format='%Y'
                )
                
        except Exception as e:
            print("Error in _getYearlyGrowth with showzeros: ", e)

        return {"amount": self._calculate_percentage_amount(yearlyamount) if percentage else dict(yearlyamount), "cumulative_amount": cumulative_amount, "typeofgraph": TYPEOFGRAPH}

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
                monthlyamount, cumulative_amount = self._showzeros(
                    amount=monthlyamount, cumulative_amount=cumulative_amount if self.cumulative else None,
                    end=datetime.now(),
                    freq='MS',
                    format='%Y-%m'
                )

        except Exception as e:
            print("Error in _getMonthlyGrowth with showzeros: ", e)

        return {"amount": self._calculate_percentage_amount(monthlyamount) if percentage else dict(monthlyamount), "cumulative_amount": cumulative_amount, "typeofgraph": TYPEOFGRAPH}

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
                amount, cumulative_amount = self._showzeros(
                    amount=amount, cumulative_amount=cumulative_amount if self.cumulative else None,
                    end=datetime.now(), freq='D',
                    format="%Y-%m-%d", last_days=last_days)
                
            elif last_days > 0:
                cumulative_amount = {k: v for k, v in cumulative_amount.items() if k >= datetime.now().date() - timedelta(days=last_days)}
        
        except Exception as e:
            print("Error in _getGrowthByDays with showzeros: ", e)

        return {"amount": self._calculate_percentage_amount(dict(amount)) if percentage else dict(amount), "cumulative_amount": cumulative_amount, "typeofgraph": TYPEOFGRAPH}

    def _showzeros(self, amount: defaultdict, cumulative_amount: dict, end: datetime, freq: str, format: str, last_days: int = 0) -> tuple:
        """
        Fills in the missing dates with zero amount and forward fills the cumulative amount values.

        Args:
            amount (defaultdict): A defaultdict containing the amount data.
            cumulative_amount (dict): A dictionary containing the cumulative amount data.
            end (datetime): The end date for the date range.
            freq (str): The frequency for the date range (e.g., 'D' for daily, 'MS' for monthly start, 'YS' for yearly start).
            format (str): The date format to use for parsing and formatting dates (e.g., "%Y-%m-%d" for daily, "%Y-%m" for monthly, "%Y" for yearly).
            last_days (int, optional): The number of last days to consider for filtering the amount data. Only applicable when amount is calculated by days. Defaults to 0, which means no filtering.

        Returns:
            tuple: A tuple containing the updated amount and cumulative amount dictionaries with missing dates filled in and cumulative amount forward filled.
    
        Raises:
            ValueError: If the date format is invalid or if the end date is before the start date.
            KeyError: If the amount or cumulative amount data is missing for a specific date.
        """

        df_amount = pd.DataFrame.from_dict(amount, orient='index', columns=['amount'])
        df_cumulative_amount = pd.DataFrame.from_dict(cumulative_amount, orient='index', columns=['cumulative_amount'])

        df_amount.index = pd.to_datetime(df_amount.index.astype(str), format=format)
        end = pd.to_datetime(end, format=format)

        full_date_range = pd.date_range(start=df_amount.index.min(), end=end, freq=freq)
    
        df_amount_filled = df_amount.reindex(full_date_range, fill_value=0)
        df_amount_filled.index = df_amount_filled.index.strftime(format)
        df_amount_filled.update(df_amount)

        if format == "%Y":
            full_date_range = full_date_range.year
            df_cumulative_amount_filled = df_cumulative_amount.reindex(full_date_range)

            df_cumulative_amount_filled.ffill(inplace=True)
            df_cumulative_amount_filled.fillna(0, inplace=True)

            amount = df_amount_filled['amount'].to_dict()
            cumulative_amount = df_cumulative_amount_filled['cumulative_amount'].to_dict()
        elif format == "%Y-%m":
            full_date_range = full_date_range.year.astype(str) + '-' + full_date_range.month.astype(str).str.zfill(2)
            df_cumulative_amount_filled = df_cumulative_amount.reindex(full_date_range)

            df_cumulative_amount_filled.ffill(inplace=True)
            df_cumulative_amount_filled.fillna(0, inplace=True)

            amount = df_amount_filled['amount'].to_dict()
            cumulative_amount = df_cumulative_amount_filled['cumulative_amount'].to_dict()
        else:

            df_cumulative_amount_filled = df_cumulative_amount.reindex(full_date_range)
            df_cumulative_amount_filled.index = df_cumulative_amount_filled.index.strftime(format)
            df_cumulative_amount_filled.update(df_cumulative_amount)
            
            df_cumulative_amount_filled.replace(0, pd.NA, inplace=True)
            df_cumulative_amount_filled.ffill(inplace=True)
            df_cumulative_amount_filled.replace(pd.NA, 0, inplace=True)

            if last_days > 0:
                amount = df_amount_filled['amount'].iloc[-last_days:].to_dict()
                cumulative_amount = df_cumulative_amount_filled['cumulative_amount'].iloc[-last_days:].to_dict()
            elif last_days == 0:
                amount = df_amount_filled.to_dict()['amount']
                cumulative_amount = df_cumulative_amount_filled.to_dict()['cumulative_amount']

        return amount, cumulative_amount
    
    def _calculate_percentage_amount(self, amount: dict) -> dict:
        """
        Calculates the percentage amount in relation to the previous period.

        Args:
            amount (dict): A dictionary containing the amount data.

        Returns:
            dict: A dictionary containing the percentage amount and amount data.
            Example: {
                "2023": [0, 100],
                "2024": [100.0, 200]
            }
        """
        first_item = True
        try:
            percentage_amount = {}
            key_list = list(amount.keys())
            for i in range(len(key_list)):
                key = key_list[i]
                if first_item:
                    percentage_amount[key] = 0
                    first_item = False
                else:
                    previous_key = key_list[i-1]
                    if amount[previous_key] == 0:
                        percentage_amount[key] = 0
                    else:
                        percentage_amount[key] = round((amount[key] - amount[previous_key]) / amount[previous_key] * 100, 1)
            
            df = pd.DataFrame.from_dict(percentage_amount, orient='index', columns=['percentage_amount'])

            df_amount = pd.DataFrame.from_dict(amount, orient='index', columns=['amount'])

            df_combined = pd.concat([df, df_amount], axis=1)

            result = df_combined.apply(lambda row: [row["percentage_amount"], row["amount"]], axis=1).to_dict()

            return result
        except Exception as e:
            print("Error in _calculate_percentage_amount: ", e)
            return {}
