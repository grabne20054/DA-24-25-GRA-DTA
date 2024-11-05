from DataAnalysis.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis

class RoutesAmount(DescriptiveAnalysis):
    """ Amount of Routes
    """
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/routesOrders")
        self.routeshandler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/routes")
    
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
            dict: Dictionary containing the routes and the amount
        """
        data = self.collect()

        routes = {}
        seen = set()

        for i in data:
            if i['routeId'] not in seen:
                routes[self._getRouteNameById(i['routeId'])] = 1
                seen.add(i['routeId'])
            else:
                routes[self._getRouteNameById(i['routeId'])] += 1

        return routes

    def report(self):
        pass

    def _getRouteNameById(self, route_id: int) -> str:
        """
        Gets the route name from the route ID

        Args:
            route_id (int): Route ID

        Returns:
            str: Route name
        """
        routes = self.routeshandler.start()

        for i in routes:
            if i['routeId'] == route_id:
                return i['name']
        
        return None