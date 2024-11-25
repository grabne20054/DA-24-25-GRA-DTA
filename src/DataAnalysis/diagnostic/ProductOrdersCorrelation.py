from DataAnalysis.diagnostic.DiagnosticAnalysis import DiagnosticAnalysis
from DataAnalysis.APIDataHandlerFactory import APIDataHandlerFactory
import pandas as pd
from sklearn.preprocessing import LabelEncoder


class ProductOrdersCorrelation(DiagnosticAnalysis):
    """ Class for analyzing the correlation between product orders"""
    def __init__(self) -> None:
        self.orderhandler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/orders")
        self.ordersProductshandler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/ordersProducts")
        self.productshandler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/products")
        self.customerhandler = APIDataHandlerFactory.create_data_handler("http://localhost:8002/customers")

        self.df_ordersProducts = None

    def collect(self) -> tuple:
        """
        Collects data from the API
        
        Returns:
            tuple: Tuple of dataframes containing the data
        """
        
        orders = self.orderhandler.start()
        ordersProducts = self.ordersProductshandler.start()
        products = self.productshandler.start()
        customers = self.customerhandler.start()

        # convert to dataframes
        df_orders = pd.DataFrame(orders)
        df_ordersProducts = pd.DataFrame(ordersProducts)
        df_products = pd.DataFrame(products)
        df_customers = pd.DataFrame(customers)

        return df_orders, df_ordersProducts, df_products, df_customers

    def perform(self):
        """
        Perform the analysis
        
        Returns:
            tuple: Tuple of correlation values between productAmount and price, orderDate, businessSector in format (price, order date, business sector)
        """
        df_orders, df_ordersProducts, df_products, df_customers = self.collect()

        # Merge the dataframes like a SQL join
        df_ordersProducts = pd.merge(df_ordersProducts, df_orders, on='orderId')
        df_ordersProducts = pd.merge(df_ordersProducts, df_products, on='productId')
        df_ordersProducts = pd.merge(df_ordersProducts, df_customers, on='customerReference')
        

        # Drop unnecessary columns
        df_ordersProducts = df_ordersProducts.drop(columns=['orderId', 'productId', 'addressId', 'customerId', 'description', 'deliveryDate',  'stock', 'imagePath', 'lastname', 'firstname', 'email', 'password', 'phoneNumber', 'signedUp', 'role', 'companyNumber', 'deleted_x', 'deleted_y', 'deleted'])
        
        # date to month
        df_ordersProducts['orderDate'] = pd.to_datetime(df_ordersProducts['orderDate'])
        df_ordersProducts['orderDate'] = df_ordersProducts['orderDate'].dt.strftime('%m').astype('int64')

        # Label Encoding
        labelencoder = LabelEncoder()
        df_ordersProducts['businessSector'] = labelencoder.fit_transform(df_ordersProducts['businessSector'])

        
        self.df_ordersProducts = df_ordersProducts
        # Correlation
        price_correlation = df_ordersProducts[['productAmount','price']].corr('pearson')
        date_correlation = df_ordersProducts[['productAmount','orderDate']].corr('spearman')
        user_correlation = df_ordersProducts[['productAmount','businessSector']].corr('spearman')

        return price_correlation.loc['productAmount', 'price'], date_correlation.loc['productAmount', 'orderDate'], user_correlation.loc['productAmount', 'businessSector'] # get certain value from the correlation matrix


    def report(self):
        pass

    def getChangingPriceOrdersCorrValue(self, price_percentage: float = 1, n_random: int = 0 ) -> float:
        """
        Get the correlation value between productAmount and price if a imaginary percentage of price change is made

        Args:
            price_percentage (float): Price Percentage to change in decimal format. Defaults to 1 making no change. Values lower than 1 will lead to a decrease in price. Values higher than 1 will lead to an increase in price.
            n_random (int): Number of random products to adjust by the price percentage.
                            If 0, all prices are scaled uniformly.
                            If n > 0, n random prices are scaled by the price percentage.

        Returns:
            float: Correlation value between productAmount and price
        """
        copy_df = self.df_ordersProducts.copy()

        if n_random == 0:
            copy_df['price'] = copy_df['price'] * price_percentage
        elif n_random > 0:
            random_products = copy_df.sample(n=n_random)
            random_products['price'] = random_products['price'] * price_percentage
            copy_df.update(random_products)
        
        price_correlation = copy_df[['productAmount','price']].corr('pearson')	
        return price_correlation.loc['productAmount', 'price']