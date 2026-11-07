from __future__ import annotations

import argparse
import csv
import statistics
import time
from collections import defaultdict
from pathlib import Path

from src.analysis import competitive_ratio
from src.cache_algorithms import simulate
from src.sequence_generators import cyclic_sequence, locality_sequence, uniform_sequence


def generate_sequence(kind: str, length: int, universe_size: int, seed: int):
    if kind == "uniform":
        return uniform_sequence(length, universe_size, seed)
    if kind == "locality":
        return locality_sequence(length, universe_size, seed=seed)
    if kind == "cyclic":
        return cyclic_sequence(length, universe_size)
    raise ValueError(f"Tipo de secuencia no soportado: {kind}")


def run_experiments(
    capacities=(3, 5, 10, 20),
    lengths=(100, 1000, 10000),
    sequence_types=("uniform", "locality", "cyclic"),
    trials=5,
    universe_size=50,
):
    rows = []

    for sequence_type in sequence_types:
        for length in lengths:
            for trial in range(trials):
                seed = 1000 + trial
                sequence = generate_sequence(
                    sequence_type, length, universe_size, seed
                )

                for capacity in capacities:
                    opt_result = simulate("opt", sequence, capacity)

                    for algorithm in ("fifo", "lru", "opt"):
                        start = time.perf_counter()
                        result = simulate(algorithm, sequence, capacity)
                        elapsed_ms = (time.perf_counter() - start) * 1000

                        rows.append({
                            "sequence_type": sequence_type,
                            "length": length,
                            "trial": trial + 1,
                            "seed": seed,
                            "capacity": capacity,
                            "algorithm": result.algorithm,
                            "accesses": result.accesses,
                            "hits": result.hits,
                            "misses": result.misses,
                            "replacements": result.replacements,
                            "hit_rate": result.hit_rate,
                            "miss_rate": result.miss_rate,
                            "ratio_vs_opt": competitive_ratio(
                                result.misses,
                                opt_result.misses,
                            ),
                            "elapsed_ms": elapsed_ms,
                        })

    return rows


def save_csv(rows, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize_rows(rows):
    groups = defaultdict(list)
    for row in rows:
        key = (
            row["sequence_type"],
            row["length"],
            row["capacity"],
            row["algorithm"],
        )
        groups[key].append(row)

    summary = []
    for (sequence_type, length, capacity, algorithm), items in groups.items():
        summary.append({
            "sequence_type": sequence_type,
            "length": length,
            "capacity": capacity,
            "algorithm": algorithm,
            "avg_misses": statistics.mean(x["misses"] for x in items),
            "avg_miss_rate": statistics.mean(x["miss_rate"] for x in items),
            "avg_ratio_vs_opt": statistics.mean(x["ratio_vs_opt"] for x in items),
            "avg_elapsed_ms": statistics.mean(x["elapsed_ms"] for x in items),
        })

    summary.sort(
        key=lambda x: (
            x["sequence_type"],
            x["length"],
            x["capacity"],
            x["algorithm"],
        )
    )
    return summary


def make_plots(summary, output_dir: Path):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib no está instalado. Se omiten las gráficas.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    max_length = max(row["length"] for row in summary)

    for sequence_type in sorted({row["sequence_type"] for row in summary}):
        subset = [
            row for row in summary
            if row["sequence_type"] == sequence_type
            and row["length"] == max_length
        ]

        capacities = sorted({row["capacity"] for row in subset})

        plt.figure(figsize=(8, 5))
        for algorithm in ("FIFO", "LRU", "OPT"):
            ys = []
            for capacity in capacities:
                match = next(
                    row for row in subset
                    if row["algorithm"] == algorithm
                    and row["capacity"] == capacity
                )
                ys.append(match["avg_miss_rate"] * 100)

            plt.plot(capacities, ys, marker="o", label=algorithm)

        plt.title(
            f"Tasa promedio de fallos - {sequence_type} "
            f"(n={max_length})"
        )
        plt.xlabel("Capacidad de caché")
        plt.ylabel("Tasa de fallos (%)")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(
            output_dir / f"miss_rate_{sequence_type}.png",
            dpi=150,
        )
        plt.close()

        plt.figure(figsize=(8, 5))
        for algorithm in ("FIFO", "LRU"):
            ys = []
            for capacity in capacities:
                match = next(
                    row for row in subset
                    if row["algorithm"] == algorithm
                    and row["capacity"] == capacity
                )
                ys.append(match["avg_ratio_vs_opt"])

            plt.plot(capacities, ys, marker="o", label=algorithm)

        plt.axhline(1.0, linestyle="--", linewidth=1)
        plt.title(
            f"Ratio empírico vs OPT - {sequence_type} "
            f"(n={max_length})"
        )
        plt.xlabel("Capacidad de caché")
        plt.ylabel("Misses(online) / Misses(OPT)")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(
            output_dir / f"ratio_vs_opt_{sequence_type}.png",
            dpi=150,
        )
        plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Experimentos para FIFO, LRU y OPT."
    )
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--universe", type=int, default=50)
    parser.add_argument(
        "--output",
        default="results",
        help="Carpeta donde se guardarán CSV y gráficas.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)

    rows = run_experiments(
        trials=args.trials,
        universe_size=args.universe,
    )

    raw_path = output_dir / "experiments_raw.csv"
    summary_path = output_dir / "experiments_summary.csv"

    save_csv(rows, raw_path)
    summary = summarize_rows(rows)
    save_csv(summary, summary_path)
    make_plots(summary, output_dir)

    print("Experimentos terminados.")
    print(f"Resultados detallados: {raw_path}")
    print(f"Resumen: {summary_path}")


if __name__ == "__main__":
    main()
