from __future__ import annotations

from tests.harness.metrics import MetricsStore
from tests.harness.suites import record_metrics, run_memory_metrics
from tests.harness.systems import MockSystem


def test_memory_retrieval_accuracy(
    systems: list[MockSystem],
    memory_queries,
    metrics_store: MetricsStore,
) -> None:
    for system in systems:
        suite_metrics = run_memory_metrics(system, memory_queries)
        record_metrics(metrics_store, system, suite_metrics)

    maya3 = metrics_store.get_metric("Maya-3x", "MemoryRetrievalAccuracy_pct")
    maya1 = metrics_store.get_metric("Maya-1x", "MemoryRetrievalAccuracy_pct")
    baseline = metrics_store.get_metric("Baseline-Agent", "MemoryRetrievalAccuracy_pct")

    assert maya3 is not None and maya3 >= 88.0
    assert maya1 is not None and baseline is not None
    assert maya3 > maya1 > baseline
