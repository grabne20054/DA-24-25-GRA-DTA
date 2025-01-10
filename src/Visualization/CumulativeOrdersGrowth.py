import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataAnalysis.predictive.OrdersGrowth.CumulativeOrdersGrowth import CumulativeOrdersGrowth

if __name__ == "__main__":
    cog = CumulativeOrdersGrowth()
    cog.perform(128, 0.0, 1e-4, 1000, 0.0001, 20, 10)