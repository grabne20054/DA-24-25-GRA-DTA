from typing import Type, TypeVar, Generic, List
from sqlalchemy.orm import Session

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def filter(self, **filters) -> List[T]:
        data = self.session.query(self.model).filter_by(**filters).all()
        return data

    def get_from_custom_model(self, model: Type[T]) -> List[T]:
        data = self.session.query(model).all()
        return data