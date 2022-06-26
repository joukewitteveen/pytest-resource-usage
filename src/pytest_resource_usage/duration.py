import datetime

import pytest


MARKER_NAME = "report_duration"


def format_duration(seconds):
    """Human-readable running time message"""
    if seconds < 60:
        duration_string = f"{seconds:.3f} seconds"
    else:
        duration_string = str(datetime.timedelta(seconds=round(seconds)))
    return f"running time: {duration_string}"


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Report running time of a test call"""
    if call.when == "call" and MARKER_NAME in item.keywords:
        item.add_report_section(
            call.when, "resource", format_duration(call.duration)
        )


def pytest_configure(config):
    """Register the marker"""
    config.addinivalue_line(
        "markers", f"{MARKER_NAME}: report duration of tests."
    )
