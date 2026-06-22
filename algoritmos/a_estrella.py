from math import sin, cos, acos, radians

COORDENADAS = {
    "Estado de México":   (19.3590, -99.6520),
    "Jalisco":            (20.6595, -103.3494),
    "Nuevo León":         (25.5922, -99.9962),
    "Guerrero":           (17.4392, -100.0000),
    "Puebla":             (19.0414, -98.2063),
    "Chihuahua":          (28.6353, -106.0889),
    "Guanajuato":         (21.0190, -101.2574),
    "CDMX":               (19.4326, -99.1332),
    "Veracruz":           (19.1738, -96.1342),
    "Oaxaca":             (17.0732, -96.7266),
    "Tamaulipas":         (23.7369, -99.1411),
    "Sonora":             (29.0892, -110.9613),
    "Sinaloa":            (24.8091, -107.3940),
    "Zacatecas":          (22.7709, -102.5832),
    "Querétaro":          (20.5888, -100.3899),
    "San Luis Potosí":    (22.1565, -100.9855),
    "Hidalgo":            (20.0911, -98.7624),
    "Morelos":            (18.6813, -99.1013),
    "Michoacán":          (19.5665, -101.7068),
    "Aguascalientes":     (21.8853, -102.2916),
    "Coahuila":           (27.0587, -101.7068),
    "Durango":            (24.0277, -104.6532),
    "Nayarit":            (21.7514, -104.8455),
    "Colima":             (19.2452, -103.7241),
    "Tabasco":            (17.9869, -92.9303),
    "Chiapas":            (16.7569, -93.1292),
    "Campeche":           (19.8301, -90.5349),
    "Yucatán":            (20.7099, -89.0943),
    "Quintana Roo":       (19.1817, -88.4791),
    "Baja California":    (30.8406, -115.2838),
    "Baja California Sur":(25.5691, -111.4547),
    "Tlaxcala":           (19.3182, -98.2375),
}


def geodist(ciudad1: str, ciudad2: str) -> float:
    if ciudad1 not in COORDENADAS or ciudad2 not in COORDENADAS:
        return 0.0
    lat1, lon1 = map(radians, COORDENADAS[ciudad1])
    lat2, lon2 = map(radians, COORDENADAS[ciudad2])
    val = (sin(lat1) * sin(lat2)) + (cos(lat1) * cos(lat2) * cos(lon1 - lon2))
    return acos(max(-1.0, min(1.0, val))) * 111.32


def buscar_a_estrella(grafo: dict, inicio: str, destino: str) -> dict:
    nodos_frontera = [[geodist(inicio, destino), 0, inicio, [inicio]]]
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
                nuevo_f = nuevo_g + geodist(vecino, destino)
                nodos_frontera.append([nuevo_f, nuevo_g, vecino, camino + [vecino]])

    return {"error": f"No existe ruta de {inicio} a {destino}"}