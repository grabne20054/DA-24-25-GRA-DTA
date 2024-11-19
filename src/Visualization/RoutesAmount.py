import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataAnalysis.descriptive.RoutesAmount import RoutesAmount
from matplotlib import pyplot as plt

if __name__ == "__main__":
    routes_amounts = RoutesAmount()
    data = routes_amounts.perform()
    
    plt.bar(data.keys(), data.values())
    plt.show()