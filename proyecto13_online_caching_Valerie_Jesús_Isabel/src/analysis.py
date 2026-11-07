from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

from src.cache_algorithms import simulate


@dataclass
class CompetitiveResult:
    algorithm: str
    misses: int
    opt_misses: int
    ratio: float


def competitive_ratio(misses: int, opt_misses: int) -> float:
    """
    Calcula misses(algoritmo) / misses(OPT).

    Si OPT tiene 0 fallos y el algoritmo también 0, se define como 1.0.
    Si OPT tiene 0 fallos y el algoritmo tiene >0, se devuelve infinito.
    """
    if opt_misses == 0:
        return 1.0 if misses == 0 else float("inf")
    return misses / opt_misses


def compare_against_opt(sequence: Sequence[int], capacity: int) -> List[CompetitiveResult]:
    """Compara FIFO y LRU contra OPT sobre la misma secuencia."""
    opt = simulate("opt", sequence, capacity)
    results = []

    for algorithm in ("fifo", "lru"):
        current = simulate(algorithm, sequence, capacity)
        results.append(
            CompetitiveResult(
                algorithm=current.algorithm,
                misses=current.misses,
                opt_misses=opt.misses,
                ratio=competitive_ratio(current.misses, opt.misses),
            )
        )

    return results


def comparison_rows(sequence: Sequence[int], capacity: int) -> List[dict]:
    """Devuelve una fila resumen por algoritmo, incluyendo ratio respecto a OPT."""
    results = {
        name: simulate(name, sequence, capacity)
        for name in ("fifo", "lru", "opt")
    }
    opt_misses = results["opt"].misses

    rows = []
    for name in ("fifo", "lru", "opt"):
        result = results[name]
        rows.append({
            "Algoritmo": result.algorithm,
            "Accesos": result.accesses,
            "Hits": result.hits,
            "Misses": result.misses,
            "Reemplazos": result.replacements,
            "Hit rate (%)": round(result.hit_rate * 100, 2),
            "Miss rate (%)": round(result.miss_rate * 100, 2),
            "Ratio vs OPT": round(competitive_ratio(result.misses, opt_misses), 3),
        })
    return rows


def detect_belady(sequence: Sequence[int], capacities: Iterable[int]) -> List[dict]:
    """
    Busca anomalías de Belady para FIFO.

    Una anomalía ocurre cuando aumentar la capacidad produce más fallos.
    """
    capacities = sorted(set(int(c) for c in capacities))
    if not capacities:
        return []

    results = []
    previous_capacity = None
    previous_misses = None

    for capacity in capacities:
        fifo = simulate("fifo", sequence, capacity)
        anomaly = (
            previous_misses is not None and
            fifo.misses > previous_misses
        )
        results.append({
            "capacity": capacity,
            "fifo_misses": fifo.misses,
            "previous_capacity": previous_capacity,
            "previous_misses": previous_misses,
            "belady_anomaly": anomaly,
        })
        previous_capacity = capacity
        previous_misses = fifo.misses

    return results


def canonical_belady_example() -> tuple[list[int], list[int]]:
    """
    Ejemplo clásico que muestra anomalía de Belady en FIFO:
    con 3 marcos hay 9 fallos y con 4 marcos hay 10.
    """
    sequence = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    capacities = [3, 4]
    return sequence, capacities
