"""Count collection and execution in the pytest process that writes JUnit."""
import json
import os
from pathlib import Path

from gate_lib import pytest_module as is_test_module


def pytest_sessionstart(session):
    global counts, outcomes, failed_subtests
    outcomes = {}
    failed_subtests = set()
    counts = dict(collected=0, deselected=0, excluded=0, started=0,
                  subtests=0, subfailures=0, modules=[], items=[], finished=0)


def pytest_ignore_collect(collection_path, config):
    if collection_path == Path.cwd() / "test/django_gui":
        counts["excluded"] += 1
        return True
    return None


def pytest_collectreport(report):
    if "::" not in report.nodeid and is_test_module(report.nodeid):
        counts["modules"].append(report.nodeid)


def pytest_itemcollected(item):
    counts["collected"] += 1
    counts["items"].append(item.nodeid)


def pytest_deselected(items):
    counts["deselected"] += len(items)


def pytest_runtest_logstart(nodeid, location):
    counts["started"] += 1


def pytest_runtest_logfinish(nodeid, location):
    counts["finished"] += 1


def pytest_runtest_logreport(report):
    if hasattr(report, "context"):  # pytest's SubtestReport
        counts["subtests"] += 1
        if report.failed:
            counts["subfailures"] += 1
            failed_subtests.add(report.nodeid)
        return
    if report.when != "call" and report.passed:
        return
    if report.when == "teardown" and report.nodeid not in outcomes:
        return
    status = {"passed": "PASS", "failed": "FAIL", "skipped": "SKIP"}
    if outcomes.get(report.nodeid) != "FAIL":
        outcomes[report.nodeid] = status[report.outcome]


def pytest_sessionfinish(session, exitstatus):
    counts["reports"] = [
        {"id": node, "outcome": "FAIL" if node in failed_subtests else status}
        for node, status in sorted(outcomes.items())
    ]
    counts["modules"].sort()
    with open(os.environ["ORV_COLLECTION"], "x", encoding="utf-8") as stream:
        json.dump(counts, stream)
