from DataAnalysis.descriptive.DescriptiveAnalysis import DescriptiveAnalysis
from DataAnalysis.APIDataHandlerFactory import APIDataHandlerFactory

from datetime import datetime, timedelta


class CustomerSignup(DescriptiveAnalysis):
    def __init__(self) -> None:
        self.handler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/customers")

    def collect(self):
        return self.handler.start()
        
    def perform(self, last_days: int = 0):
        data = self.collect()

        customers = []
        dates = []
        
        data.sort(key=lambda i: datetime.strptime(i['signedUp'], "%Y-%m-%dT%H:%M:%S.%f")) # Sort by signedUp date)
        
        for i in data:
            should_append = True
            if last_days > 0:
                if datetime.strptime(i['signedUp'], "%Y-%m-%dT%H:%M:%S.%f") <= datetime.now() - timedelta(days=last_days):
                    should_append = False  # Don't append if date is older than last_days

            if should_append:
                i['signedUp'] = i['signedUp'].split("t")[0]
                customers.append(i['lastname'] + ", " + i['firstname'])
                dates.append(i['signedUp'])
        return customers, dates



    def report(self):
        pass