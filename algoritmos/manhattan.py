# algoritmos/manhattan.py
# Distancia Manhattan adaptada a coordenadas geográficas
# Se usa como heurística alternativa a geodist en A*
# En grids: |x1-x2| + |y1-y2|  →  aquí: |lat1-lat2| + |lon1-lon2| × factor

from algoritmos.a_estrella import COORDENADAS


def manhattan_dist(ciudad1: str, ciudad2: str) -> float:
    """h(n) Manhattan geográfico — diferencia absoluta de lat + lon en km"""
    if ciudad1 not in COORDENADAS or ciudad2 not in COORDENADAS:
        return 0.0
    lat1, lon1 = COORDENADAS[ciudad1]
    lat2, lon2 = COORDENADAS[ciudad2]
    return (abs(lat1 - lat2) + abs(lon1 - lon2)) * 111.32


def buscar_manhattan(grafo: dict, inicio: str, destino: str) -> dict:
    """A* usando heurística Manhattan en vez de geodésica"""
    nodos_frontera = [[manhattan_dist(inicio, destino), 0, inicio, [inicio]]]
    nodos_visitados = []

    while nodos_frontera:
        nodos_frontera.sort(key=lambda x: x[0])
        f, g, ciudad_actual, camino = nodos_frontera.pop(0)

        if ciudad_actual in nodos_visitados:
            continue
        nodos_visitados.append(ciudad_actual)

        if ciudad_actual == destino:
            return {
                "ruta":        camino,
                "costo_total": round(g, 2),
                "pasos":       len(camino) - 1,
                "visitados":   nodos_visitados,
            }

        if ciudad_actual not in grafo:
            continue

        for vecino, costo in grafo[ciudad_actual].items():
            if vecino not in nodos_visitados:
                nuevo_g = g + costo
                nuevo_f = nuevo_g + manhattan_dist(vecino, destino)
                nodos_frontera.append([nuevo_f, nuevo_g, vecino, camino + [vecino]])

    return {"error": f"No existe ruta de {inicio} a {destino}"}