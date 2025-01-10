import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataAnalysis.diagnostic.ProductOrdersCorrelation import ProductOrdersCorrelation
import plotly.graph_objects as go
from tkinter import Tk, Scale, HORIZONTAL, Label
import matplotlib.pyplot as plt

if __name__ == "__main__":
    analysis = ProductOrdersCorrelation()
    price_correlation, date_correlation, user_correlation = analysis.perform()
    
    print("Price Correlation: ", price_correlation)

    new_cor = analysis.getChangingPriceOrdersCorrValue(1, 0)
    print("Price Correlation: ", new_cor)



    