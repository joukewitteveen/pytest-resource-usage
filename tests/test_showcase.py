from time import sleep

import pytest


def test_pass():
    pass


@pytest.mark.skip(reason="slow test")
@pytest.mark.report_duration
def test_long_sleep():
    sleep(99)


@pytest.mark.report_duration
def test_sleep():
    _ = list(range(100_000))
    sleep(0.2)


@pytest.mark.report_duration
@pytest.mark.report_tracemalloc
def test_sleep_trace_overhead():
    _ = list(range(100_000))
    sleep(0.2)


@pytest.mark.report_tracemalloc
@pytest.mark.parametrize("elements", [2_000_000, 1_000_000])
def test_allocate(elements):
    _ = list(range(elements))
