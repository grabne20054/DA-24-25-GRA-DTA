from DataAnalysis.db.models.BaseRepository import BaseRepository
from DataAnalysis.db.models.queryparams import CustomerSignup as CustomerSignupParams
from DataAnalysis.db.model import Customer

class CustomerSignupRepository(BaseRepository[Customer]):
    def __init__(self, session):
        super().__init__(Customer, session)

    def get(self) -> list[CustomerSignupParams]:
        try:
            data = self.filter()
            return data
        except Exception as e:
            print(f"Error while getting customer signup data: {e}")
            return []
