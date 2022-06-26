# pytest-resource-usage

This is a personal experiment to add running times and peak memory usage
(including swap) of tests to the output of [pytest](https://pytest.org).
Memory usage is tracked through `tracemalloc`, which can have a high
overhead. Since `tracemalloc` is a standard library, the only dependency
of `pytest-resource-usage` is `pytest`.

If you want something more feature-rich and ambitious, you should use
[pytest-monitor](https://github.com/CFMTech/pytest-monitor).


## Example usage

Reporting is triggered by the presence of the `report_duration` and
`report_tracemalloc` markers.

```python
from time import sleep

import pytest


@pytest.mark.report_duration
def test_sleep():
    sleep(99)


@pytest.mark.report_tracemalloc
@pytest.mark.parametrize("elements", [2_000_000, 1_000_000])
def test_allocate(elements):
    _ = list(range(elements))


@pytest.mark.report_duration
@pytest.mark.report_tracemalloc
def test_sleep_trace_overhead():
    _ = list(range(100_000))
    sleep(0.2)
```

Running the above tests produces the following `pytest` output

```
============================================== test session starts ===============================================
plugins: pytest_resource_usage-0.0.1
collected 4 items                                                                                                

tests/test_readme.py ....                                                                                  [100%]

================================================= resource usage =================================================
tests/test_readme.py::test_sleep (call) running time: 0:01:39
tests/test_readme.py::test_allocate[2000000] (call) peak allocated memory: 72MB
tests/test_readme.py::test_allocate[1000000] (call) peak allocated memory: 36MB
tests/test_readme.py::test_sleep_trace_overhead (call) peak allocated memory: 3.59MB, running time: 0.228 seconds
========================================= 4 passed in 100.20s (0:01:40) ==========================================
```
