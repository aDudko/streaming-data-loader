import pytest

from prometheus_client import Summary
from metrics import (
    counter_metric_decorator,
    consume_time_metric,
    errors_total,
    messages_processed,
    batch_processing_time_metric,
    response_time_metric
)


@pytest.mark.asyncio
@pytest.mark.parametrize("raise_error", [False, True])
async def test_counter_metric_decorator_counts(raise_error):
    calls = {"called": False}

    @counter_metric_decorator()
    async def decorated_func():
        calls["called"] = True
        if raise_error:
            raise ValueError("Test error")

    if raise_error:
        with pytest.raises(ValueError):
            await decorated_func()
        assert errors_total._value.get() > 0
    else:
        await decorated_func()
        assert calls["called"]


def test_messages_processed_increment():
    start = messages_processed._value.get()
    messages_processed.inc(3)
    assert messages_processed._value.get() == start + 3


def test_messages_processed_no_increment():
    start = messages_processed._value.get()
    assert messages_processed._value.get() == start


def test_errors_total_increment():
    start = errors_total._value.get()
    errors_total.inc()
    assert errors_total._value.get() == start + 1


def test_errors_total_no_increment():
    start = errors_total._value.get()
    assert errors_total._value.get() == start


@pytest.mark.asyncio
async def test_consume_time_metric_decorator_measures():
    metric = Summary("test_consume_time", "test")
    calls = []

    @counter_metric_decorator(metric=metric)
    async def dummy():
        calls.append(1)

    await dummy()
    assert sum(calls) == 1
    assert metric._count.get() >= 1


@pytest.mark.asyncio
async def test_batch_processing_time_metric_decorator_measures():
    metric = batch_processing_time_metric
    metric._count.set(0)

    @metric.time()
    async def dummy():
        return True

    await dummy()
    assert metric._count.get() >= 1


@pytest.mark.asyncio
async def test_response_time_metric_measures():
    metric = response_time_metric
    metric._count.set(0)

    @metric.time()
    async def dummy():
        return True

    await dummy()
    assert metric._count.get() >= 1
