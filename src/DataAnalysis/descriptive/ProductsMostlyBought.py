from DataAnalysis.preprocessing.APIDataHandlerFactory import APIDataHandlerFactory
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
        try:
            return self.handler.start()
        except ConnectionRefusedError as e:
            print("Connection refused: ", e)

        except ConnectionError as e:
            print("Connection error: ", e)
        except Exception as e:
            print("Error: ", e)
    
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
        if data == None:
            raise Exception("No data found")

        if year:
            return self._getYearlyPurchases(data)
        elif month:
            return self._getMonthlyPurchases(data)
        else:
            return self._getPurchasesByDays(data, last_days)


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
    
    def _getOrderDate(self, order_id: int) -> str:
        """
        Gets the order date from the order ID

        Args:
            order_id (int): Order ID

        Returns:
            str: Order date

        Raises:
            Exception: Order not found
        """
        for i in self.ordershandler.start():
            if i['orderId'] == order_id:
                return i['orderDate']
        
        raise Exception("Order not found")

    def _getYearlyPurchases(self, data: list) -> dict:
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
            if datetime.strptime(self._getOrderDate(i['orderId']), "%Y-%m-%dT%H:%M:%S.%f").year == datetime.now().year:
                if i['productId'] not in seen:
                    products_bought[self._getProductNameById(i['productId'])] = i['productAmount']
                    seen.add(i['productId'])
                else:
                    products_bought[self._getProductNameById(i['productId'])] += i['productAmount']

        return products_bought
    
    def _getMonthlyPurchases(self, data: list) -> dict:
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
            if datetime.strptime(self._getOrderDate(i['orderId']), "%Y-%m-%dT%H:%M:%S.%f").month == self._getCurrentMonth():
                if i['productId'] not in seen:
                    products_bought[self._getProductNameById(i['productId'])] = i['productAmount']
                    seen.add(i['productId'])
                else:
                    products_bought[self._getProductNameById(i['productId'])] += i['productAmount']

        return products_bought
    
    def _getPurchasesByDays(self, data: list, last_days: int) -> dict:
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
        
        products_bought = {}
        seen = set()
        for i in data:
            if last_days > 0:
                if (datetime.strptime(self._getOrderDate(i['orderId']), "%Y-%m-%dT%H:%M:%S.%f") >= datetime.now() - timedelta(days=last_days)) and (datetime.strptime(self._getOrderDate(i['orderId']), "%Y-%m-%dT%H:%M:%S.%f") <= datetime.now()):
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
            elif last_days < 0:
                raise ValueError("The number of days should be greater than zero")

        return products_bought
    
    def _getCurrentMonth(self) -> int:
        """
        Gets the current month

        Returns:
            int: Current month
        """
        return datetime.now().month
    

    def report(self):
        pass