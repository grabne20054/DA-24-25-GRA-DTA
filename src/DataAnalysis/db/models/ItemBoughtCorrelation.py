from DataAnalysis.db.models.BaseRepository import BaseRepository
from DataAnalysis.db.models.queryparams import OrdersParam, ProductsParam, OrdersProductsParam
from DataAnalysis.db.model import Product, ordersProducts, Order
from uuid import UUID

class ItemBoughtCorrelationRepository(BaseRepository[Product]):
    def __init__(self, session):
        super().__init__(Product, session)

    def getProducts(self) -> list[ProductsParam]:
        try:
            data = self.filter()
            return data
        except Exception as e:
            print(f"Error while getting order amount data: {e}")
            return []

    def getOrdersProducts(self) -> list[OrdersProductsParam]:
        try:
            data = self.get_from_custom_model(ordersProducts)
            return data
        except Exception as e:
            print(f"Error while getting order amount data: {e}")
            return []
        
    def getOrders(self) -> list[OrdersParam]:
        try:
            data = self.get_from_custom_model(Order)
            return data
        except Exception as e:
            print(f"Error while getting order amount data: {e}")
            return []
        
    def getAll(self) -> tuple[list[ProductsParam], list[OrdersProductsParam], list[OrdersParam]]:
        return self.getProducts(), self.getOrdersProducts(), self.getOrders()

