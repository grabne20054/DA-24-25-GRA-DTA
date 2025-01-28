import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from GrowthModel import GrowthModel
from descriptive.CustomerSignup import CustomerSignup
from descriptive.OrdersAmount import OrdersAmount

from threading import Thread

class ModelOptimizer:
    def __init__(self):
        self.customerGrowth = GrowthModel("CustomerGrowth", "growth", data_source=CustomerSignup())
        self.cumulativeCustomerGrowth = GrowthModel("CumulativeCustomerGrowth", "cumulative_growth", data_source=CustomerSignup())
        self.ordersGrowth = GrowthModel("OrdersGrowth", "growth", data_source=OrdersAmount())
        self.cumulativeOrdersGrowth = GrowthModel("CumulativeOrdersGrowth", "cumulative_growth", data_source=OrdersAmount())
    
    def spawn_optimizer(self):
        for i in [self.customerGrowth, self.cumulativeCustomerGrowth, self.ordersGrowth, self.cumulativeOrdersGrowth]:
            t = Thread(target=i.perform)
            t.start()


if __name__ == "__main__":
    ModelOptimizer().spawn_optimizer()