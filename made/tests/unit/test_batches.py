from datetime import date
from typing import Tuple

import hypothesis.strategies as st
from hypothesis import assume, given

from made.core.domain import Batch, OrderLine


def make_batch_and_line(
    sku: str, batch_qty: int, line_qty: int
) -> Tuple[Batch, OrderLine]:
    return (
        Batch(
            reference="batch-001",
            sku=sku,
            _purchased_quantity=batch_qty,
            eta=date.today(),
        ),
        OrderLine(id="order-123", sku=sku, quantity=line_qty),
    )


@given(st.integers(), st.integers())
def test_allocation_to_batch_reduces_available_quantity(
    available_quantity, order_quantity
):
    batch, order_line = make_batch_and_line(
        "SMALL-TABLE", available_quantity, order_quantity
    )

    assume(batch.can_allocate(order_line))

    batch.allocate(order_line)

    assert batch.available_quantity == available_quantity - order_quantity


@given(st.integers(), st.integers())
def test_can_allocate_if_available_greater_or_equal_than_required(required, available):
    assume(available >= required)

    batch, line = make_batch_and_line("SMALL-TABLE", available, required)

    assert batch.can_allocate(line)


@given(st.integers(), st.integers())
def test_cannot_allocate_if_available_smaller_than_required(required, available):
    assume(available < required)

    batch, line = make_batch_and_line("SMALL-TABLE", available, required)

    assert not batch.can_allocate(line)


@given(st.text(), st.text())
def test_cannot_allocate_if_skus_do_not_match(sku1, sku2):
    assume(sku1 != sku2)

    batch = Batch(
        reference="batch-001", sku=sku1, _purchased_quantity=10, eta=date.today()
    )
    line = OrderLine(id="order-001", sku=sku2, quantity=5)

    assert not batch.can_allocate(line)


def test_cannot_deallocate_unallocated_lines():
    batch, line = make_batch_and_line("SMALL-TABLE", 20, 10)

    batch.deallocate(line)

    assert batch.available_quantity == 20


def test_can_deallocate_allocated_lines():
    batch, line = make_batch_and_line("SMALL-TABLE", 20, 10)

    batch.allocate(line)
    assert batch.available_quantity == 10

    batch.deallocate(line)
    assert batch.available_quantity == 20


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("SMALL-TABLE", 20, 10)

    batch.allocate(line)
    batch.allocate(line)

    assert batch.available_quantity == 10
