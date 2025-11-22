from __future__ import annotations

from tests.harness.metrics import MetricsStore
from tests.harness.suites import record_metrics, run_voice_metrics
from tests.harness.systems import MockSystem


def test_realtime_latency_and_satisfaction(
    systems: list[MockSystem],
    voice_queries,
    metrics_store: MetricsStore,
) -> None:
    raw_results: dict[str, dict[str, float]] = {}
    for system in systems:
        suite_metrics = dict(run_voice_metrics(system, voice_queries))
        raw_results[system.name] = suite_metrics
        record_metrics(metrics_store, system, suite_metrics)

    maya3_latency = metrics_store.get_metric("Maya-3x", "AvgLatency_ms")
    maya1_latency = metrics_store.get_metric("Maya-1x", "AvgLatency_ms")
    baseline_latency = metrics_store.get_metric("Baseline-Agent", "AvgLatency_ms")

    assert maya3_latency is not None and maya3_latency <= 275.0
    assert maya1_latency is not None and baseline_latency is not None
    assert maya3_latency < maya1_latency < baseline_latency

    maya3_satisfaction = raw_results["Maya-3x"]["VoiceInteractionSatisfaction_mean"]
    assert maya3_satisfaction >= 4.0
    assert raw_results["Baseline-Agent"]["VoiceInteractionSatisfaction_mean"] <= 3.4
