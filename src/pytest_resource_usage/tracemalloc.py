import tracemalloc

import pytest


def format_peak_memory(size):
    """Human-readable memory usage message"""
    for unit in [" bytes", "kB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
        if size < 1000:
            break
        size /= 1000
    else:
        unit = "YB"
    return f"peak allocated memory: {size:.3g}{unit}"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """Measure peak allocated memory size on a test run

    We only measure if the `report_tracemalloc` marker is present.
    Tracing of memory allocations will be stopped after the test is
    finished only if memory allocations were not being traced already
    before the test is run.
    """
    if "report_tracemalloc" not in item.keywords:
        yield
        return

    if tracemalloc.is_tracing():
        tracemalloc_started = False
        tracemalloc.clear_traces()
    else:
        tracemalloc_started = True
        tracemalloc.start()
    yield
    _, peak_size = tracemalloc.get_traced_memory()
    if tracemalloc_started:
        tracemalloc.stop()

    item.add_report_section("call", "resource", format_peak_memory(peak_size))
