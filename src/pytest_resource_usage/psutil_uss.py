import gc
import multiprocessing

import psutil
import pytest


MARKER_NAME = "report_uss"


class OnDemandValue:
    """Transfer of a time-sensitive value between processes"""

    def __init__(self, typecode_or_type):
        self._data = multiprocessing.RawValue(typecode_or_type)
        self._demand = multiprocessing.Lock()
        self._supply = multiprocessing.Lock()
        self._demand.acquire()
        self._supply.acquire()

    def wait_for_demand(self, timeout=None):
        """Wait for a consumer to indicate demand

        Without a timeout, the producer and consumer will never be
        active simultaneously.
        """
        return self._demand.acquire(timeout=timeout)

    def set(self, value):
        """Satisfy the demand of a waiting consumer"""
        self._data.value = value
        self._supply.release()

    def get(self):
        """Indicate demand and await the supply of a producer"""
        self._demand.release()
        self._supply.acquire()
        return self._data.value

    @property
    def value(self):
        return self._data.value


class PollUSS(multiprocessing.Process):
    """Polling of Unique Set Size from a separate process"""

    def __init__(self, interval, pid=None):
        super().__init__(daemon=True)
        self._interval = interval
        self._process = psutil.Process(pid)
        self._peak_uss = OnDemandValue("Q")

    def start(self):
        """Start polling and return current USS"""
        super().start()
        if gc.isenabled():
            gc.collect()
        return self._peak_uss.get()

    def stop(self):
        """Stop polling and return peak observed USS"""
        peak_uss = self._peak_uss.get()
        self.join()
        return peak_uss

    def run(self):
        """Polling method to be run in the sub-process"""
        # Wait until the parent process is ready to be measured
        self._peak_uss.wait_for_demand()
        peak_uss = self._get_uss()
        self._peak_uss.set(peak_uss)
        while not self._peak_uss.wait_for_demand(self._interval):
            peak_uss = max(peak_uss, self._get_uss())
        self._peak_uss.set(peak_uss)

    def _get_uss(self):
        """Unique Set Size of the measured process and its children"""
        uss = self._process.memory_full_info().uss
        for child_process in self._process.children(recursive=True):
            if child_process.pid == self.pid:
                # Skip the process from which we poll
                continue
            try:
                uss += child_process.memory_full_info().uss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return uss


def format_peak_memory(size):
    """Human-readable memory usage message"""
    for unit in [" bytes", "kB", "MB", "GB", "TB", "PB"]:
        if size < 1000:
            break
        size /= 1000
    else:
        unit = "EB"
    return f"peak unique set size: {size:.3g}{unit}"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """Observe peak unique set size of a test run

    The unique set size of the test process and all its children is
    obtained using `psutil`. The frequency of observing is controlled
    with the `interval` keyword argument of the `report_uss` marker.
    In case no polling interval is specified, a default of 0.1 seconds
    is used. Polling only takes place if the marker is present.
    When automatic garbage collection is enabled, we ensured that
    garbage is collected before the test is started.
    """
    if MARKER_NAME not in item.keywords:
        yield
        return
    for marker in item.iter_markers(MARKER_NAME):
        try:
            interval = marker.kwargs["interval"]
        except KeyError:
            continue
        break
    else:
        interval = 0.1

    monitor = PollUSS(interval)
    reference_uss = monitor.start()
    yield
    peak_uss = monitor.stop()

    item.add_report_section(
        "call", "resource", format_peak_memory(peak_uss - reference_uss)
    )


def pytest_configure(config):
    """Register the marker"""
    config.addinivalue_line(
        "markers",
        f"{MARKER_NAME}(*, interval): "
        "report highest unshared memory of tests, "
        "observed every `interval` seconds.",
    )
