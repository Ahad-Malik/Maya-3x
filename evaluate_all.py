from __future__ import annotations

import argparse
import pathlib
import random
from typing import Dict, Iterable, List, Sequence

import matplotlib.pyplot as plt
import pandas as pd

from tests.harness.data_generation import (
    generate_memory_queries,
    generate_privacy_queries,
    generate_security_events,
    generate_task_scenarios,
    generate_voice_queries,
    select_interrupted_workflows,
)
from tests.harness.metrics import RESULT_COLUMNS, MetricsStore
from tests.harness.suites import (
    record_metrics,
    run_memory_metrics,
    run_privacy_metrics,
    run_security_metrics,
    run_task_performance,
    run_voice_metrics,
    run_workflow_recovery,
)
from tests.harness.systems import MockSystem, get_systems

EVALUATION_SEED = 2024


def build_results_dataframe(
    store: MetricsStore, systems: Sequence[MockSystem]
) -> pd.DataFrame:
    rows: List[Dict[str, float]] = []
    for system in systems:
        metrics = store.system_metrics(system.name)
        row = {"System": system.display_name}
        for column in RESULT_COLUMNS:
            row[column] = metrics.get(column, 0.0)
        rows.append(row)
    return pd.DataFrame(rows)


def write_results_csv(df: pd.DataFrame, output_path: pathlib.Path) -> None:
    ordered_columns = ["System", *RESULT_COLUMNS]
    df[ordered_columns].to_csv(output_path, index=False)


def plot_grouped_bars(df: pd.DataFrame, output_path: pathlib.Path) -> None:
    percentage_cols = [col for col in RESULT_COLUMNS if col.endswith("_pct")]
    ax = df.set_index("System")[percentage_cols].plot(kind="bar", figsize=(11, 6))
    ax.set_ylabel("Percentage")
    ax.set_ylim(0, 105)
    ax.set_title("Maya-3x Comparative Evaluation (Durability, Privacy, Memory, Security)")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)
    plt.tight_layout(rect=(0, 0, 0.82, 1))
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_latency_bars(df: pd.DataFrame, output_path: pathlib.Path) -> None:
    ax = df.set_index("System")["AvgLatency_ms"].plot(kind="bar", color="#1f77b4", figsize=(8, 5))
    ax.set_ylabel("Average Latency (ms)")
    ax.set_title("Realtime Latency Comparison")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_radar_chart(df: pd.DataFrame, output_path: pathlib.Path) -> None:
    import math

    percentage_cols = [col for col in RESULT_COLUMNS if col.endswith("_pct")]
    metrics = df.set_index("System")[percentage_cols]
    labels = percentage_cols
    angles = [n / float(len(labels)) * 2 * math.pi for n in range(len(labels))]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    for system, values in metrics.iterrows():
        data = values.tolist()
        data += data[:1]
        ax.plot(angles, data, label=system)
        ax.fill(angles, data, alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 105)
    ax.set_title("Radar View: Percentage Metrics")
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def ensure_output_dir(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def run_evaluation(mode: str, output_dir: pathlib.Path) -> pd.DataFrame:
    systems = get_systems(mode, seed=EVALUATION_SEED)
    store = MetricsStore()

    task_scenarios = generate_task_scenarios(count=100, rng=random.Random(EVALUATION_SEED))
    interrupted = select_interrupted_workflows(
        task_scenarios, ratio=0.5, rng=random.Random(EVALUATION_SEED + 1)
    )
    voice_queries = generate_voice_queries(count=1000, rng=random.Random(EVALUATION_SEED + 2))
    privacy_queries = generate_privacy_queries(count=200, rng=random.Random(EVALUATION_SEED + 3))
    memory_queries = generate_memory_queries(count=120, rng=random.Random(EVALUATION_SEED + 4))
    security_events = generate_security_events(count=80, rng=random.Random(EVALUATION_SEED + 5))

    for system in systems:
        record_metrics(store, system, run_task_performance(system, task_scenarios))
        record_metrics(store, system, run_workflow_recovery(system, task_scenarios, interrupted))
        record_metrics(store, system, run_voice_metrics(system, voice_queries))
        record_metrics(store, system, run_privacy_metrics(system, privacy_queries))
        record_metrics(store, system, run_memory_metrics(system, memory_queries))
        record_metrics(store, system, run_security_metrics(system, security_events))

    df = build_results_dataframe(store, systems)

    ensure_output_dir(output_dir)
    write_results_csv(df, output_dir / "results.csv")
    plot_grouped_bars(df, output_dir / "durability_privacy_memory_security.png")
    plot_latency_bars(df, output_dir / "latency.png")
    plot_radar_chart(df, output_dir / "radar.png")

    caption = (
        "Figure X — Comparative evaluation of Maya-3x against Maya-1x and a Baseline Agent across "
        "production-oriented metrics. Metrics include task completion and recovery rates (durability), "
        "local processing ratio (privacy-first behavior), memory retrieval effectiveness (GraphRAG), "
        "security detection accuracy, and average end-to-end latency for multimodal interactions. "
        "Results are aggregated over standardized test suites described in the Methods section."
    )
    (output_dir / "figure_caption.txt").write_text(caption, encoding="utf-8")

    return df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Maya evaluation harness and build artifacts.")
    parser.add_argument(
        "--mode",
        default="mock",
        choices=["mock"],
        help="Evaluation mode. 'mock' runs against synthetic harnesses only.",
    )
    parser.add_argument(
        "--output-dir",
        default="artifacts/eval",
        help="Directory where results.csv and charts will be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = pathlib.Path(args.output_dir)
    df = run_evaluation(args.mode, output_dir)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
