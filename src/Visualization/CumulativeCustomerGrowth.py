import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataAnalysis.predictive.CustomerGrowth.CumulativeCustomerGrowthOptimizer import CumulativeCustomerGrowthOptimizer
from DataAnalysis.predictive.CustomerGrowth.CumulativeCustomerGrowth import CumulativeCustomerGrowth

if __name__ == "__main__":
    cg = CumulativeCustomerGrowth()
    cg.perform(128, 0.0, 1e-4, 1000, 0.0001, 20, 10)