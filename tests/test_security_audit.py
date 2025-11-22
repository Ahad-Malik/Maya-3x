from __future__ import annotations

from tests.harness.metrics import MetricsStore
from tests.harness.suites import record_metrics, run_security_metrics
from tests.harness.systems import MockSystem


def test_security_detection_accuracy(
    systems: list[MockSystem],
    security_events,
    metrics_store: MetricsStore,
) -> None:
    for system in systems:
        suite_metrics = run_security_metrics(system, security_events)
        record_metrics(metrics_store, system, suite_metrics)

    maya3 = metrics_store.get_metric("Maya-3x", "SecurityDetectionAccuracy_pct")
    maya1 = metrics_store.get_metric("Maya-1x", "SecurityDetectionAccuracy_pct")
    baseline = metrics_store.get_metric("Baseline-Agent", "SecurityDetectionAccuracy_pct")

    assert maya3 is not None and maya3 >= 88.0
    assert maya1 is not None and baseline is not None
    assert maya3 > maya1 > baseline
