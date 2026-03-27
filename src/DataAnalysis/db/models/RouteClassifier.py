from DataAnalysis.db.models.BaseRepository import BaseRepository
from DataAnalysis.db.models.queryparams import RouteClassifierParam as RouteClassifierParams
from DataAnalysis.db.model import routesOrders, Address, Order, Customer

class RouteClassifierRepository(BaseRepository[routesOrders]):
    def __init__(self, session):
        super().__init__(routesOrders, session)

    def get(self) -> list[RouteClassifierParams]:
        try:
            data = self.session.query(
                routesOrders.c.routeId,
                Address.latitude, Address.longitude,
            ).join(Order, routesOrders.c.orderId==Order.orderId
            ).join(Customer, Order.customerReference==Customer.customerReference
            ).join(Address, Customer.addressId==Address.addressId).all()
            data = [RouteClassifierParams(routeId=row.routeId, latitude=row.latitude, longitude=row.longitude) for row in data]
            return data
        except Exception as e:
            print(f"Error while getting order amount data: {e}")
            return []