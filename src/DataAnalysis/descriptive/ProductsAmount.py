from DataAnalysis.preprocessing.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis

from os import getenv

from dotenv import load_dotenv
load_dotenv()

TYPEOFGRAPH = "bar"

class ProductsAmount(DescriptiveAnalysis):
    """ Amount of Products
    """
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/products")

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
    
    def perform(self, limit: int) -> dict:
        """
        Perform the analysis

        Args:
            limit (int): Limit of products to be shown
        
        Raises:
            Exception: If no data is found
            Exception: If the limit is greater than the amount of products present
            Exception: If the limit is negative

        Returns:
            dict: Dictionary containing the products and the stock
        """
        data = self.collect()
        if data == None:
            raise Exception("No data found")

        if limit > len(data):
            raise Exception("Limit is greater than the amount of products present")

        if limit < 0:
            raise Exception("Limit cannot be negative")
        
        if limit == 0:
            limit = len(data)

        products = {}

        for i in data:    
            products[i['name']] = i['stock']

        products = dict(sorted(products.items(), key=lambda item: item[1], reverse=True)[:limit])

        return { "products" : products, "typeofgraph" : TYPEOFGRAPH }



    def report(self):
        pass