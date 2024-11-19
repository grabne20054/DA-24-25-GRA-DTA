import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataAnalysis.descriptive.ProductsMostlyBought import ProductsMostlyBought
from matplotlib import pyplot as plt

if __name__ == "__main__":
    products_mostly_bought = ProductsMostlyBought()
    data = products_mostly_bought.perform(last_days=30)

    plt.bar(data.keys(), data.values())
    plt.show()