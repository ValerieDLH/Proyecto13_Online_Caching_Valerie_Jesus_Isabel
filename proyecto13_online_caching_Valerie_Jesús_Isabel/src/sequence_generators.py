from __future__ import annotations

import random
from typing import List


def uniform_sequence(length: int, universe_size: int, seed: int | None = None) -> List[int]:
    """Accesos uniformemente aleatorios dentro de [0, universe_size-1]."""
    if length < 0 or universe_size <= 0:
        raise ValueError("length debe ser >= 0 y universe_size debe ser > 0.")
    rng = random.Random(seed)
    return [rng.randrange(universe_size) for _ in range(length)]


def locality_sequence(
    length: int,
    universe_size: int,
    hotset_size: int | None = None,
    hot_probability: float = 0.85,
    seed: int | None = None,
) -> List[int]:
    """
    Genera una secuencia con localidad temporal.

    La mayoría de accesos se concentra en un subconjunto pequeño (hot set),
    mientras una fracción menor accede al resto del universo.
    """
    if length < 0 or universe_size <= 0:
        raise ValueError("length debe ser >= 0 y universe_size debe ser > 0.")
    if not 0 <= hot_probability <= 1:
        raise ValueError("hot_probability debe estar entre 0 y 1.")

    if hotset_size is None:
        hotset_size = max(1, universe_size // 5)

    hotset_size = max(1, min(hotset_size, universe_size))
    rng = random.Random(seed)
    hot = list(range(hotset_size))
    cold = list(range(hotset_size, universe_size))

    sequence = []
    for _ in range(length):
        use_hot = rng.random() < hot_probability or not cold
        pool = hot if use_hot else cold
        sequence.append(rng.choice(pool))
    return sequence


def cyclic_sequence(length: int, working_set_size: int) -> List[int]:
    """Secuencia repetitiva 0,1,2,... que ayuda a estudiar patrones adversos."""
    if length < 0 or working_set_size <= 0:
        raise ValueError("length debe ser >= 0 y working_set_size debe ser > 0.")
    return [i % working_set_size for i in range(length)]
