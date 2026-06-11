# algoritmos/genetico.py
# Algoritmo Genético para ruteo — búsqueda local
# Genera población de rutas, las evalúa, cruza y muta

import random


def calcular_costo_ruta(ruta: list, grafo: dict) -> float:
    """Suma el costo total de una ruta. Retorna infinito si no es válida."""
    costo = 0
    for i in range(len(ruta) - 1):
        ciudad_a = ruta[i]
        ciudad_b = ruta[i + 1]
        if ciudad_a not in grafo or ciudad_b not in grafo[ciudad_a]:
            return float("inf")
        costo += grafo[ciudad_a][ciudad_b]
    return costo


def generar_ruta_aleatoria(inicio: str, destino: str, ciudades: list) -> list:
    """Genera una ruta aleatoria que empieza en inicio y termina en destino."""
    intermedias = [c for c in ciudades if c != inicio and c != destino]
    random.shuffle(intermedias)
    # Tomar solo 2-4 intermedias para rutas razonables
    n = random.randint(0, min(3, len(intermedias)))
    return [inicio] + intermedias[:n] + [destino]


def cruzar(padre1: list, padre2: list) -> list:
    """Cruce de un punto — toma la primera mitad de padre1 y completa con padre2."""
    if len(padre1) <= 2:
        return padre1
    punto = random.randint(1, len(padre1) - 1)
    hijo = padre1[:punto]
    for ciudad in padre2:
        if ciudad not in hijo:
            hijo.append(ciudad)
    # Asegurar que termina en el destino
    if hijo[-1] != padre1[-1]:
        hijo.append(padre1[-1])
    return hijo


def mutar(ruta: list, tasa: float = 0.2) -> list:
    """Intercambia dos ciudades intermedias aleatoriamente."""
    if random.random() < tasa and len(ruta) > 3:
        intermedias = ruta[1:-1]
        i, j = random.sample(range(len(intermedias)), 2)
        intermedias[i], intermedias[j] = intermedias[j], intermedias[i]
        return [ruta[0]] + intermedias + [ruta[-1]]
    return ruta


def buscar_genetico(
    grafo:       dict,
    inicio:      str,
    destino:     str,
    generaciones: int = 100,
    poblacion:   int  = 50,
) -> dict:
    ciudades = list(grafo.keys())

    if inicio not in ciudades or destino not in ciudades:
        return {"error": f"Ciudad no encontrada en el grafo"}

    # Población inicial
    poblacion_actual = [
        generar_ruta_aleatoria(inicio, destino, ciudades)
        for _ in range(poblacion)
    ]

    mejor_ruta  = None
    mejor_costo = float("inf")

    for gen in range(generaciones):
        # Evaluar
        evaluados = [
            (ruta, calcular_costo_ruta(ruta, grafo))
            for ruta in poblacion_actual
        ]
        evaluados.sort(key=lambda x: x[1])

        # Guardar el mejor global
        if evaluados[0][1] < mejor_costo:
            mejor_costo = evaluados[0][1]
            mejor_ruta  = evaluados[0][0]

        # Selección — top 50%
        seleccionados = [r for r, _ in evaluados[: poblacion // 2]]

        # Nueva generación: cruce + mutación
        nueva_poblacion = seleccionados[:]
        while len(nueva_poblacion) < poblacion:
            p1, p2 = random.sample(seleccionados, 2)
            hijo = mutar(cruzar(p1, p2))
            nueva_poblacion.append(hijo)

        poblacion_actual = nueva_poblacion

    if mejor_ruta is None or mejor_costo == float("inf"):
        return {"error": f"No se encontró ruta válida de {inicio} a {destino}"}

    return {
        "ruta":         mejor_ruta,
        "costo_total":  round(mejor_costo, 2),
        "pasos":        len(mejor_ruta) - 1,
        "generaciones": generaciones,
    }