from DataAnalysis.diagnostic.DiagnosticAnalysis import DiagnosticAnalysis
from DataAnalysis.preprocessing.APIDataHandlerFactory import APIDataHandlerFactory
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from typing import Tuple
from os import getenv

from dotenv import load_dotenv

load_dotenv()

LOWER_BOUND = -1
UPPER_BOUND = 1
TYPEOFGRAPH = "gauge"


class ProductOrdersCorrelation(DiagnosticAnalysis):
    """ Class for analyzing the correlation between product orders"""
    def __init__(self) -> None:
        self.orderhandler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/orders")
        self.ordersProductshandler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/ordersProducts")
        self.productshandler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/products")
        self.customerhandler = APIDataHandlerFactory.create_data_handler(getenv("APIURL") + "/customers")

        self.df_ordersProducts = None


    def collect(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Collects data from the API
        
        Returns:
            tuple: Tuple of dataframes containing the data
        """
        try:
            orders = self.orderhandler.start()
            ordersProducts = self.ordersProductshandler.start()
            products = self.productshandler.start()
            customers = self.customerhandler.start()
        except Exception as e:
            print("Error: ", e)
            return None, None, None

        df_orders = pd.DataFrame(orders)
        df_ordersProducts = pd.DataFrame(ordersProducts)
        df_products = pd.DataFrame(products)
        df_customers = pd.DataFrame(customers)

        return df_orders, df_ordersProducts, df_products, df_customers
    
    def merge(self) -> pd.DataFrame:
        """
        Merge the dataframes

        Returns:
            pd.DataFrame: Merged dataframe
        
        Raises:
            Exception: No data found
            Exception: One or more dataframes are empty
        """

        df_orders, df_ordersProducts, df_products, df_customers = self.collect()
        if df_orders is None or df_ordersProducts is None or df_products is None or df_customers is None:
            raise Exception("No data found")
        elif df_orders.empty or df_ordersProducts.empty or df_products.empty or df_customers.empty:
            raise Exception("One or more dataframes are empty")

        try:
            df_ordersProducts = pd.merge(df_ordersProducts, df_orders, on='orderId')
            df_ordersProducts = pd.merge(df_ordersProducts, df_products, on='productId')
            df_ordersProducts = pd.merge(df_ordersProducts, df_customers, on='customerReference')
        except Exception as e:
            print("Error: ", e)
            return None
        

        columns_to_drop = [
            'orderId', 'productId', 'addressId', 'customerId', 'description', 
            'deliveryDate', 'stock', 'imagePath', 'lastname', 'firstname', 
            'email', 'password', 'phoneNumber', 'signedUp', 'role', 
            'companyNumber', 'deleted_x', 'deleted_y', 'deleted', 'orderDate_y'
        ]

        df_ordersProducts = df_ordersProducts.drop(columns=df_ordersProducts.columns.intersection(columns_to_drop))
        df_ordersProducts = df_ordersProducts.rename(columns={'orderDate_x': 'orderDate'})
        
        df_ordersProducts['orderDate'] = pd.to_datetime(df_ordersProducts['orderDate'])
        df_ordersProducts['orderDate'] = df_ordersProducts['orderDate'].dt.strftime('%m').astype('int64')

        labelencoder = LabelEncoder()
        df_ordersProducts['businessSector'] = labelencoder.fit_transform(df_ordersProducts['businessSector'])

        
        self.df_ordersProducts = df_ordersProducts


    def perform(self) -> dict:
        """
        Perform the analysis
        
        Returns:
            dict: Dictionary containing the correlation values
        Raises:
            Exception: No data found
            Exception: Correlation values are NaN
        """
        
        self.merge()
        if self.df_ordersProducts is None:
            raise Exception("No data found")
        price_correlation = self.df_ordersProducts[['productAmount','price']].corr('spearman')
        date_correlation = self.df_ordersProducts[['productAmount','orderDate']].corr('spearman')
        user_correlation = self.df_ordersProducts[['productAmount','businessSector']].corr('spearman')

        if price_correlation.isnull().values.any() or date_correlation.isnull().values.any() or user_correlation.isnull().values.any():
            raise Exception("Correlation values are NaN")
       
        return {"product-price-corr": price_correlation.loc['productAmount', 'price'], "product-orderDate-corr" : date_correlation.loc['productAmount', 'orderDate'], "product-businessSector-corr": user_correlation.loc['productAmount', 'businessSector'], "lower-bound": LOWER_BOUND, "upper-bound": UPPER_BOUND, "typeofgraph": TYPEOFGRAPH}


    def report(self):
        pass

    def getChangingPriceOrdersCorrValue(self, price_percentage: float = 1, n_random: int = 0 ) -> dict:
        """
        Get the correlation value between productAmount and price if a imaginary percentage of price change is made

        Args:
            price_percentage (float): Price Percentage to change in decimal format. Defaults to 1 making no change. Values lower than 1 will lead to a decrease in price. Values higher than 1 will lead to an increase in price.
            n_random (int): Number of random products to adjust by the price percentage.
                            If 0, all prices are scaled uniformly.
                            If n > 0, n random prices are scaled by the price percentage.

        Example:

        getChangingPriceOrdersCorrValue(0.1, 0) will return the correlation value between productAmount and price if all prices are decreased by 90%
        getChangingPriceOrdersCorrValue(1.1, 5) will return the correlation value between productAmount and price if 5 random prices are increased by 10%

        Returns:
            dict: Dictionary containing the correlation value
        """
        self.merge()
        if self.df_ordersProducts is None:
            raise Exception("No data found")
        
        copy_df = self.df_ordersProducts.copy()
        if n_random == 0:
            copy_df['price'] = copy_df['price'] * price_percentage
        elif n_random > 0:
            if n_random > len(copy_df):
                raise Exception("Number of random products to adjust is greater than the actual number of products present")
            random_products = copy_df.sample(n=n_random)
            random_products['price'] = (random_products['price'] * price_percentage).astype(copy_df['price'].dtype)
            copy_df.update(random_products)
        
        price_correlation = copy_df[['productAmount','price']].corr('pearson')	
        return {"changed-product-price-corr" : price_correlation.loc['productAmount', 'price'], "lower-bound": LOWER_BOUND, "upper-bound": UPPER_BOUND, "typeofgraph": TYPEOFGRAPH}