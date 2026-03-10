from DataAnalysis.db.models.BaseRepository import BaseRepository
from DataAnalysis.db.models.queryparams import ProductsAmount as ProductsAmountParams
from DataAnalysis.db.model import Product

class ProductsAmountRepository(BaseRepository[Product]):
    def __init__(self, session):
        super().__init__(Product, session)

    def get(self) -> list[ProductsAmountParams]:
        try:
            data = self.filter()
            return data
        except Exception as e:
            print(f"Error while getting order amount data: {e}")
            return []
