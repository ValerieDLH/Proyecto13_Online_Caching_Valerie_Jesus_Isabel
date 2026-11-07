from __future__ import annotations

import argparse
from typing import List

from src.cache_algorithms import simulate


def parse_sequence(text: str) -> List[int]:
    """
    Convierte una secuencia como:
    1,2,3,1,4,2,5
    en una lista de enteros.
    """
    text = text.strip()
    if not text:
        return []
    return [int(item.strip()) for item in text.split(",")]


def print_result(result, show_steps: bool = True):
    print("\n" + "=" * 72)
    print(f"ALGORITMO: {result.algorithm}")
    print("=" * 72)

    if show_steps:
        print(
            f"{'Paso':<6}{'Acceso':<10}{'Resultado':<12}"
            f"{'Expulsado':<12}{'Caché'}"
        )
        print("-" * 72)

        for step in result.steps:
            state = "HIT" if step.hit else "MISS"
            evicted = "-" if step.evicted is None else str(step.evicted)
            print(
                f"{step.index + 1:<6}{str(step.page):<10}{state:<12}"
                f"{evicted:<12}{step.cache}"
            )

    print("-" * 72)
    print(f"Accesos       : {result.accesses}")
    print(f"Aciertos (hit): {result.hits}")
    print(f"Fallos (miss) : {result.misses}")
    print(f"Reemplazos    : {result.replacements}")
    print(f"Tasa de hit   : {result.hit_rate * 100:.2f}%")
    print(f"Tasa de fallo : {result.miss_rate * 100:.2f}%")


def compare_all(sequence, capacity, show_steps=False):
    results = [
        simulate("fifo", sequence, capacity),
        simulate("lru", sequence, capacity),
        simulate("opt", sequence, capacity),
    ]

    if show_steps:
        for result in results:
            print_result(result, show_steps=True)

    print("\nCOMPARACIÓN GENERAL")
    print("=" * 72)
    print(
        f"{'Algoritmo':<12}{'Hits':<10}{'Misses':<10}"
        f"{'Reemplazos':<14}{'Miss rate':<12}"
    )
    print("-" * 72)
    for result in results:
        print(
            f"{result.algorithm:<12}"
            f"{result.hits:<10}"
            f"{result.misses:<10}"
            f"{result.replacements:<14}"
            f"{result.miss_rate * 100:>7.2f}%"
        )

    best = min(results, key=lambda r: r.misses)
    print("-" * 72)
    print(f"Menor número de fallos: {best.algorithm} ({best.misses})")


def interactive_mode():
    print("PROYECTO 13 - ONLINE CACHING Y ESTRATEGIAS DE REEMPLAZO")
    print("FIFO vs LRU vs OPT\n")

    while True:
        raw = input(
            "Ingrese la secuencia de accesos separada por comas\n"
            "(ejemplo: 1,2,3,1,4,2,5): "
        )
        try:
            sequence = parse_sequence(raw)
            if not sequence:
                print("La secuencia no puede estar vacía.\n")
                continue
            break
        except ValueError:
            print("La secuencia debe contener solo enteros.\n")

    while True:
        try:
            capacity = int(input("Capacidad de la caché: "))
            if capacity <= 0:
                raise ValueError
            break
        except ValueError:
            print("La capacidad debe ser un entero mayor que 0.")

    print("\nOpciones:")
    print("1. FIFO")
    print("2. LRU")
    print("3. OPT")
    print("4. Comparar los tres")

    option = input("Seleccione una opción: ").strip()

    mapping = {"1": "fifo", "2": "lru", "3": "opt"}

    if option in mapping:
        result = simulate(mapping[option], sequence, capacity)
        print_result(result, show_steps=True)
    elif option == "4":
        compare_all(sequence, capacity, show_steps=True)
    else:
        print("Opción no válida.")


def main():
    parser = argparse.ArgumentParser(
        description="Simulador de reemplazo de caché: FIFO, LRU y OPT."
    )
    parser.add_argument(
        "--sequence",
        help="Secuencia separada por comas. Ejemplo: 1,2,3,1,4,2,5",
    )
    parser.add_argument("--capacity", type=int, help="Capacidad de la caché.")
    parser.add_argument(
        "--algorithm",
        choices=["fifo", "lru", "opt", "all"],
        default="all",
    )
    parser.add_argument(
        "--steps",
        action="store_true",
        help="Muestra la simulación paso a paso.",
    )
    args = parser.parse_args()

    if args.sequence is None or args.capacity is None:
        interactive_mode()
        return

    sequence = parse_sequence(args.sequence)

    if args.algorithm == "all":
        compare_all(sequence, args.capacity, show_steps=args.steps)
    else:
        result = simulate(args.algorithm, sequence, args.capacity)
        print_result(result, show_steps=args.steps)


if __name__ == "__main__":
    main()
