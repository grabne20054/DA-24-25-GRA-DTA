from DataAnalysis.preprocessing.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from collections import Counter
import pandas as pd
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
        self.roleshandler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/roles")

    def collect(self, handler=None) -> list:
        """
        Collects data from the API

        Returns:
            list: List of dictionaries containing the data
        """
        if handler is None:
            handler = self.handler
        try:
            return handler.start()
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
        roles = self.collect(self.roleshandler)
        if data == None or roles == None:
            raise Exception("No data found")

        employees_df = pd.DataFrame(data)
        roles_df = pd.DataFrame(roles)

        merged_df = pd.concat([employees_df, roles_df], axis=1)

        merged_df["role"] = merged_df["roleId"].map(roles_df.set_index("id")["name"])
        employees = dict(Counter(merged_df["role"]))

        if employees == {}:
            raise Exception("No Employees found")

        result = {role: count for role, count in employees.items()}
        result["typeofgraph"] = TYPEOFGRAPH
        return result



    def report(self):
        pass