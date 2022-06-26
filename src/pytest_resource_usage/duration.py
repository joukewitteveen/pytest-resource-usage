import datetime

import pytest


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
    if call.when == "call" and "report_duration" in item.keywords:
        item.add_report_section(
            call.when, "resource", format_duration(call.duration)
        )
