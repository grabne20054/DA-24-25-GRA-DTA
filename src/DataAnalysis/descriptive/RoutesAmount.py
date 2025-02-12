from DataAnalysis.preprocessing.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from os import getenv

from dotenv import load_dotenv
load_dotenv()

TYPEOFGRAPH = "bar"

class RoutesAmount(DescriptiveAnalysis):
    """ Amount of Routes
    """
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/routesOrders")
        self.routeshandler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/routes")
    
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
    
    def perform(self, limit: int = 5) -> dict:
        """
        Perform the analysis

        Returns:
            dict: Dictionary containing the routes and the amount
        
        Raises:
            Exception: No data found
        """
        data = self.collect()
        if data == None:
            raise Exception("No data found")
        
        if limit < 0:
            raise Exception("Limit cannot be negative")
        
        if limit > self._getLenghtUniqueRoutesWithOrders(data):
            raise Exception("Limit is greater than the amount of routes with orders are present")
        
        routes = {}
        seen = set()

        for i in data:
            uuid = i['routeId']
            if uuid not in seen:
                routes[uuid] = 1
                seen.add(uuid)
            else:
                routes[uuid] += 1

        sorted_routes = dict(sorted(routes.items(), key=lambda item: item[1], reverse=True))
        
        if limit > 0:
            sorted_routes = dict(list(sorted_routes.items())[:limit])
        else:
            sorted_routes = dict(list(sorted_routes.items()))
        
        sorted_routes_with_names = {}
        for i in sorted_routes:
            route_name = self._getRouteNameById(i)
            sorted_routes_with_names[route_name] = sorted_routes[i]
            
        return { "routes" : sorted_routes_with_names, "typeofgraph" : TYPEOFGRAPH }

    def report(self):
        pass

    def _getRouteNameById(self, route_id: str) -> str:
        """
        Gets the route name from the route ID

        Args:
            route_id (str): Route ID

        Returns:
            str: Route name
        
        Raises:
            Exception: Route not found
        """
        routes = self.routeshandler.start()

        for i in routes:
            if i['routeId'] == route_id:
                return i['name']
        
        raise Exception("Route not found")
    
    def _getLenghtUniqueRoutesWithOrders(self, data: list) -> dict:
        """
        Gets the unique routes with orders

        Args:
            data (list): List of dictionaries containing the data

        Returns:
            int: Amount of unique routes with orders
        """

        seen = set()

        for i in data:
            uuid = i['routeId']
            if uuid not in seen:
                seen.add(uuid)
            else:
                continue

        print(len(seen))
        return len(seen)