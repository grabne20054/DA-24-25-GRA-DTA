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

    def collect(self) -> list:
        """
        Collects data from the API

        Returns:
            list: List of dictionaries containing the data
        """
        try:
            return EmployeeAmountRepository(self.db).get(), EmployeeAmountRepository(self.db).getRoles()
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
        data, roles = self.collect()
        if data == None or roles == None:
            raise Exception("No data found")

        employees_df = pd.DataFrame([i.__dict__ for i in data], columns=["roleId"])
        roles_df = pd.DataFrame([i.__dict__ for i in roles], columns=["id", "name"])

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