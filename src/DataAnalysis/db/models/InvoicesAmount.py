from DataAnalysis.db.models.BaseRepository import BaseRepository
from DataAnalysis.db.models.queryparams import InvoicesAmount as InvoicesAmountParams
from DataAnalysis.db.model import Invoice

class InvoicesAmountRepository(BaseRepository[Invoice]):
    def __init__(self, session):
        super().__init__(Invoice, session)

    def get(self) -> list[InvoicesAmountParams]:
        try:
            data = self.filter()
            return data
        except Exception as e:
            print(f"Error while getting order amount data: {e}")
            return []
