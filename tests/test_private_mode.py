from __future__ import annotations

from tests.harness.metrics import MetricsStore
from tests.harness.suites import record_metrics, run_privacy_metrics
from tests.harness.systems import MockSystem


def test_privacy_local_processing(
    systems: list[MockSystem],
    privacy_queries,
    metrics_store: MetricsStore,
) -> None:
    raw_results: dict[str, dict[str, float]] = {}
    for system in systems:
        suite_metrics = dict(run_privacy_metrics(system, privacy_queries))
        raw_results[system.name] = suite_metrics
        record_metrics(metrics_store, system, suite_metrics)

    maya3_ratio = metrics_store.get_metric("Maya-3x", "LocalProcessingRatio_pct")
    maya1_ratio = metrics_store.get_metric("Maya-1x", "LocalProcessingRatio_pct")
    baseline_ratio = metrics_store.get_metric("Baseline-Agent", "LocalProcessingRatio_pct")

    assert maya3_ratio is not None and maya3_ratio >= 80.0
    assert maya1_ratio is not None and baseline_ratio is not None
    assert maya3_ratio > maya1_ratio > baseline_ratio

    assert raw_results["Maya-3x"]["LocalAccuracy_pct"] >= 92.0
    assert raw_results["Baseline-Agent"]["LocalAccuracy_pct"] <= 90.0
