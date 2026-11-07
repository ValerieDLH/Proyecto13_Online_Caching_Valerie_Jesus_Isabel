from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Hashable, Iterable, List, Optional, Sequence


@dataclass
class StepResult:
    """Estado de una política de caché después de procesar un acceso."""
    index: int
    page: Hashable
    hit: bool
    evicted: Optional[Hashable]
    cache: List[Hashable]


@dataclass
class SimulationResult:
    """Resumen completo de una simulación."""
    algorithm: str
    capacity: int
    accesses: int
    hits: int
    misses: int
    replacements: int
    steps: List[StepResult]

    @property
    def hit_rate(self) -> float:
        return self.hits / self.accesses if self.accesses else 0.0

    @property
    def miss_rate(self) -> float:
        return self.misses / self.accesses if self.accesses else 0.0

    def summary_dict(self) -> dict:
        return {
            "algorithm": self.algorithm,
            "capacity": self.capacity,
            "accesses": self.accesses,
            "hits": self.hits,
            "misses": self.misses,
            "replacements": self.replacements,
            "hit_rate": self.hit_rate,
            "miss_rate": self.miss_rate,
        }


def _validate(sequence: Sequence[Hashable], capacity: int) -> None:
    if capacity <= 0:
        raise ValueError("La capacidad de la caché debe ser mayor que 0.")
    if sequence is None:
        raise ValueError("La secuencia no puede ser None.")


def simulate_fifo(sequence: Sequence[Hashable], capacity: int) -> SimulationResult:
    """
    FIFO: elimina el elemento que lleva más tiempo dentro de la caché.

    Complejidad aproximada de esta implementación:
    - Tiempo: O(n * c) por comprobaciones de pertenencia en una lista.
    - Espacio: O(c + n) si se conserva el historial paso a paso.
    """
    _validate(sequence, capacity)

    cache: List[Hashable] = []
    steps: List[StepResult] = []
    hits = misses = replacements = 0

    for i, page in enumerate(sequence):
        hit = page in cache
        evicted = None

        if hit:
            hits += 1
        else:
            misses += 1
            if len(cache) >= capacity:
                evicted = cache.pop(0)
                replacements += 1
            cache.append(page)

        steps.append(StepResult(i, page, hit, evicted, cache.copy()))

    return SimulationResult(
        algorithm="FIFO",
        capacity=capacity,
        accesses=len(sequence),
        hits=hits,
        misses=misses,
        replacements=replacements,
        steps=steps,
    )


def simulate_lru(sequence: Sequence[Hashable], capacity: int) -> SimulationResult:
    """
    LRU: elimina el elemento que lleva más tiempo sin ser utilizado.

    La lista se mantiene del menos reciente al más reciente.
    """
    _validate(sequence, capacity)

    cache: List[Hashable] = []
    steps: List[StepResult] = []
    hits = misses = replacements = 0

    for i, page in enumerate(sequence):
        hit = page in cache
        evicted = None

        if hit:
            hits += 1
            cache.remove(page)
            cache.append(page)
        else:
            misses += 1
            if len(cache) >= capacity:
                evicted = cache.pop(0)
                replacements += 1
            cache.append(page)

        steps.append(StepResult(i, page, hit, evicted, cache.copy()))

    return SimulationResult(
        algorithm="LRU",
        capacity=capacity,
        accesses=len(sequence),
        hits=hits,
        misses=misses,
        replacements=replacements,
        steps=steps,
    )


def simulate_opt(sequence: Sequence[Hashable], capacity: int) -> SimulationResult:
    """
    OPT: elimina el elemento cuyo siguiente uso está más lejano en el futuro.

    Si un elemento de la caché no vuelve a aparecer, se elimina primero.
    OPT es offline porque necesita conocer la secuencia futura completa.
    """
    _validate(sequence, capacity)

    cache: List[Hashable] = []
    steps: List[StepResult] = []
    hits = misses = replacements = 0

    for i, page in enumerate(sequence):
        hit = page in cache
        evicted = None

        if hit:
            hits += 1
        else:
            misses += 1

            if len(cache) >= capacity:
                future = sequence[i + 1:]
                farthest_next_use = -1
                victim = None

                for cached_page in cache:
                    try:
                        next_use = future.index(cached_page)
                    except ValueError:
                        # No vuelve a aparecer: es el mejor candidato.
                        victim = cached_page
                        break

                    if next_use > farthest_next_use:
                        farthest_next_use = next_use
                        victim = cached_page

                evicted = victim
                cache.remove(victim)
                replacements += 1

            cache.append(page)

        steps.append(StepResult(i, page, hit, evicted, cache.copy()))

    return SimulationResult(
        algorithm="OPT",
        capacity=capacity,
        accesses=len(sequence),
        hits=hits,
        misses=misses,
        replacements=replacements,
        steps=steps,
    )


ALGORITHMS = {
    "fifo": simulate_fifo,
    "lru": simulate_lru,
    "opt": simulate_opt,
}


def simulate(algorithm: str, sequence: Sequence[Hashable], capacity: int) -> SimulationResult:
    """Ejecuta una política por nombre: fifo, lru u opt."""
    key = algorithm.strip().lower()
    if key not in ALGORITHMS:
        raise ValueError(
            f"Algoritmo desconocido: {algorithm}. "
            f"Opciones válidas: {', '.join(ALGORITHMS)}."
        )
    return ALGORITHMS[key](sequence, capacity)
