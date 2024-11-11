from DataAnalysis.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis

class ProductsAmount(DescriptiveAnalysis):
    """ Amount of Products
    """
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/products")

    def collect(self) -> list:
        """
        Collects data from the API
        
        Returns:
            list: List of dictionaries containing the data
        """
        return self.handler.start()
    
    def perform(self) -> dict:
        """
        Perform the analysis

        Returns:
            dict: Dictionary containing the products and the stock
        """
        data = self.collect()

        products = {}

        for i in data:    
            products[i['name']] = i['stock']

        return products



    def report(self):
        pass