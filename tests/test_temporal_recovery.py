from __future__ import annotations

from tests.harness.metrics import MetricsStore
from tests.harness.suites import record_metrics, run_workflow_recovery
from tests.harness.systems import MockSystem


def test_workflow_recovery_rate(
    systems: list[MockSystem],
    task_scenarios,
    interrupted_workflows,
    metrics_store: MetricsStore,
) -> None:
    for system in systems:
        suite_metrics = run_workflow_recovery(system, task_scenarios, interrupted_workflows)
        record_metrics(metrics_store, system, suite_metrics)

    maya3 = metrics_store.get_metric("Maya-3x", "WorkflowRecoveryRate_pct")
    maya1 = metrics_store.get_metric("Maya-1x", "WorkflowRecoveryRate_pct")
    baseline = metrics_store.get_metric("Baseline-Agent", "WorkflowRecoveryRate_pct")

    assert maya3 is not None and maya3 >= 88.0
    assert maya1 is not None and baseline is not None
    assert maya3 > maya1 > baseline
