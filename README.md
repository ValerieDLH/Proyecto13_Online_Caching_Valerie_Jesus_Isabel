# Proyecto 13: Online Caching y Estrategias de Reemplazo

Curso: Algoritmos y Complejidad  
Proyecto: Online Caching y Estrategias de Reemplazo  
Algoritmos: FIFO, LRU y OPT

## Qué incluye esta versión

Esta implementación cubre el núcleo del proyecto y añade una interfaz visual para
facilitar el análisis y la exposición.

### Implementación algorítmica

- FIFO
- LRU
- OPT
- Simulación paso a paso
- Hits
- Misses
- Reemplazos
- Hit rate
- Miss rate

### Análisis competitivo empírico

Para FIFO y LRU se calcula:

```text
misses(algoritmo) / misses(OPT)
```

OPT se utiliza como referencia offline.

Este valor se interpreta de forma empírica sobre cada secuencia simulada. No se
presenta como demostración de una cota competitiva teórica.

### Experimentos

La aplicación permite:

- secuencias uniformemente aleatorias
- secuencias con localidad temporal
- secuencias cíclicas
- múltiples capacidades
- múltiples repeticiones
- semillas reproducibles

### Anomalía de Belady

Se incluye el caso clásico:

```text
1,2,3,4,1,2,5,1,2,3,4,5
```

Con FIFO:

- capacidad 3 -> 9 fallos
- capacidad 4 -> 10 fallos

Esto muestra que aumentar la caché no garantiza reducir los fallos cuando se usa FIFO.

### Interfaz gráfica

La aplicación Streamlit contiene cuatro pestañas:

1. Simulación
2. Experimentos
3. Belady
4. Teoría

También permite exportar resultados a CSV.

---

## Estructura

```text
proyecto13_online_caching/
├── app.py
├── main.py
├── experiments.py
├── ABRIR_INTERFAZ.bat
├── INSTALAR_DEPENDENCIAS.bat
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── analysis.py
│   ├── cache_algorithms.py
│   └── sequence_generators.py
├── tests/
│   └── test_algorithms.py
└── results/
```

---

## Opción recomendada en Windows

### Primera vez

Haz doble clic en:

```text
INSTALAR_DEPENDENCIAS.bat
```

Después haz doble clic en:

```text
ABRIR_INTERFAZ.bat
```

La aplicación se abrirá en el navegador.

---

## Abrir manualmente desde PowerShell

Instalar dependencias:

```bash
python -m pip install -r requirements.txt
```

Abrir la interfaz:

```bash
python -m streamlit run app.py
```

Si Windows usa `py`:

```bash
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

---

## Versión de consola

También se conserva la versión de consola:

```bash
python main.py
```

Ejemplo:

```bash
python main.py --sequence "1,2,3,1,4,2,5" --capacity 3 --algorithm all --steps
```

---

## Experimentos automáticos sin interfaz

```bash
python experiments.py
```

Se generan:

- CSV con resultados detallados
- CSV resumen
- gráficas de miss rate
- gráficas del ratio vs OPT

---

## Pruebas

```bash
python -m unittest discover -s tests -v
```

Las pruebas incluyen:

- resultados conocidos de FIFO
- resultados conocidos de LRU
- resultados conocidos de OPT
- validación de capacidad
- secuencia vacía
- competitive ratio
- propiedad empírica OPT <= FIFO y OPT <= LRU en 100 casos aleatorios
- anomalía de Belady clásica

---

## Qué mostrar durante la exposición

1. Abra la pestaña **Simulación**.
2. Use la secuencia:
   `1,2,3,4,1,2,5,1,2,3,4,5`
3. Seleccione capacidad 3.
4. Compare FIFO, LRU y OPT.
5. Muestre la tabla paso a paso.
6. Abra **Experimentos** y ejecute varias capacidades.
7. Explique la gráfica de miss rate.
8. Explique el ratio contra OPT.
9. Abra **Belady** y muestre que FIFO pasa de 9 a 10 fallos al aumentar
   la capacidad de 3 a 4.
10. Cierre explicando por qué OPT es una referencia offline y FIFO/LRU son
    políticas online.

---

## Alcance académico

La implementación busca cumplir con:

- estudio algorítmico
- implementación funcional
- comparación experimental
- análisis de fallos de caché
- comparación de políticas online frente a OPT
- reproducibilidad
- visualización de resultados

La interfaz es un complemento para la demostración y no reemplaza el análisis
teórico del informe.
