from DataAnalysis.db.models.BaseRepository import BaseRepository
from DataAnalysis.db.models.queryparams import OrderAmount as OrderAmountParams
from DataAnalysis.db.model import Order

class OrderAmountRepository(BaseRepository[Order]):
    def __init__(self, session):
        super().__init__(Order, session)

    def get(self) -> list[OrderAmountParams]:
        try:
            data = self.filter()
            return data
        except Exception as e:
            print(f"Error while getting order amount data: {e}")
            return []
