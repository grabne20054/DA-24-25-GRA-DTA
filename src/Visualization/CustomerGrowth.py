import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataAnalysis.predictive.CustomerGrowth.CustomerGrowth import CustomerGrowth

if __name__ == "__main__":
    cg = CustomerGrowth()
    cg.perform(128, 0.0, 1e-4, 1000, 0.0001, 20, 10)
