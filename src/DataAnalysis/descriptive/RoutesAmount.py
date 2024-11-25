from DataAnalysis.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from os import getenv

from dotenv import load_dotenv
load_dotenv()

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
    
    def perform(self) -> dict:
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
        
        Raises:
            Exception: Route not found
        """
        routes = self.routeshandler.start()

        for i in routes:
            if i['routeId'] == route_id:
                return i['name']
        
        raise Exception("Route not found")