from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


class OutOfStock(Exception):
    pass


@dataclass
class OrderLine:
    id: str
    sku: str
    qty: int

    def __hash__(self) -> int:
        return hash(self.id)


class Batch:
    def __init__(self, reference: str, sku: str, quantity: int, eta: Optional[date]):
        self.reference = reference
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = quantity
        self._allocations: set[OrderLine] = set()

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other: Batch) -> bool:
        if self.eta is None:
            return False

        if other.eta is None:
            return True

        return self.eta > other.eta

    def allocate(self, order_line: OrderLine):
        if self.can_allocate(order_line):
            self._allocations.add(order_line)

    def deallocate(self, order_line: OrderLine):
        if order_line in self._allocations:
            self._allocations.remove(order_line)

    def can_allocate(self, order_line: OrderLine) -> bool:
        return self.sku == order_line.sku and self.available_quantity >= order_line.qty


def allocate(line: OrderLine, batches: list[Batch]) -> str:
    try:
        batch = next(batch for batch in sorted(batches) if batch.can_allocate(line))
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")

    batch.allocate(line)

    return batch.reference
