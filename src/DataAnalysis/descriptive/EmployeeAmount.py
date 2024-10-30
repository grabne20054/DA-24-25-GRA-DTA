from DataAnalysis.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from collections import Counter

class EmployeeAmount(DescriptiveAnalysis):
    """ Amount of Employees by Role
    """
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/employees")

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
            dict: Dictionary containing the roles and the amount of employees
        """
        data = self.collect()

        employees = Counter([i['role'] for i in data])

        return {role: count for role, count in employees.items()}



    def report(self):
        pass