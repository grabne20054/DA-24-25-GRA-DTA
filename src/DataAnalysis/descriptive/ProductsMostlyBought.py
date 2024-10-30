from DataAnalysis.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis

class ProductsMostlyBought(DescriptiveAnalysis):
    """ Products Mostly Bought
    """
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/ordersProducts")
    
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
            dict: Dictionary containing the products and the amount
        """
        data = self.collect()

        products_bought = {}
        seen = set()

        for i in data:
            if i['productId'] not in seen:
                products_bought[i['productId']] = i['productAmount']
                seen.add(i['productId'])
            else:
                products_bought[i['productId']] += i['productAmount']

        return products_bought


        

    def report(self):
        pass