import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import matplotlib.pyplot as plt
from DataAnalysis.diagnostic.ItemBoughtCorrelation import ItemBoughtCorrelation

if __name__ == "__main__":
    analysis = ItemBoughtCorrelation()

    test = analysis.perform("product4", 5)
    print(test)
