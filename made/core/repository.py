from abc import ABC, abstractmethod

from made.core.domain import Batch


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abstractmethod
    def get(self, reference: str) -> Batch:
        raise NotImplementedError
