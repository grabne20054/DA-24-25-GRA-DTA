import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataAnalysis.predictive.PredictiveEngine.DataPredictor.GrowthModel import GrowthModel
from DataAnalysis.descriptive.CustomerSignup import CustomerSignup
from DataAnalysis.descriptive.OrdersAmount import OrdersAmount
from DataAnalysis.predictive.RouteClassifier.ClassifierModel import ClassifierModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from threading import Thread
import time

from DataAnalysis.predictive.dependencies import OPTIONS, MONTHLY_OPTIONS
class ModelOptimizer:
    def __init__(self):
        self.customerGrowth = GrowthModel("CustomerGrowth", "growth", data_source=CustomerSignup())
        self.ordersGrowth = GrowthModel("OrdersGrowth", "growth", data_source=OrdersAmount())

        self.customerGrowthMonthly = GrowthModel("CustomerGrowthMonthly", "growth", data_source=CustomerSignup(), month=True)
        self.ordersGrowthMonthly = GrowthModel("OrdersGrowthMonthly", "growth", data_source=OrdersAmount(), month=True)
        
    def spawn_optimizer(self):
        for model in [self.customerGrowth, self.ordersGrowth, self.customerGrowthMonthly, self.ordersGrowthMonthly]:
            t = Thread(target=model.perform, args=(MONTHLY_OPTIONS if model.month else OPTIONS, model))
            t.start()
    
    def spawn_classifier_optimizer(self):
        classifier_model = ClassifierModel()
        classifier_model.perform()


if __name__ == "__main__":
    while True:
        try:
            optimizer = ModelOptimizer()
            optimizer.spawn_optimizer()
            optimizer.spawn_classifier_optimizer()

        except Exception as e:
            logger.error(f"Error occurred: {e}")
        finally:
            time.sleep(60 * 60 * 24)