from DataAnalysis.db.models.BaseRepository import BaseRepository
from DataAnalysis.db.models.queryparams import AuthParams
from DataAnalysis.db.model import Employee, Role
from sqlalchemy import func

class AuthRepository(BaseRepository[Employee]):
    def __init__(self, session, email: str, password: str):
        super().__init__(Employee, session)
        self.email = email
        self.password = password

    def get(self) -> list[AuthParams]:
        try:
            result = (
                self.session.query(Employee.email, Role.name).join(Role, Employee.roleId == Role.roleId).filter(Employee.email == self.email, Employee.password == self.password).first()
            )
            return result
        except Exception as e:
            print(f"Error while getting employee amount data: {e}")
            return []
