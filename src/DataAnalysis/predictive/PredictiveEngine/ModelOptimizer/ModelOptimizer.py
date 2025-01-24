from DataAnalysis.predictive.GrowthModel import GrowthModel
from DataAnalysis.descriptive.CustomerSignup import CustomerSignup
from DataAnalysis.descriptive.OrdersAmount import OrdersAmount



from threading import Thread



class ModelOptimizer:
    def __init__(self):
        self.customerGrowth = GrowthModel("CustomerGrowth", "growth", data_source=CustomerSignup())
        self.cumulativeCustomerGrowth = GrowthModel("CumulativeCustomerGrowth", "cumulative_growth", data_source=CustomerSignup())
        #self.ordersGrowth = OrdersGrowth()
        #self.cumulativeOrdersGrowth = CumulativeOrdersGrowth()
    
    def spawn_optimizer(self):
        for i in [self.customerGrowth, self.cumulativeCustomerGrowth]:
            t = Thread(target=i.perform)
            t.start()


if __name__ == "__main__":
    ModelOptimizer().spawn_optimizer()