from DataAnalysis.diagnostic.DiagnosticAnalysis import DiagnosticAnalysis
from DataAnalysis.preprocessing.APIDataHandlerFactory import APIDataHandlerFactory
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from itertools import combinations
from collections import defaultdict
from typing import Tuple
from os import getenv

from dotenv import load_dotenv
load_dotenv()

class ItemBoughtCorrelation(DiagnosticAnalysis):
    """
    Class for analyzing the correlation between items bought by customers"""
    def __init__(self) -> None:
        self.ordershandler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/orders")
        self.ordersProductshandler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/ordersProducts")
        self.productshandler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/products")


    def collect(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Collects data from the API

        Returns:
            tuple: Tuple of dataframes containing the data
        """
        try:
            orders = self.ordershandler.start()
            ordersProducts = self.ordersProductshandler.start()
            products = self.productshandler.start()
        except Exception as e:
            print("Error: ", e)
            return None, None, None

        df_orders = pd.DataFrame(orders)
        df_ordersProducts = pd.DataFrame(ordersProducts)
        df_products = pd.DataFrame(products)

        return df_orders, df_ordersProducts, df_products

    def perform(self, productId: str, combination_product_amount: int = 2) -> list[str]:
        """
        Perform the analysis
        
        Args:
            productId (str): Product ID to analyze
            combination_product_amount (int, optional): Amount of products to combine. Defaults to 2.
            
            Returns:
                list: list containing the products      
        """

        if combination_product_amount < 1:
            raise ValueError("Not enough products to combine")

        df_orders, df_ordersProducts, df_products= self.collect()
        if df_orders is None or df_ordersProducts is None or df_products is None:
            raise Exception("No data found")
        elif df_orders.empty or df_ordersProducts.empty or df_products.empty:
            raise Exception("One or more dataframes are empty")

        try:
            df_orders = pd.merge(df_orders, df_ordersProducts, on='orderId')
            df_orders = pd.merge(df_orders, df_products, on='productId')
        except Exception as e:
            raise Exception("Error in merging dataframes")
        
        columns_to_drop = ['description', 'deliveryDate', 'deleted_x', 'customerReference', 'imagePath', 'deleted_y', 'stock', 'orderDate', 'name', 'price', 'productAmount', 'selfCollect', 'orderDate_x', 'orderDate_y', 'createdAt', 'orderState']
        
        df_orders = df_orders.drop(columns=df_orders.columns.intersection(columns_to_drop))
        
        if combination_product_amount > len(df_orders['productId'].unique()):
            raise ValueError("Too many products to combine")


        pivot_df = pd.crosstab(df_orders['orderId'], df_orders['productId'])
        product_correlation = np.dot(pivot_df.T, pivot_df)
        np.fill_diagonal(product_correlation, 0)


        correlation_df = pd.DataFrame(product_correlation, index=pivot_df.columns, columns=pivot_df.columns)

        try:
            product_id = df_products.loc[df_products['productId'] == productId, 'productId'].values[0]
        except ValueError as e:
            raise ValueError("Product not found")
        except IndexError as e:
            raise IndexError("Product not found")
        
        products =  correlation_df.loc[product_id].nlargest(combination_product_amount).index.to_list()

        return {"products": products}
    
    def report():
        pass