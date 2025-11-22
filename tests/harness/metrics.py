from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, MutableMapping

RESULT_COLUMNS: List[str] = [
    "TaskCompletionRate_pct",
    "WorkflowRecoveryRate_pct",
    "LocalProcessingRatio_pct",
    "MemoryRetrievalAccuracy_pct",
    "SecurityDetectionAccuracy_pct",
    "AvgLatency_ms",
]


class MetricsStore:
    """Lightweight in-memory registry for evaluation metrics."""

    def __init__(self) -> None:
        self._store: MutableMapping[str, Dict[str, float]] = defaultdict(dict)

    def record(self, system: str, metric: str, value: float) -> None:
        self._store[system][metric] = float(value)

    def get_metric(self, system: str, metric: str, default: float | None = None) -> float | None:
        return self._store.get(system, {}).get(metric, default)

    def system_metrics(self, system: str) -> Dict[str, float]:
        return dict(self._store.get(system, {}))

    def iter_rows(self, *, columns: Iterable[str] = RESULT_COLUMNS) -> Iterator[Dict[str, float]]:
        ordered_columns = list(columns)
        for system, metrics in self._store.items():
            row = {col: metrics.get(col) for col in ordered_columns}
            row["System"] = system
            yield row

    def as_dict(self) -> Dict[str, Dict[str, float]]:
        return {system: dict(metrics) for system, metrics in self._store.items()}


def ensure_all_columns(row: Dict[str, float], *, columns: Iterable[str] = RESULT_COLUMNS) -> Dict[str, float]:
    completed = dict(row)
    for column in columns:
        completed.setdefault(column, 0.0)
    return completed
