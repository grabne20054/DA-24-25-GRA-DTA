from DataAnalysis.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis

class ProductsAmount(DescriptiveAnalysis):
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/products")

    def collect(self):
        return self.handler.start()
    
    def perform(self):
        data = self.collect()

        products = {}

        for i in data:    
            products[i['name']] = i['amount']

        return products



    def report(self):
        pass