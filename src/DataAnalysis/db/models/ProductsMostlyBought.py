from DataAnalysis.db.models.BaseRepository import BaseRepository
from DataAnalysis.db.models.queryparams import ProductsMostlyBought as ProductsMostlyBoughtParams
from DataAnalysis.db.models.queryparams import OrdersProducts as OrdersProductsParams
from DataAnalysis.db.model import Product, ordersProducts

class ProductsMostlyBoughtRepository(BaseRepository[Product]):
    def __init__(self, session):
        super().__init__(Product, session)

    def get(self) -> list[ProductsMostlyBoughtParams]:
        try:
            data = self.filter()
            return data
        except Exception as e:
            print(f"Error while getting order amount data: {e}")
            return []
        
    def getOrdersProducts(self) -> list[OrdersProductsParams]:
        try:
            data = self.get_from_custom_model(ordersProducts)
            return data
        except Exception as e:
            print(f"Error while getting order amount data: {e}")
            return []
