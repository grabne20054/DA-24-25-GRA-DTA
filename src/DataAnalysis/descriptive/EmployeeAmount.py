from DataAnalysis.preprocessing.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from collections import Counter
from os import getenv

from dotenv import load_dotenv
load_dotenv()

TYPEOFGRAPH = "bar"
############# DEPRECATED ######################

class EmployeeAmount(DescriptiveAnalysis):
    """ Amount of Employees by Role
    """
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/employees")

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
            dict: Dictionary containing the roles and the amount of employees
        """
        data = self.collect()
        if data == None:
            raise Exception("No data found")

        employees = Counter([i['role'] for i in data])

        if employees == {}:
            raise Exception("No Employees found")

        result = {role: count for role, count in employees.items()}
        result["typeofgraph"] = TYPEOFGRAPH
        return result



    def report(self):
        pass