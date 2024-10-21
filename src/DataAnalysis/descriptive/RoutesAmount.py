from DataAnalysis.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis

class RoutesAmount(DescriptiveAnalysis):
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/routesOrders")
    
    def collect(self):
        return self.handler.start()
    
    def perform(self):
        data = self.collect()

        routes = {}
        seen = set()

        for i in data:
            if i['routeId'] not in seen:
                routes[i['routeId']] = 1
                seen.add(i['routeId'])
            else:
                routes[i['routeId']] += 1

        return routes

    def report(self):
        pass