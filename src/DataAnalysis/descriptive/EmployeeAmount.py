from DataAnalysis.APIDataHandlerFactory import APIDataHandlerFactory
from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from collections import Counter

class EmployeeAmount(DescriptiveAnalysis):
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/employees")

    def collect(self):
        return self.handler.start()
    
    def perform(self):
        data = self.collect()

        employees = Counter([i['role'] for i in data])

        return {role: count for role, count in employees.items()}



    def report(self):
        pass