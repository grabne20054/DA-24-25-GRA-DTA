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

from DataAnalysis.predictive.dependencies import OPTIONS
class ModelOptimizer:
    def __init__(self):
        self.customerGrowth = GrowthModel("CustomerGrowth", "growth", data_source=CustomerSignup())
        self.ordersGrowth = GrowthModel("OrdersGrowth", "growth", data_source=OrdersAmount())

    
    def spawn_optimizer(self):
        for model in [self.customerGrowth, self.ordersGrowth]:
            t = Thread(target=model.perform, args=(OPTIONS, model))
            t.start()


if __name__ == "__main__":
    while True:
        try:
            ModelOptimizer().spawn_optimizer()
        except Exception as e:
            logger.error(f"Error occurred: {e}")
        finally:
            time.sleep(60 * 60 * 24)