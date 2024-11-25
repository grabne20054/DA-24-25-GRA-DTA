from DataAnalysis.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis

from os import getenv

from dotenv import load_dotenv
load_dotenv()

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
    
    def perform(self) -> dict:
        """
        Perform the analysis

        Returns:
            dict: Dictionary containing the products and the stock
        """
        data = self.collect()
        if data == None:
            raise Exception("No data found")

        products = {}

        for i in data:    
            products[i['name']] = i['stock']

        return products



    def report(self):
        pass