import pytest


def get_all_reports(terminalreporter):
    """Reports for all stages and all outcomes"""
    for reports in terminalreporter.stats.values():
        for report in reports:
            if isinstance(report, pytest.TestReport):
                yield report


def resource_usage_message(report):
    """The resource usage message for a report"""
    return ", ".join(
        content
        for (prefix, content) in report.get_sections(
            f"Captured resource {report.when}"
        )
    )


@pytest.hookimpl
def pytest_terminal_summary(terminalreporter):
    """Produce a resource usage report if any test asked for it"""
    resource_reports = [
        (report, message)
        for report in get_all_reports(terminalreporter)
        if (message := resource_usage_message(report))
    ]
    if not resource_reports:
        return
    terminalreporter.write_sep("=", "resource usage", bold=True)
    for report, message in resource_reports:
        terminalreporter.write_line(
            f"{report.nodeid} ({report.when}) {message}"
        )
