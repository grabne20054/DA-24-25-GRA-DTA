from DataAnalysis.DataCollector import DataCollector
from DataAnalysis.db.models.ItemBoughtCorrelation import ItemBoughtCorrelationRepository
import pandas as pd
import numpy as np
from uuid import UUID
from typing import Tuple
from os import getenv

from dotenv import load_dotenv
load_dotenv()

class ItemBoughtCorrelation(DataCollector):
    """
    Class for analyzing the correlation between items bought by customers"""
    def __init__(self) -> None:
        super().__init__()

    def collect(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Collects data from the DB

        Returns:
            tuple: Tuple of dataframes containing the data
        """
        try:
            products, ordersProducts, orders = ItemBoughtCorrelationRepository(self.db).getAll()
        except Exception as e:
            print("Error: ", e)
            return None, None, None
        
        df_orders = pd.DataFrame([i.orderId for i in orders], columns=['orderId'])

        df_ordersProducts = pd.DataFrame(ordersProducts, columns=['orderId', 'productId', 'productAmount', 'orderDate'])
        df_ordersProducts = df_ordersProducts.drop(columns=['orderDate', 'productAmount'])

        df_products = pd.DataFrame([i.productId for i in products], columns=['productId'])

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
        
        if combination_product_amount > len(df_orders['productId'].unique()):
            raise ValueError("Too many products to combine")


        pivot_df = pd.crosstab(df_orders['orderId'], df_orders['productId'])
        product_correlation = np.dot(pivot_df.T, pivot_df)
        np.fill_diagonal(product_correlation, 0)

        correlation_df = pd.DataFrame(product_correlation, index=pivot_df.columns, columns=pivot_df.columns)
    
        try:
            product_id = df_products.loc[df_products['productId'] == UUID(productId), 'productId'].values[0]
            print(f"Product ID: {product_id}")
        except ValueError as e:
            raise ValueError("Product not found")
        except IndexError as e:
            raise IndexError("Product not found")
        
        products =  correlation_df.loc[product_id].nlargest(combination_product_amount).index.to_list()

        return {"products": products}
    
    def report():
        pass