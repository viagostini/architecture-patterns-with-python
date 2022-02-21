from datetime import date, timedelta

import pytest

from made.core.domain import Batch, OrderLine, OutOfStock, allocate

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipment():
    in_stock_batch = Batch(
        "in-stock-batch", "RETRO-CLOCK", _purchased_quantity=100, eta=None
    )
    shipment_batch = Batch(
        "shipment-batch", "RETRO-CLOCK", _purchased_quantity=100, eta=tomorrow
    )
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    _ = allocate(line, [shipment_batch, in_stock_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch(
        "speedy-batch", "MINIMALIST-SPOON", _purchased_quantity=100, eta=today
    )
    medium = Batch(
        "normal-batch", "MINIMALIST-SPOON", _purchased_quantity=100, eta=tomorrow
    )
    latest = Batch("slow-batch", "MINIMALIST-SPOON", _purchased_quantity=100, eta=later)
    line = OrderLine("order1", "MINIMALIST-SPOON", 10)

    _ = allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch(
        "in-stock-batch-ref", "HIGHBROW-POSTER", _purchased_quantity=100, eta=None
    )
    line = OrderLine("oref", "HIGHBROW-POSTER", 10)

    allocation = allocate(line, [in_stock_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-FORK", _purchased_quantity=10, eta=today)
    _ = allocate(OrderLine("order1", "SMALL-FORK", 10), [batch])

    with pytest.raises(OutOfStock):
        _ = allocate(OrderLine("order2", "SMALL-FORK", 1), [batch])
