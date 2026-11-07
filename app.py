from __future__ import annotations

from io import StringIO
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.analysis import (
    canonical_belady_example,
    comparison_rows,
    competitive_ratio,
    detect_belady,
)
from src.cache_algorithms import simulate
from src.sequence_generators import cyclic_sequence, locality_sequence, uniform_sequence


st.set_page_config(
    page_title="Online Caching Simulator",
    page_icon="🧠",
    layout="wide",
)

st.title("Online Caching Simulator")
st.caption("Proyecto 13 · FIFO vs LRU vs OPT · Algoritmos y Complejidad")


def parse_sequence(text: str) -> list[int]:
    text = text.strip()
    if not text:
        return []
    values = []
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        values.append(int(item))
    return values


def steps_dataframe(result) -> pd.DataFrame:
    rows = []
    for step in result.steps:
        rows.append({
            "Paso": step.index + 1,
            "Acceso": step.page,
            "Resultado": "HIT" if step.hit else "MISS",
            "Expulsado": "-" if step.evicted is None else step.evicted,
            "Caché": str(step.cache),
        })
    return pd.DataFrame(rows)


def render_summary_cards(result, opt_misses: int | None = None):
    cols = st.columns(5)
    cols[0].metric("Accesos", result.accesses)
    cols[1].metric("Hits", result.hits)
    cols[2].metric("Misses", result.misses)
    cols[3].metric("Miss rate", f"{result.miss_rate * 100:.2f}%")

    if opt_misses is None:
        cols[4].metric("Reemplazos", result.replacements)
    else:
        ratio = competitive_ratio(result.misses, opt_misses)
        cols[4].metric("Ratio vs OPT", f"{ratio:.3f}")


def generate_sequence(kind: str, length: int, universe: int, seed: int, hot_probability: float):
    if kind == "Uniforme":
        return uniform_sequence(length, universe, seed)
    if kind == "Localidad temporal":
        return locality_sequence(
            length,
            universe,
            hot_probability=hot_probability,
            seed=seed,
        )
    if kind == "Cíclica":
        return cyclic_sequence(length, universe)
    raise ValueError("Tipo de secuencia no soportado.")


tab_sim, tab_exp, tab_belady, tab_theory = st.tabs(
    ["Simulación", "Experimentos", "Belady", "Teoría"]
)

