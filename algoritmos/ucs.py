# algoritmos/ucs.py
# Búsqueda de Costo Uniforme — igual que el apunte del maestro
# pero adaptado a estados de México con pesos de peligrosidad

def buscar_ucs(grafo: dict, inicio: str, destino: str) -> dict:
    nodos_frontera = []   # [costo_acumulado, ciudad, camino]
    nodos_visitados = []

    nodos_frontera.append([0, inicio, [inicio]])

    while nodos_frontera:
        # Ordenar por costo acumulado g(n) — cola de prioridad
        nodos_frontera.sort(key=lambda x: x[0])
        costo_actual, ciudad_actual, camino = nodos_frontera.pop(0)

        if ciudad_actual in nodos_visitados:
            continue
        nodos_visitados.append(ciudad_actual)

        if ciudad_actual == destino:
            return {
                "ruta":        camino,
                "costo_total": costo_actual,
                "pasos":       len(camino) - 1,
                "visitados":   nodos_visitados,
            }

        if ciudad_actual not in grafo:
            continue

        for vecino, costo in grafo[ciudad_actual].items():
            if vecino not in nodos_visitados:
                nuevo_costo  = costo_actual + costo
                nuevo_camino = camino + [vecino]
                nodos_frontera.append([nuevo_costo, vecino, nuevo_camino])

    return {"error": f"No existe ruta de {inicio} a {destino}"}