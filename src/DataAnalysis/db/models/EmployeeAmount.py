from DataAnalysis.db.models.BaseRepository import BaseRepository
from DataAnalysis.db.models.queryparams import EmployeeAmount as EmployeeAmountParams, Roles as RolesParams
from DataAnalysis.db.model import Employee, Role

class EmployeeAmountRepository(BaseRepository[Employee]):
    def __init__(self, session):
        super().__init__(Employee, session)

    def get(self) -> list[EmployeeAmountParams]:
        try:
            data = self.filter()
            return data
        except Exception as e:
            print(f"Error while getting employee amount data: {e}")
            return []
        
    def getRoles(self) -> list[RolesParams]:
        try:
            data = self.get_from_custom_model(Role)
            return data
        except Exception as e:
            print(f"Error while getting employee roles data: {e}")
            return []