with tab_sim:
    st.subheader("Simulación paso a paso")

    mode = st.radio(
        "Origen de la secuencia",
        ["Manual", "Generada automáticamente"],
        horizontal=True,
    )

    if mode == "Manual":
        sequence_text = st.text_input(
            "Secuencia de accesos",
            value="1,2,3,4,1,2,5,1,2,3,4,5",
            help="Ingrese enteros separados por comas.",
        )
        try:
            sequence = parse_sequence(sequence_text)
        except ValueError:
            sequence = []
            st.error("La secuencia manual solo puede contener números enteros.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        seq_kind = c1.selectbox(
            "Tipo",
            ["Uniforme", "Localidad temporal", "Cíclica"],
        )
        seq_length = c2.number_input("Longitud", min_value=1, value=30, step=1)
        universe = c3.number_input("Universo", min_value=1, value=8, step=1)
        seed = c4.number_input("Semilla", min_value=0, value=42, step=1)
        hot_probability = st.slider(
            "Probabilidad de acceder al conjunto caliente",
            min_value=0.50,
            max_value=0.99,
            value=0.85,
            step=0.01,
            disabled=seq_kind != "Localidad temporal",
        )
        sequence = generate_sequence(
            seq_kind,
            int(seq_length),
            int(universe),
            int(seed),
            float(hot_probability),
        )
        st.code(",".join(map(str, sequence)), language=None)

    c1, c2 = st.columns(2)
    capacity = int(
        c1.number_input(
            "Capacidad de caché",
            min_value=1,
            value=3,
            step=1,
        )
    )
    selected_algorithms = c2.multiselect(
        "Algoritmos",
        ["FIFO", "LRU", "OPT"],
        default=["FIFO", "LRU", "OPT"],
    )

    if st.button("Ejecutar simulación", type="primary", use_container_width=True):
        if not sequence:
            st.error("La secuencia no puede estar vacía.")
        elif not selected_algorithms:
            st.error("Seleccione al menos un algoritmo.")
        else:
            st.session_state["simulation_sequence"] = sequence
            st.session_state["simulation_capacity"] = capacity
            st.session_state["simulation_algorithms"] = selected_algorithms

    if "simulation_sequence" in st.session_state:
        sequence = st.session_state["simulation_sequence"]
        capacity = st.session_state["simulation_capacity"]
        selected_algorithms = st.session_state["simulation_algorithms"]

        opt_result = simulate("opt", sequence, capacity)
        rows = []

        for label in selected_algorithms:
            result = simulate(label.lower(), sequence, capacity)

            st.markdown(f"### {label}")
            render_summary_cards(result, opt_result.misses)

            df_steps = steps_dataframe(result)
            st.dataframe(
                df_steps,
                use_container_width=True,
                hide_index=True,
            )

            rows.append({
                "Algoritmo": label,
                "Hits": result.hits,
                "Misses": result.misses,
                "Reemplazos": result.replacements,
                "Hit rate (%)": result.hit_rate * 100,
                "Miss rate (%)": result.miss_rate * 100,
                "Ratio vs OPT": competitive_ratio(result.misses, opt_result.misses),
            })

        st.markdown("### Comparación")

        df_compare = pd.DataFrame(rows)
        st.dataframe(
            df_compare.style.format({
                "Hit rate (%)": "{:.2f}",
                "Miss rate (%)": "{:.2f}",
                "Ratio vs OPT": "{:.3f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.bar(df_compare["Algoritmo"], df_compare["Misses"])
        ax.set_title("Fallos de caché por algoritmo")
        ax.set_xlabel("Algoritmo")
        ax.set_ylabel("Misses")
        ax.grid(axis="y", alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)

        csv_data = df_compare.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Descargar comparación en CSV",
            data=csv_data,
            file_name="comparacion_cache.csv",
            mime="text/csv",
        )

with tab_exp:
    st.subheader("Experimentos reproducibles")
    st.write(
        "Esta sección ejecuta múltiples configuraciones sobre la misma familia de "
        "secuencias y compara FIFO, LRU y OPT."
    )

    c1, c2, c3 = st.columns(3)
    exp_kind = c1.selectbox(
        "Tipo de secuencia",
        ["Uniforme", "Localidad temporal", "Cíclica"],
        key="exp_kind",
    )
    exp_length = int(
        c2.number_input(
            "Longitud por secuencia",
            min_value=10,
            max_value=100000,
            value=1000,
            step=10,
        )
    )
    exp_universe = int(
        c3.number_input(
            "Universo de páginas",
            min_value=2,
            value=50,
            step=1,
        )
    )

    c4, c5, c6 = st.columns(3)
    capacities_text = c4.text_input("Capacidades", value="3,5,10,20")
    trials = int(
        c5.number_input(
            "Repeticiones",
            min_value=1,
            max_value=50,
            value=5,
            step=1,
        )
    )
    base_seed = int(
        c6.number_input(
            "Semilla base",
            min_value=0,
            value=2026,
            step=1,
        )
    )

    exp_hot_probability = st.slider(
        "Probabilidad del conjunto caliente",
        min_value=0.50,
        max_value=0.99,
        value=0.85,
        step=0.01,
        key="exp_hot",
        disabled=exp_kind != "Localidad temporal",
    )

    run_experiment = st.button(
        "Ejecutar experimentos",
        type="primary",
        use_container_width=True,
    )

    if run_experiment:
        try:
            capacities = sorted(
                {int(x.strip()) for x in capacities_text.split(",") if x.strip()}
            )
            if any(c <= 0 for c in capacities):
                raise ValueError
        except ValueError:
            st.error("Las capacidades deben ser enteros positivos separados por comas.")
            capacities = []

        if capacities:
            progress = st.progress(0)
            total = trials * len(capacities) * 3
            done = 0
            experiment_rows = []

            for trial in range(trials):
                seed = base_seed + trial
                sequence = generate_sequence(
                    exp_kind,
                    exp_length,
                    exp_universe,
                    seed,
                    exp_hot_probability,
                )

                for capacity_value in capacities:
                    opt = simulate("opt", sequence, capacity_value)

                    for algorithm in ("fifo", "lru", "opt"):
                        result = simulate(algorithm, sequence, capacity_value)
                        experiment_rows.append({
                            "Tipo": exp_kind,
                            "Trial": trial + 1,
                            "Semilla": seed,
                            "Capacidad": capacity_value,
                            "Algoritmo": result.algorithm,
                            "Hits": result.hits,
                            "Misses": result.misses,
                            "Hit rate (%)": result.hit_rate * 100,
                            "Miss rate (%)": result.miss_rate * 100,
                            "Ratio vs OPT": competitive_ratio(result.misses, opt.misses),
                        })
                        done += 1
                        progress.progress(done / total)

            st.session_state["experiment_rows"] = experiment_rows

    if "experiment_rows" in st.session_state:
        df = pd.DataFrame(st.session_state["experiment_rows"])

        summary = (
            df.groupby(["Capacidad", "Algoritmo"], as_index=False)
            .agg({
                "Hits": "mean",
                "Misses": "mean",
                "Hit rate (%)": "mean",
                "Miss rate (%)": "mean",
                "Ratio vs OPT": "mean",
            })
        )

        st.markdown("### Resumen promedio")
        st.dataframe(
            summary.style.format({
                "Hits": "{:.2f}",
                "Misses": "{:.2f}",
                "Hit rate (%)": "{:.2f}",
                "Miss rate (%)": "{:.2f}",
                "Ratio vs OPT": "{:.3f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

        fig, ax = plt.subplots(figsize=(8, 4.5))
        for algorithm in ["FIFO", "LRU", "OPT"]:
            subset = summary[summary["Algoritmo"] == algorithm]
            ax.plot(
                subset["Capacidad"],
                subset["Miss rate (%)"],
                marker="o",
                label=algorithm,
            )
        ax.set_title("Tasa de fallos vs capacidad")
        ax.set_xlabel("Capacidad")
        ax.set_ylabel("Miss rate (%)")
        ax.grid(alpha=0.3)
        ax.legend()
        st.pyplot(fig)
        plt.close(fig)

        fig2, ax2 = plt.subplots(figsize=(8, 4.5))
        for algorithm in ["FIFO", "LRU"]:
            subset = summary[summary["Algoritmo"] == algorithm]
            ax2.plot(
                subset["Capacidad"],
                subset["Ratio vs OPT"],
                marker="o",
                label=algorithm,
            )
        ax2.axhline(1.0, linestyle="--", linewidth=1)
        ax2.set_title("Ratio competitivo empírico vs OPT")
        ax2.set_xlabel("Capacidad")
        ax2.set_ylabel("Misses(online) / Misses(OPT)")
        ax2.grid(alpha=0.3)
        ax2.legend()
        st.pyplot(fig2)
        plt.close(fig2)

        st.download_button(
            "Descargar resultados completos en CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="experimentos_online_caching.csv",
            mime="text/csv",
        )

with tab_belady:
    st.subheader("Anomalía de Belady")
    st.write(
        "FIFO puede producir más fallos incluso cuando se aumenta la capacidad de la caché. "
        "Esta sección incluye un caso clásico para observar ese comportamiento."
    )

    sequence, capacities = canonical_belady_example()

    st.code(",".join(map(str, sequence)), language=None)

    result_rows = detect_belady(sequence, capacities)
    df_belady = pd.DataFrame([
        {
            "Capacidad": row["capacity"],
            "Fallos FIFO": row["fifo_misses"],
            "¿Anomalía?": "Sí" if row["belady_anomaly"] else "No",
        }
        for row in result_rows
    ])

    st.dataframe(df_belady, use_container_width=True, hide_index=True)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(
        [str(row["capacity"]) for row in result_rows],
        [row["fifo_misses"] for row in result_rows],
    )
    ax.set_title("FIFO: anomalía de Belady")
    ax.set_xlabel("Capacidad")
    ax.set_ylabel("Fallos")
    ax.grid(axis="y", alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    if any(row["belady_anomaly"] for row in result_rows):
        st.success(
            "Se detecta la anomalía: al pasar de capacidad 3 a 4, "
            "FIFO aumenta de 9 a 10 fallos."
        )
    else:
        st.warning("No se detectó anomalía en la configuración actual.")

with tab_theory:
    st.subheader("Conceptos del proyecto")

    st.markdown(
        """
### FIFO
Elimina el elemento que lleva más tiempo dentro de la caché.

### LRU
Elimina el elemento que lleva más tiempo sin utilizarse.

### OPT
Elimina el elemento cuyo próximo uso está más lejano en el futuro. Es una política
offline y se utiliza como referencia para medir qué tan lejos están las políticas
online de una solución óptima.

### Métricas
- **Hit:** el elemento solicitado ya estaba en caché.
- **Miss:** el elemento solicitado no estaba en caché.
- **Miss rate:** misses / accesos totales.
- **Ratio vs OPT:** misses del algoritmo / misses de OPT.

Un valor del ratio cercano a 1 indica que el algoritmo online se acercó al óptimo
para la secuencia evaluada.
"""
    )

    st.info(
        "La comparación experimental con OPT no demuestra por sí sola una cota "
        "competitiva teórica. En este proyecto se usa como análisis competitivo empírico "
        "sobre las secuencias simuladas."
    )
