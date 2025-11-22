from __future__ import annotations

import pytest

from tests.harness.metrics import MetricsStore
from tests.harness.suites import record_metrics, run_task_performance
from tests.harness.systems import MockSystem


def test_task_completion_rate(
    systems: list[MockSystem],
    task_scenarios,
    metrics_store: MetricsStore,
) -> None:
    for system in systems:
        suite_metrics = run_task_performance(system, task_scenarios)
        record_metrics(metrics_store, system, suite_metrics)

    maya3 = metrics_store.get_metric("Maya-3x", "TaskCompletionRate_pct")
    maya1 = metrics_store.get_metric("Maya-1x", "TaskCompletionRate_pct")
    baseline = metrics_store.get_metric("Baseline-Agent", "TaskCompletionRate_pct")

    assert maya3 is not None and maya3 >= 92.0
    assert maya1 is not None and maya1 >= 75.0
    assert baseline is not None and baseline >= 60.0
    assert maya3 > maya1 > baseline
