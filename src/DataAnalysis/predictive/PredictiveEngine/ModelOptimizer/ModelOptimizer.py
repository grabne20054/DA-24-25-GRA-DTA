import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataAnalysis.predictive.PredictiveEngine.ModelOptimizer.ModelManager import ModelManager
from DataAnalysis.predictive.PredictiveEngine.ModelOptimizer.GrowthModel import GrowthModel
from DataAnalysis.descriptive.CustomerSignup import CustomerSignup
from DataAnalysis.descriptive.OrdersAmount import OrdersAmount
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from threading import Thread
import time

OPTIONS = {"one_day": {"lag": 7, "sequence_lenght": 7, "rolling_mean": 3}, "seven_days": {"lag": 14, "sequence_lenght": 7, "rolling_mean": 7}, "month": {"lag": 6, "sequence_lenght": 1, "rolling_mean": 3}}
# year not supported yet
class ModelOptimizer:
    def __init__(self):
        self.customerGrowth = GrowthModel("CustomerGrowth", "growth", data_source=CustomerSignup())
        self.ordersGrowth = GrowthModel("OrdersGrowth", "growth", data_source=OrdersAmount())

    
    def spawn_optimizer(self):
        month = False
        year = False

        for option_key in OPTIONS.keys():
            for model in [self.customerGrowth, self.ordersGrowth]:
                if option_key == "month":
                    month = True
                elif option_key == "year":
                    year = True
                t = Thread(target=model.perform, args=(OPTIONS[option_key]["lag"],
                                                        OPTIONS[option_key]["rolling_mean"],
                                                          OPTIONS[option_key]["sequence_lenght"], month, year))
                t.start()
                logger.info(f"Spawned thread for {model} with option {option_key}")
                month = False
                year = False


if __name__ == "__main__":
    while True:
        try:
            ModelOptimizer().spawn_optimizer()
        except Exception as e:
            logger.error(f"Error occurred: {e}")
        finally:
            time.sleep(60 * 60 * 24)