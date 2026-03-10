from DataAnalysis.db.models.EmployeeAmount import EmployeeAmountRepository
from DataAnalysis.db.models.queryparams import EmployeeAmount as EmployeeAmountParams
from DataAnalysis.DataCollector import DataCollector
from collections import Counter
import pandas as pd
from os import getenv

from dotenv import load_dotenv
load_dotenv()

TYPEOFGRAPH = "bar"

class EmployeeAmount(DataCollector):
    """ Amount of Employees by Role
    """
    def __init__(self) -> None:
        super().__init__()

    def collect(self, limit: int) -> list[EmployeeAmountParams]:
        """
        Collects data from the API

        Returns:
            list: List of dictionaries containing the data
        """
        try:
            return EmployeeAmountRepository(self.db, limit=limit).get()
        except ConnectionRefusedError as e:
            print("Connection refused: ", e)
        except ConnectionError as e:
            print("Connection error: ", e)
        except Exception as e:
            print("Error: ", e)
    
    def perform(self, limit:int) -> dict:
        """
        Perform the analysis

        Returns:
            dict: Dictionary containing the roles and the amount of employees
        """
        data = self.collect(limit=limit)
        if data == None:
            raise Exception("No data found")

        result = {}

        for i in data:
            result[i.name] = i.employee_count
        result["typeofgraph"] = TYPEOFGRAPH

        return result



    def report(self):
        pass