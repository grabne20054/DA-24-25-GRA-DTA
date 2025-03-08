import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataAnalysis.predictive.PredictiveEngine.ModelOptimizer.ModelManager import ModelManager
from DataAnalysis.predictive.PredictiveEngine.ModelOptimizer.GrowthModel import GrowthModel
from DataAnalysis.descriptive.CustomerSignup import CustomerSignup
from DataAnalysis.descriptive.OrdersAmount import OrdersAmount

from threading import Thread
import time

OPTIONS = {"one_day": {"lag": 7, "sequence_lenght": 7, "rolling_mean": 3}, "seven_days": {"lag": 14, "sequence_lenght": 7, "rolling_mean": 7}, "month": {"lag": 6, "sequence_lenght": 1, "rolling_mean": 3}, "year": {"lag": 1, "sequence_lenght": 1, "rolling_mean": 1}}

class ModelOptimizer:
    def __init__(self):
        self.customerGrowth = GrowthModel("CustomerGrowth", "growth", data_source=CustomerSignup())
        self.ordersGrowth = GrowthModel("OrdersGrowth", "growth", data_source=OrdersAmount())
        self.model_manager = ModelManager()

    
    def spawn_optimizer(self):
        config = []
        month = False
        year = False

        for option_key in OPTIONS.keys():
            for model in [self.customerGrowth, self.ordersGrowth]:
                config.append((model.data_analysis, model.growthtype, option_key))
                if option_key == "month":
                    month = True
                elif option_key == "year":
                    year = True
                t = Thread(target=model.perform, args=(OPTIONS[option_key]["lag"], OPTIONS[option_key]["rolling_mean"], OPTIONS[option_key]["sequence_lenght"], month, year))
                t.start()
                print("Spawned thread for ", model, " with option ", option_key)
                month = False
                year = False


if __name__ == "__main__":
    while True:
        try:
            ModelOptimizer().spawn_optimizer()
            time.sleep(60*60*24)
        except Exception as e:
            print(f"Error occured: {e}")