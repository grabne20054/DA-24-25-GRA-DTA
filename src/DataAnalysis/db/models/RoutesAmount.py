from DataAnalysis.db.models.BaseRepository import BaseRepository
from DataAnalysis.db.models.queryparams import RoutesAmount as RoutesAmountParams
from DataAnalysis.db.model import Route, routesOrders
from sqlalchemy import func

class RoutesAmountRepository(BaseRepository[Route]):
    def __init__(self, session, limit):
        super().__init__(Route, session)
        self.limit = limit

    def get(self) -> list[RoutesAmountParams]:
        try:
           
            result = (
                self.session.query(Route.name, func.count(routesOrders.c.orderId).label("order_count"))
                .join(routesOrders, Route.routeId == routesOrders.c.routeId)
                .group_by(Route.name)
                .order_by(func.count(routesOrders.c.orderId).desc())
                .limit(self.limit)
                .all()
            )
            return result
        except Exception as e:
            print(f"Error while getting order amount data: {e}")
            return []