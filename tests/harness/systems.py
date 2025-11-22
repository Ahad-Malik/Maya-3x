from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, List

from .data_generation import MemoryQuery, PrivacyQuery, SecurityEvent, TaskScenario, VoiceQuery


@dataclass(frozen=True)
class SystemConfig:
    name: str
    display_name: str
    task_completion_rate: float
    recovery_rate: float
    recovery_step_penalty: float
    avg_latency_ms: float
    latency_jitter_ms: float
    local_processing_ratio: float
    local_accuracy: float
    memory_accuracy: float
    memory_hop_penalty: float
    security_detection: float
    security_false_positive: float
    voice_satisfaction_mean: float


@dataclass(frozen=True)
class WorkflowOutcome:
    success: bool
    hitl_required: bool


@dataclass(frozen=True)
class RecoveryOutcome:
    resumed: bool


@dataclass(frozen=True)
class VoiceOutcome:
    latency_ms: float
    satisfaction_score: float


@dataclass(frozen=True)
class PrivacyOutcome:
    processed_locally: bool
    relative_accuracy: float


@dataclass(frozen=True)
class MemoryOutcome:
    retrieved_relevant: bool


@dataclass(frozen=True)
class SecurityOutcome:
    flagged: bool


class MockSystem:
    """Probabilistic stand-in for a deployed system."""

    def __init__(self, config: SystemConfig, *, seed_offset: int = 0) -> None:
        self.config = config
        combined_seed = hash((config.name, seed_offset)) & 0xFFFFFFFF
        self._rng = random.Random(combined_seed)

    @property
    def name(self) -> str:  # pragma: no cover - trivial accessor
        return self.config.name

    @property
    def display_name(self) -> str:  # pragma: no cover - trivial accessor
        return self.config.display_name

    def _draw(self, probability: float) -> bool:
        return self._rng.random() < max(0.0, min(1.0, probability))

    def execute_workflow(self, scenario: TaskScenario) -> WorkflowOutcome:
        base_prob = self.config.task_completion_rate
        step_penalty = 0.01 * max(0, scenario.steps - 6)
        success_prob = base_prob - step_penalty
        success = self._draw(success_prob)
        hitl = scenario.requires_hitl_review and not success and self._rng.random() < 0.5
        return WorkflowOutcome(success=success or hitl, hitl_required=hitl)

    def recover_workflow(self, scenario: TaskScenario, interrupted: bool) -> RecoveryOutcome:
        if not interrupted:
            return RecoveryOutcome(resumed=True)
        resume_prob = self.config.recovery_rate - self.config.recovery_step_penalty * max(
            0, scenario.steps - 6
        )
        resumed = self._draw(resume_prob)
        return RecoveryOutcome(resumed=resumed)

    def run_voice_interaction(self, query: VoiceQuery) -> VoiceOutcome:
        base = self.config.avg_latency_ms
        tokens_factor = 0.45 * (query.transcript_tokens - 60)
        modality_penalty = {"voice_only": 0, "voice_screen": 45, "voice_image": 75}[query.modality_mix]
        follow_up_penalty = 65 if query.contains_follow_up else 0
        noise = self._rng.gauss(0, self.config.latency_jitter_ms)
        latency = max(120.0, base + tokens_factor + modality_penalty + follow_up_penalty + noise)
        satisfaction = self.config.voice_satisfaction_mean
        satisfaction -= 0.003 * max(0, query.transcript_tokens - 80)
        satisfaction -= 0.05 if latency > base * 1.5 else 0
        satisfaction = max(1.0, min(5.0, satisfaction + self._rng.gauss(0, 0.25)))
        return VoiceOutcome(latency_ms=latency, satisfaction_score=satisfaction)

    def route_privacy_query(self, query: PrivacyQuery) -> PrivacyOutcome:
        base_ratio = self.config.local_processing_ratio
        sensitivity_boost = 0.15 if query.is_sensitive else -0.2
        context_penalty = 0.1 if query.context_kb > 256 else 0
        decision_prob = base_ratio + sensitivity_boost - context_penalty
        processed_locally = self._draw(decision_prob)
        accuracy = self.config.local_accuracy
        if not processed_locally:
            accuracy = max(0.5, accuracy - 0.08)
        return PrivacyOutcome(processed_locally=processed_locally, relative_accuracy=accuracy)

    def retrieve_memory(self, query: MemoryQuery) -> MemoryOutcome:
        base = self.config.memory_accuracy
        hop_penalty = self.config.memory_hop_penalty * max(0, query.hops_required - 1)
        has_signal = 0.5 if not query.has_relevant_facts else 0
        prob = base - hop_penalty - has_signal
        return MemoryOutcome(retrieved_relevant=self._draw(prob))

    def audit_event(self, event: SecurityEvent) -> SecurityOutcome:
        if event.is_malicious:
            flagged = self._draw(self.config.security_detection)
        else:
            flagged = self._draw(self.config.security_false_positive)
        return SecurityOutcome(flagged=flagged)


MOCK_CONFIGS: List[SystemConfig] = [
    SystemConfig(
        name="Maya-3x",
        display_name="Maya-3x",
    task_completion_rate=0.975,
        recovery_rate=0.985,
        recovery_step_penalty=0.01,
        avg_latency_ms=220.0,
        latency_jitter_ms=48.0,
        local_processing_ratio=0.88,
        local_accuracy=0.97,
    memory_accuracy=0.97,
    memory_hop_penalty=0.035,
        security_detection=0.93,
        security_false_positive=0.07,
        voice_satisfaction_mean=4.4,
    ),
    SystemConfig(
        name="Maya-1x",
        display_name="Maya-1x",
        task_completion_rate=0.84,
        recovery_rate=0.79,
        recovery_step_penalty=0.02,
        avg_latency_ms=385.0,
        latency_jitter_ms=72.0,
        local_processing_ratio=0.56,
        local_accuracy=0.91,
        memory_accuracy=0.78,
        memory_hop_penalty=0.08,
        security_detection=0.74,
        security_false_positive=0.11,
        voice_satisfaction_mean=3.7,
    ),
    SystemConfig(
        name="Baseline-Agent",
        display_name="Baseline Agent",
        task_completion_rate=0.71,
        recovery_rate=0.42,
        recovery_step_penalty=0.025,
        avg_latency_ms=520.0,
        latency_jitter_ms=95.0,
        local_processing_ratio=0.18,
        local_accuracy=0.85,
        memory_accuracy=0.62,
        memory_hop_penalty=0.09,
        security_detection=0.51,
        security_false_positive=0.18,
        voice_satisfaction_mean=3.2,
    ),
]


def get_systems(mode: str = "mock", *, seed: int = 2024) -> List[MockSystem]:
    if mode != "mock":
        raise NotImplementedError(
            "Only mock evaluation mode is implemented. Hook production clients via get_systems()."
        )
    return [MockSystem(config, seed_offset=seed) for config in MOCK_CONFIGS]
