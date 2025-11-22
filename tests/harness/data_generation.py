from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Set


@dataclass(frozen=True)
class TaskScenario:
    """Represents a multi-step workflow executed via Maya Studio."""

    task_id: int
    category: str
    steps: int
    requires_hitl_review: bool


@dataclass(frozen=True)
class VoiceQuery:
    """Synthetic representation of a voice interaction."""

    utterance_id: int
    transcript_tokens: int
    modality_mix: str
    contains_follow_up: bool


@dataclass(frozen=True)
class PrivacyQuery:
    """Encodes whether a query should stay local or offload."""

    query_id: int
    is_sensitive: bool
    context_kb: int


@dataclass(frozen=True)
class MemoryQuery:
    """Captures a retrieval request against the memory graph."""

    query_id: int
    hops_required: int
    has_relevant_facts: bool


@dataclass(frozen=True)
class SecurityEvent:
    """Describes an agent action that may be anomalous."""

    event_id: int
    vector: str
    is_malicious: bool


CATEGORY_WEIGHTS = {
    "scheduling": 0.22,
    "research": 0.2,
    "summarization": 0.18,
    "multimodal": 0.15,
    "continual_planning": 0.15,
    "sensitive_analysis": 0.1,
}


def _build_rng(rng: random.Random | None, seed: int | None = None) -> random.Random:
    if rng is not None:
        return rng
    if seed is not None:
        return random.Random(seed)
    return random.Random(1337)


def generate_task_scenarios(
    count: int = 100, *, rng: random.Random | None = None
) -> List[TaskScenario]:
    sampler = _build_rng(rng)
    categories: Sequence[str] = tuple(CATEGORY_WEIGHTS.keys())
    weights: Sequence[float] = tuple(CATEGORY_WEIGHTS.values())
    scenarios: List[TaskScenario] = []
    for task_id in range(count):
        category = sampler.choices(categories, weights=weights, k=1)[0]
        steps = sampler.randint(4, 9) if category != "multimodal" else sampler.randint(5, 11)
        requires_hitl = category in {"sensitive_analysis", "multimodal"} and sampler.random() < 0.2
        scenarios.append(
            TaskScenario(
                task_id=task_id,
                category=category,
                steps=steps,
                requires_hitl_review=requires_hitl,
            )
        )
    return scenarios


def select_interrupted_workflows(
    scenarios: Sequence[TaskScenario], *, ratio: float = 0.5, rng: random.Random | None = None
) -> Set[int]:
    sampler = _build_rng(rng)
    total_to_interrupt = max(1, int(len(scenarios) * ratio))
    ids = [scenario.task_id for scenario in scenarios]
    sampler.shuffle(ids)
    return set(ids[:total_to_interrupt])


def generate_voice_queries(
    count: int = 1000, *, rng: random.Random | None = None
) -> List[VoiceQuery]:
    sampler = _build_rng(rng)
    modalities = ["voice_only", "voice_screen", "voice_image"]
    queries: List[VoiceQuery] = []
    for idx in range(count):
        transcript_tokens = sampler.randint(12, 140)
        modality_mix = sampler.choices(modalities, weights=[0.6, 0.25, 0.15], k=1)[0]
        contains_follow_up = sampler.random() < 0.35
        queries.append(
            VoiceQuery(
                utterance_id=idx,
                transcript_tokens=transcript_tokens,
                modality_mix=modality_mix,
                contains_follow_up=contains_follow_up,
            )
        )
    return queries


def generate_privacy_queries(
    count: int = 200, *, rng: random.Random | None = None
) -> List[PrivacyQuery]:
    sampler = _build_rng(rng)
    queries: List[PrivacyQuery] = []
    for idx in range(count):
        is_sensitive = sampler.random() < 0.5
        base_context = sampler.randint(25, 400)
        if is_sensitive:
            base_context = max(base_context, sampler.randint(50, 200))
        queries.append(
            PrivacyQuery(
                query_id=idx,
                is_sensitive=is_sensitive,
                context_kb=base_context,
            )
        )
    return queries


def generate_memory_queries(
    count: int = 120, *, rng: random.Random | None = None
) -> List[MemoryQuery]:
    sampler = _build_rng(rng)
    queries: List[MemoryQuery] = []
    for idx in range(count):
        hops_required = sampler.choice([1, 2, 3])
        has_relevant_facts = sampler.random() < (0.9 if hops_required == 1 else 0.7)
        queries.append(
            MemoryQuery(
                query_id=idx,
                hops_required=hops_required,
                has_relevant_facts=has_relevant_facts,
            )
        )
    return queries


def generate_security_events(
    count: int = 80, *, rng: random.Random | None = None
) -> List[SecurityEvent]:
    sampler = _build_rng(rng)
    vectors = [
        "prompt_override",
        "credential_exfiltration",
        "tool_chain_abuse",
        "data_exfil",
        "policy_violation",
    ]
    events: List[SecurityEvent] = []
    for idx in range(count):
        vector = sampler.choice(vectors)
        is_malicious = sampler.random() < 0.45
        events.append(
            SecurityEvent(
                event_id=idx,
                vector=vector,
                is_malicious=is_malicious,
            )
        )
    return events


def reproducible_shuffle(items: Sequence[int], *, rng: random.Random | None = None) -> List[int]:
    sampler = _build_rng(rng)
    pool = list(items)
    sampler.shuffle(pool)
    return pool
