import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataAnalysis.descriptive.ProductsAmount import ProductsAmount
from matplotlib import pyplot as plt

if __name__ == "__main__":
    product_amount = ProductsAmount()
    data = product_amount.perform()

    plt.bar(data.keys(), data.values())
    plt.show()
    