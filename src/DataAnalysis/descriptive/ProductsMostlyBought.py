from DataAnalysis.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from datetime import datetime, timedelta
from os import getenv

from dotenv import load_dotenv
load_dotenv()

class ProductsMostlyBought(DescriptiveAnalysis):
    """ Products Mostly Bought
    """
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/ordersProducts")
        self.productshandler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/products")
        self.ordershandler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/orders")
    
    def collect(self) -> list:
        """
        Collects data from the API

        Returns:
            list: List of dictionaries containing the data
        """
        return self.handler.start()
    
    def perform(self, last_days: int = 0, year: bool = False, month: bool = False ) -> dict:
        """
        Perform the analysis
        
        Args:

            last_days (int, optional): Number of days to consider. Defaults to 0.
            year (bool, optional): If True, returns the purchases of the current year. Defaults to False.
            month (bool, optional): If True, returns purchases of the current month. Defaults to False.

        Returns:
            dict: Dictionary containing the products mostly bought
        """
        data = self.collect()

        if year:
            return self._setYearlyPurchases(data)
        elif month:
            return self._setMonthlyPurchases(data)
        else:
            return self._setPurchasesByDays(data, last_days)


    def _getProductNameById(self, product_id: int) -> str:
        """
        Gets the product name from the product ID

        Args:
            product_id (int): Product ID

        Returns:
            str: Product name
        """
        products = self.productshandler.start()

        for i in products:
            if i['productId'] == product_id:
                return i['name']
        
        return None
    
    def _getOrderDate(self, order_id: int) -> str:

        for i in self.ordershandler.start():
            if i['orderId'] == order_id:
                return i['orderDate']
        
        return None

    def _setYearlyPurchases(self, data: list) -> dict:
        products_bought = {}
        seen = set()
        for i in data:
            if datetime.strptime(self._getOrderDate(i['orderId']), "%Y-%m-%dT%H:%M:%S.%f").year == datetime.now().year:
                if i['productId'] not in seen:
                    products_bought[self._getProductNameById(i['productId'])] = i['productAmount']
                    seen.add(i['productId'])
                else:
                    products_bought[self._getProductNameById(i['productId'])] += i['productAmount']

        return products_bought
    
    def _setMonthlyPurchases(self, data: list) -> dict:
        products_bought = {}
        seen = set()
        for i in data:
            if datetime.strptime(self._getOrderDate(i['orderId']), "%Y-%m-%dT%H:%M:%S.%f").month == datetime.now().month:
                if i['productId'] not in seen:
                    products_bought[self._getProductNameById(i['productId'])] = i['productAmount']
                    seen.add(i['productId'])
                else:
                    products_bought[self._getProductNameById(i['productId'])] += i['productAmount']

        return products_bought
    
    def _setPurchasesByDays(self, data: list, last_days: int) -> dict:
        products_bought = {}
        seen = set()
        for i in data:
            if last_days > 0:
                if datetime.strptime(self._getOrderDate(i['orderId']), "%Y-%m-%dT%H:%M:%S.%f") >= datetime.now() - timedelta(days=last_days):
                    if i['productId'] not in seen:
                        products_bought[self._getProductNameById(i['productId'])] = i['productAmount']
                        seen.add(i['productId'])
                    else:
                        products_bought[self._getProductNameById(i['productId'])] += i['productAmount']
            elif last_days == 0:
                if i['productId'] not in seen:
                    products_bought[self._getProductNameById(i['productId'])] = i['productAmount']
                    seen.add(i['productId'])
                else:
                    products_bought[self._getProductNameById(i['productId'])] += i['productAmount']

            else: 
                return None # error handling

        return products_bought
    
    

    def report(self):
        pass