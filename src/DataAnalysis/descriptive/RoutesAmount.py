from DataAnalysis.db.models.RoutesAmount import RoutesAmountRepository
from DataAnalysis.DataCollector import DataCollector
from DataAnalysis.db.models.queryparams import RoutesAmount as RoutesAmountParams
from os import getenv

from dotenv import load_dotenv
load_dotenv()

TYPEOFGRAPH = "bar"

class RoutesAmount(DataCollector):
    """ Amount of Routes
    """
    def __init__(self) -> None:
        super().__init__()
    
    def collect(self, limit: int) -> list[RoutesAmountParams]:
        """
        Collects data from the API

        Returns:
            list: List of dictionaries containing the data
        """
        try:
            return RoutesAmountRepository(self.db, limit=limit).get()
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
        data = self.collect(limit=limit)
        if data == None:
            raise Exception("No data found")
        
        if limit < 0:
            raise Exception("Limit cannot be negative")
        
        if limit > self._getLenghtUniqueRoutesWithOrders(data):
            raise Exception("Limit is greater than the amount of routes with orders are present")
        
        routes = {}
        
        for i in data:
            routes[i.name] = i.order_count

        return { "routes" : routes, "typeofgraph" : TYPEOFGRAPH }

    def _getLenghtUniqueRoutesWithOrders(self, data: list[RoutesAmountParams]) -> dict:
        """
        Gets the unique routes with orders

        Args:
            data (list): List of dictionaries containing the data

        Returns:
            int: Amount of unique routes with orders
        """

        seen = set()

        for i in data:
            uuid = i.name
            if uuid not in seen:
                seen.add(uuid)
            else:
                continue
            
        return len(seen)