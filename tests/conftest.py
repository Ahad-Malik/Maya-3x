from __future__ import annotations

import random
from typing import Iterable, List

import pytest

from tests.harness.data_generation import (
    generate_memory_queries,
    generate_privacy_queries,
    generate_security_events,
    generate_task_scenarios,
    generate_voice_queries,
    select_interrupted_workflows,
)
from tests.harness.metrics import MetricsStore
from tests.harness.systems import MockSystem, get_systems


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--mode",
        action="store",
        metavar="MODE",
        default="mock",
        help="Evaluation mode (mock | prod). Mock uses synthetic harness only.",
    )


def pytest_configure(config: pytest.Config) -> None:
    random.seed(2024)


@pytest.fixture(scope="session")
def evaluation_seed() -> int:
    return 2024


@pytest.fixture(scope="session")
def evaluation_mode(pytestconfig: pytest.Config) -> str:
    return str(pytestconfig.getoption("mode") or "mock")


@pytest.fixture(scope="session")
def systems(evaluation_mode: str, evaluation_seed: int) -> List[MockSystem]:
    return get_systems(evaluation_mode, seed=evaluation_seed)


@pytest.fixture(scope="session")
def task_scenarios(evaluation_seed: int):
    return generate_task_scenarios(count=100, rng=random.Random(evaluation_seed))


@pytest.fixture(scope="session")
def interrupted_workflows(task_scenarios, evaluation_seed: int):
    return select_interrupted_workflows(
        task_scenarios,
        ratio=0.5,
        rng=random.Random(evaluation_seed + 1),
    )


@pytest.fixture(scope="session")
def voice_queries(evaluation_seed: int):
    return generate_voice_queries(count=1000, rng=random.Random(evaluation_seed + 2))


@pytest.fixture(scope="session")
def privacy_queries(evaluation_seed: int):
    return generate_privacy_queries(count=200, rng=random.Random(evaluation_seed + 3))


@pytest.fixture(scope="session")
def memory_queries(evaluation_seed: int):
    return generate_memory_queries(count=120, rng=random.Random(evaluation_seed + 4))


@pytest.fixture(scope="session")
def security_events(evaluation_seed: int):
    return generate_security_events(count=80, rng=random.Random(evaluation_seed + 5))


@pytest.fixture(scope="session")
def metrics_store() -> MetricsStore:
    return MetricsStore()
