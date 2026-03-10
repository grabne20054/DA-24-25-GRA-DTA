from DataAnalysis.db.models.BaseRepository import BaseRepository
from DataAnalysis.db.models.queryparams import EmployeeAmount as EmployeeAmountParams
from DataAnalysis.db.model import Employee, Role
from sqlalchemy import func

class EmployeeAmountRepository(BaseRepository[Employee]):
    def __init__(self, session, limit):
        super().__init__(Employee, session)
        self.limit = limit

    def get(self) -> list[EmployeeAmountParams]:
        try:
            result = (
                self.session.query(Role.name, func.count(Employee.employeeId).label("employee_count"))
                .join(Employee, Role.roleId == Employee.roleId)
                .group_by(Role.name)
                .order_by(func.count(Employee.employeeId).desc())
                .limit(self.limit)
                .all()
            )
            return result
        except Exception as e:
            print(f"Error while getting employee amount data: {e}")
            return []
