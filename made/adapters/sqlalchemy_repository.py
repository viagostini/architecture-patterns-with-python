import sqlalchemy

from made.core.domain import Batch
from made.core.repository import AbstractRepository


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: sqlalchemy.orm.Session):
        self.session = session

    def add(self, batch: Batch):
        self.session.add(batch)

    def get(self, reference: str) -> Batch:
        return self.session.query(Batch).filter_by(reference=reference).one()

    def list(self) -> list[Batch]:
        return self.session.query(Batch).all()
