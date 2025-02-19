import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataAnalysis.predictive.PredictiveEngine.ModelOptimizer.GrowthModel import GrowthModel
from DataAnalysis.descriptive.CustomerSignup import CustomerSignup
from DataAnalysis.descriptive.OrdersAmount import OrdersAmount

from threading import Thread
import time

OPTIONS = {"one_day": {"lag": 2, "sequence_lenght": 5, "rolling_mean": 3}, "seven_days": {"lag": 3, "sequence_lenght": 7, "rolling_mean": 7}, "month": {"lag": 7, "sequence_lenght": 15, "rolling_mean": 14}, "year": {"lag": 30, "sequence_lenght": 60, "rolling_mean": 30}}

class ModelOptimizer:
    def __init__(self):
        self.customerGrowth = GrowthModel("CustomerGrowth", "growth", data_source=CustomerSignup())
        self.cumulativeCustomerGrowth = GrowthModel("CumulativeCustomerGrowth", "cumulative_growth", data_source=CustomerSignup())
        self.ordersGrowth = GrowthModel("OrdersGrowth", "growth", data_source=OrdersAmount())
        self.cumulativeOrdersGrowth = GrowthModel("CumulativeOrdersGrowth", "cumulative_growth", data_source=OrdersAmount())
    
    def spawn_optimizer(self):
        for option_key in OPTIONS.keys():
            for model in [self.customerGrowth, self.cumulativeCustomerGrowth, self.ordersGrowth, self.cumulativeOrdersGrowth]:
                t = Thread(target=model.perform, args=(OPTIONS[option_key]["lag"], OPTIONS[option_key]["rolling_mean"], OPTIONS[option_key]["sequence_lenght"]))
                t.start()
                print("Spawned thread for ", model, " with option ", option_key)
if __name__ == "__main__":
    while True:
        try:
            ModelOptimizer().spawn_optimizer()
            time.sleep(60*60*24)
        except Exception as e:
            print(f"Error occured: {e}")