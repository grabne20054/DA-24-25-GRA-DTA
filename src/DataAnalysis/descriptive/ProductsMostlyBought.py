from DataAnalysis.preprocessing.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from datetime import datetime, timedelta
from os import getenv

from dotenv import load_dotenv
load_dotenv()

TYPEOFGRAPH = "bar"

class ProductsMostlyBought(DescriptiveAnalysis):
    """ Products Mostly Bought
    """
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/ordersProducts")
        self.productshandler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/products")
    
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
    
    def perform(self, last_days: int = 0, year: bool = False, month: bool = False, limit: int = 5) -> dict:
        """
        Perform the analysis
        
        Args:

            last_days (int, optional): Number of days to consider. Defaults to 0.
            year (bool, optional): If True, returns the purchases of the current year. Defaults to False.
            month (bool, optional): If True, returns purchases of the current month. Defaults to False.
            limit (int, optional): Limit of products to be shown. Defaults to 5.

        Returns:
            dict: Dictionary containing the products mostly bought
        """
        data = self.collect()
        if data == None:
            raise Exception("No data found")
        
        if limit > len(data):
            raise Exception("Limit is greater than the amount of bought products present")
        
        if limit < 0:
            raise Exception("Limit cannot be negative")

        if year:
            return self._getYearlyPurchases(data, limit)
        elif month:
            return self._getMonthlyPurchases(data, limit)
        else:
            return self._getPurchasesByDays(data, last_days, limit)


    def _getProductNameById(self, product_id: int) -> str:
        """
        Gets the product name from the product ID

        Args:
            product_id (int): Product ID

        Returns:
            str: Product name

        Raises:
            Exception: Product not found
            Exception: Order not found
            ValueError: The number of days should be greater than zero
        """
        products = self.productshandler.start()

        for i in products:
            if i['productId'] == product_id:
                return i['name']
        
        raise Exception("Product not found")

    def _getYearlyPurchases(self, data: list, limit) -> dict:
        """
        gets the yearly purchases of the products
        
        Args:
            data (list): List of dictionaries containing the data
            
        Returns:
            dict: Dictionary containing the products mostly bought

        Raises:
            ValueError: The number of days should be greater than zero
        """
        
        products_bought = {}
        seen = set()
        for i in data:
            if datetime.strptime(i['orderDate'], "%Y-%m-%dT%H:%M:%S.%f").year == datetime.now().year:
                if i['productId'] not in seen:
                    products_bought[i['productId']] = i['productAmount']
                    seen.add(i['productId'])
                else:
                    products_bought[i['productId']] += i['productAmount']

        products_bought = dict(list(sorted(products_bought.items(), key=lambda item: item[1], reverse=True))[:limit])

        products_bought_named = {}
        for i in products_bought.keys():
            product_name = self._getProductNameById(i)
            products_bought_named[product_name] = products_bought[i]
        products_bought = products_bought_named

        return {"products" : products_bought, "typeofgraph" : TYPEOFGRAPH}
    
    def _getMonthlyPurchases(self, data: list, limit) -> dict:
        """
        gets the monthly purchases of the products

        Args:
            data (list): List of dictionaries containing the data

        Returns:
            dict: Dictionary containing the products mostly bought
        """

        products_bought = {}
        seen = set()
        for i in data:
            if datetime.strptime(i['orderDate'], "%Y-%m-%dT%H:%M:%S.%f").month == self._getCurrentMonth() and datetime.strptime(i['orderDate'], "%Y-%m-%dT%H:%M:%S.%f").year == datetime.now().year:
                if i['productId'] not in seen:
                    products_bought[i['productId']] = i['productAmount']
                    seen.add(i['productId'])
                else:
                    products_bought[i['productId']] += i['productAmount']

        products_bought = dict(list(sorted(products_bought.items(), key=lambda item: item[1], reverse=True))[:limit])

        products_bought_named = {}
        for i in products_bought.keys():
            product_name = self._getProductNameById(i)
            products_bought_named[product_name] = products_bought[i]
        products_bought = products_bought_named

        return {"products" : products_bought, "typeofgraph" : TYPEOFGRAPH}
    
    def _getPurchasesByDays(self, data: list, last_days: int, limit) -> dict:
        """
        gets the purchases of the products by the number of days

        Args:
            data (list): List of dictionaries containing the data
            last_days (int): Number of days to consider

        Returns:
            dict: Dictionary containing the products mostly bought
        
        Raises:
            ValueError: If the number of days is less than zero
        """

        if limit > len(data):
            raise Exception("Limit is greater than the amount of bought products present")
        
        if limit < 0:
            raise Exception("Limit cannot be negative")
        
        if limit == 0:
            limit = len(data)
        
        products_bought = {}
        seen = set()
        for i in data:
            if last_days > 0:
                if datetime.strptime(i['orderDate'], "%Y-%m-%dT%H:%M:%S.%f") >= datetime.now() - timedelta(days=last_days) and datetime.strptime(i['orderDate'], "%Y-%m-%dT%H:%M:%S.%f") <= datetime.now():
                    if i['productId'] not in seen:
                        products_bought[i['productId']] = i['productAmount']
                        seen.add(i['productId'])
                    else:
                        products_bought[i['productId']] += i['productAmount']
            elif last_days == 0:
                if i['productId'] not in seen:
                    products_bought[i['productId']] = i['productAmount']
                    seen.add(i['productId'])
                else:
                    products_bought[i['productId']] += i['productAmount']
            elif last_days < 0:
                raise ValueError("The number of days should be greater than zero")
            
        products_bought = dict(list(sorted(products_bought.items(), key=lambda item: item[1], reverse=True))[:limit])

        products_bought_named = {}
        for i in products_bought.keys():
            product_name = self._getProductNameById(i)
            products_bought_named[product_name] = products_bought[i]
        products_bought = products_bought_named

        return {"products" : products_bought, "typeofgraph" : TYPEOFGRAPH}
    
    def _getCurrentMonth(self) -> int:
        """
        Gets the current month

        Returns:
            int: Current month
        """
        return datetime.now().month
    

    def report(self):
        pass