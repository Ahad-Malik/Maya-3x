from __future__ import annotations

from statistics import mean
from typing import Iterable, Mapping, Sequence

from .data_generation import MemoryQuery, PrivacyQuery, SecurityEvent, TaskScenario, VoiceQuery
from .metrics import MetricsStore
from .systems import MockSystem


def run_task_performance(system: MockSystem, scenarios: Sequence[TaskScenario]) -> Mapping[str, float]:
    successes = 0
    hitl = 0
    for scenario in scenarios:
        outcome = system.execute_workflow(scenario)
        successes += int(outcome.success)
        hitl += int(outcome.hitl_required)
    total = len(scenarios) or 1
    return {
        "TaskCompletionRate_pct": successes / total * 100,
        "HITLCount": float(hitl),
        "Total": float(total),
    }


def run_workflow_recovery(
    system: MockSystem,
    scenarios: Sequence[TaskScenario],
    interrupted_ids: Iterable[int],
) -> Mapping[str, float]:
    interrupted = set(interrupted_ids)
    resumed = 0
    total = 0
    for scenario in scenarios:
        if scenario.task_id not in interrupted:
            continue
        outcome = system.recover_workflow(scenario, interrupted=True)
        resumed += int(outcome.resumed)
        total += 1
    total = total or 1
    return {
        "WorkflowRecoveryRate_pct": resumed / total * 100,
        "RecoveryEvaluations": float(total),
    }


def run_voice_metrics(system: MockSystem, queries: Sequence[VoiceQuery]) -> Mapping[str, float]:
    latencies = []
    satisfactions = []
    for query in queries:
        outcome = system.run_voice_interaction(query)
        latencies.append(outcome.latency_ms)
        satisfactions.append(outcome.satisfaction_score)
    latency_ms = float(mean(latencies)) if latencies else 0.0
    satisfaction_score = float(mean(satisfactions)) if satisfactions else 0.0
    return {
        "AvgLatency_ms": latency_ms,
        "VoiceInteractionSatisfaction_mean": satisfaction_score,
    }


def run_privacy_metrics(system: MockSystem, queries: Sequence[PrivacyQuery]) -> Mapping[str, float]:
    local = 0
    total_sensitive = 0
    accuracies = []
    for query in queries:
        outcome = system.route_privacy_query(query)
        if query.is_sensitive:
            total_sensitive += 1
            local += int(outcome.processed_locally)
        accuracies.append(outcome.relative_accuracy)
    total_sensitive = total_sensitive or 1
    return {
        "LocalProcessingRatio_pct": local / total_sensitive * 100,
        "LocalAccuracy_pct": mean(accuracies) * 100 if accuracies else 0.0,
    }


def run_memory_metrics(system: MockSystem, queries: Sequence[MemoryQuery]) -> Mapping[str, float]:
    successes = 0
    eligible = 0
    for query in queries:
        if not query.has_relevant_facts:
            continue
        eligible += 1
        outcome = system.retrieve_memory(query)
        successes += int(outcome.retrieved_relevant)
    eligible = eligible or 1
    return {
        "MemoryRetrievalAccuracy_pct": successes / eligible * 100,
        "MemoryEligible": float(eligible),
    }


def run_security_metrics(system: MockSystem, events: Sequence[SecurityEvent]) -> Mapping[str, float]:
    correct = 0
    total = len(events) or 1
    for event in events:
        outcome = system.audit_event(event)
        if bool(outcome.flagged) == bool(event.is_malicious):
            correct += 1
    return {
        "SecurityDetectionAccuracy_pct": correct / total * 100,
        "SecurityEvents": float(total),
    }


def record_metrics(store: MetricsStore, system: MockSystem, metrics: Mapping[str, float]) -> None:
    for key, value in metrics.items():
        if key.endswith("_pct") or key == "AvgLatency_ms":
            store.record(system.name, key, value)
