from DataAnalysis.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis

class ProductsMostlyBought(DescriptiveAnalysis):
    """ Products Mostly Bought
    """
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/ordersProducts")
        self.productshandler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/products")
    
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
                products_bought[self._getProductNameById(i['productId'])] = i['productAmount']
                seen.add(i['productId'])
            else:
                products_bought[self._getProductNameById(i['productId'])] += i['productAmount']

        return products_bought


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

    def report(self):
        pass