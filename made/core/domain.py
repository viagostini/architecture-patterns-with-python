from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


class OutOfStock(Exception):
    pass


@dataclass(frozen=True)
class OrderLine:
    id: str
    sku: str
    quantity: int


@dataclass
class Batch:
    reference: str
    sku: str
    eta: Optional[date]
    _purchased_quantity: int
    _allocations: set[OrderLine] = field(default_factory=set)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.quantity for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

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
        return (
            self.sku == order_line.sku
            and self.available_quantity >= order_line.quantity
        )


def allocate(line: OrderLine, batches: list[Batch]) -> str:
    try:
        batch = next(batch for batch in sorted(batches) if batch.can_allocate(line))
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")

    batch.allocate(line)

    return batch.reference
