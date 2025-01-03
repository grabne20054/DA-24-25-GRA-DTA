from DataAnalysis.diagnostic.DiagnosticAnalysis import DiagnosticAnalysis
from DataAnalysis.preprocessing.APIDataHandlerFactory import APIDataHandlerFactory
import pandas as pd
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

        # convert to dataframes
        df_orders = pd.DataFrame(orders)
        df_ordersProducts = pd.DataFrame(ordersProducts)
        df_products = pd.DataFrame(products)

        return df_orders, df_ordersProducts, df_products

    def perform(self, product_name: str, combination_product_amount: int = 2) -> list[str]:
        """
        Perform the analysis
        
        Args:
            product_name (str): Product name
            combination_product_amount (int, optional): Amount of products to combine. Defaults to 2.
            
            Returns:
                list[str]: List of product names        
        """

        df_orders, df_ordersProducts, df_products= self.collect()
        if df_orders is None or df_ordersProducts is None or df_products is None:
            raise Exception("No data found")
        elif df_orders.empty or df_ordersProducts.empty or df_products.empty:
            raise Exception("One or more dataframes are empty")

        # Merge the dataframes like a SQL join
        try:
            df_orders = pd.merge(df_orders, df_ordersProducts, on='orderId')
            df_orders = pd.merge(df_orders, df_products, on='productId')
        except Exception as e:
            print("Error: ", e)
            return None
        
        columns_to_drop = ['description', 'deliveryDate', 'deleted_x', 'customerReference', 'imagePath', 'deleted_y', 'stock', 'orderDate', 'name', 'price', 'productAmount']
        
        df_orders = df_orders.drop(columns=df_orders.columns.intersection(columns_to_drop))
        # Create a dictionary of sets to store items bought in each order
        z = defaultdict(set)
        for order_id, product_id in zip(df_orders['orderId'], df_orders['productId']):
            z[order_id].add(product_id)

        # Create a dictionary to count combinations of items
        d = defaultdict(int)
        unique_products = set(df_orders['productId'])
        if len(unique_products) <= 2:
            raise Exception("Not enough products to analyze")

        for i in range(2, len(unique_products)):
            combs = combinations(unique_products, i)
            for comb in combs:
                for items in z.values():
                    if set(comb).issubset(items):
                        d[tuple(comb)] += 1

        product_combinations = {}

        # Sort and display the results
        sorted_combinations = list(reversed(sorted([[v, k] for k, v in d.items()])))
        for count, combination in sorted_combinations:
            for i in combination:
                # trough each combination in list
                if self._getProductNameById(i) == product_name:
                    for k in combination:
                        # trough each combination
                        if self._getProductNameById(k) != product_name:
                            if self._getProductNameById(k) in product_combinations:
                                product_combinations[self._getProductNameById(k)] += 1
                            elif self._getProductNameById(k) not in product_combinations:
                                product_combinations[self._getProductNameById(k)] = 1

        # Sort by value
        sorted_product_combinations = dict(sorted(product_combinations.items(), key=lambda item: item[1], reverse=True))
        return list(sorted_product_combinations.keys())[:combination_product_amount]
    
    def report():
        pass

    def _getProductNameById(self, product_id: int) -> str:
        """
        Gets the product name from the product ID

        Args:
            product_id (int): Product ID

        Returns:
            str: Product name

        Raises:
            Exception: Product not found
        """
        products = self.productshandler.start()

        for i in products:
            if i['productId'] == product_id:
                return i['name']
        
        raise Exception("Product not found")