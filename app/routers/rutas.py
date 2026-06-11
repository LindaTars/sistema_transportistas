# app/routers/rutas.py
from fastapi import APIRouter, HTTPException
from app.schemas import RutaRequest, RutaResponse

from algoritmos.ucs import buscar_ucs
from algoritmos.a_estrella import buscar_a_estrella
from algoritmos.manhattan import buscar_manhattan
from algoritmos.genetico import buscar_genetico

from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from app.database import get_db
from app.models import NivelPeligro, PingTransportista
from app.schemas import PingCreate, PingResponse

router = APIRouter(prefix="/rutas", tags=["Rutas y Algoritmos"])

# Grafo de carreteras entre estados con distancias en km
# Basado en el mismo grafo del apunte del maestro pero con estados reales
GRAFO_MEXICO = {
    "Estado de México": {
        "CDMX": 60, "Hidalgo": 120, "Querétaro": 180,
        "Morelos": 90, "Puebla": 130, "Michoacán": 200
    },
    "CDMX": {
        "Estado de México": 60, "Morelos": 85,
        "Hidalgo": 130, "Puebla": 120
    },
    "Jalisco": {
        "Guanajuato": 170, "Michoacán": 220,
        "Aguascalientes": 110, "Zacatecas": 290, "Sinaloa": 580
    },
    "Nuevo León": {
        "Tamaulipas": 220, "San Luis Potosí": 380,
        "Zacatecas": 470, "Chihuahua": 790, "Sonora": 1100,
        "Coahuila": 230
    },
    "Guerrero": {
        "Morelos": 190, "Puebla": 270,
        "Oaxaca": 360, "Michoacán": 280
    },
    "Puebla": {
        "Estado de México": 130, "CDMX": 120, "Guerrero": 270,
        "Oaxaca": 330, "Veracruz": 210, "Morelos": 120, "Hidalgo": 180
    },
    "Chihuahua": {
        "Sonora": 600, "Sinaloa": 570,
        "Zacatecas": 720, "Nuevo León": 790, "Coahuila": 500
    },
    "Guanajuato": {
        "Jalisco": 170, "Querétaro": 110,
        "San Luis Potosí": 200, "Michoacán": 150, "Aguascalientes": 100
    },
    "Hidalgo": {
        "Estado de México": 120, "CDMX": 130,
        "Querétaro": 140, "Veracruz": 280, "Puebla": 180
    },
    "Morelos": {
        "CDMX": 85, "Estado de México": 90,
        "Guerrero": 190, "Puebla": 120
    },
    "Michoacán": {
        "Jalisco": 220, "Guanajuato": 150,
        "Estado de México": 200, "Guerrero": 280, "Colima": 180
    },
    "Oaxaca": {
        "Puebla": 330, "Guerrero": 360,
        "Veracruz": 340, "Chiapas": 240
    },
    "Querétaro": {
        "Estado de México": 180, "Hidalgo": 140,
        "Guanajuato": 110, "San Luis Potosí": 200
    },
    "San Luis Potosí": {
        "Querétaro": 200, "Guanajuato": 200,
        "Zacatecas": 190, "Nuevo León": 380,
        "Tamaulipas": 430, "Hidalgo": 280
    },
    "Sinaloa": {
        "Sonora": 420, "Chihuahua": 570,
        "Jalisco": 580, "Zacatecas": 530, "Nayarit": 280
    },
    "Sonora": {
        "Chihuahua": 600, "Sinaloa": 420,
        "Nuevo León": 1100, "Baja California": 750
    },
    "Tamaulipas": {
        "Nuevo León": 220, "San Luis Potosí": 430,
        "Veracruz": 520, "Coahuila": 400
    },
    "Veracruz": {
        "Puebla": 210, "Oaxaca": 340,
        "Hidalgo": 280, "Tamaulipas": 520,
        "Tabasco": 350, "Chiapas": 480
    },
    "Zacatecas": {
        "Jalisco": 290, "San Luis Potosí": 190,
        "Aguascalientes": 120, "Chihuahua": 720,
        "Nuevo León": 470, "Durango": 310, "Coahuila": 420
    },
    "Aguascalientes": {
        "Jalisco": 110, "Guanajuato": 100, "Zacatecas": 120
    },
    "Coahuila": {
        "Nuevo León": 230, "Chihuahua": 500,
        "Zacatecas": 420, "Tamaulipas": 400, "Durango": 560
    },
    "Durango": {
        "Zacatecas": 310, "Sinaloa": 320,
        "Chihuahua": 480, "Coahuila": 560, "Nayarit": 330
    },
    "Nayarit": {
        "Jalisco": 190, "Sinaloa": 280, "Durango": 330
    },
    "Colima": {
        "Jalisco": 130, "Michoacán": 180
    },
    "Tabasco": {
        "Veracruz": 350, "Chiapas": 230, "Campeche": 280
    },
    "Chiapas": {
        "Oaxaca": 240, "Veracruz": 480,
        "Tabasco": 230, "Campeche": 420
    },
    "Campeche": {
        "Tabasco": 280, "Chiapas": 420,
        "Yucatán": 160, "Quintana Roo": 320
    },
    "Yucatán": {
        "Campeche": 160, "Quintana Roo": 320
    },
    "Quintana Roo": {
        "Yucatán": 320, "Campeche": 320
    },
    "Baja California": {
        "Sonora": 750, "Baja California Sur": 680
    },
    "Baja California Sur": {
        "Baja California": 680
    },
    "Tlaxcala": {
        "Puebla": 30, "Hidalgo": 120, "Estado de México": 150
    },
}

ALGORITMOS = {
    "ucs":        buscar_ucs,
    "a_estrella": buscar_a_estrella,
    "manhattan":  buscar_manhattan,
    "genetico":   buscar_genetico,
}


@router.post("/calcular", response_model=RutaResponse)
async def calcular_ruta(request: RutaRequest):
    if request.algoritmo not in ALGORITMOS:
        raise HTTPException(
            status_code=400,
            detail=f"Algoritmo no válido. Opciones: {list(ALGORITMOS.keys())}"
        )

    funcion = ALGORITMOS[request.algoritmo]
    resultado = funcion(GRAFO_MEXICO, request.origen, request.destino)

    if "error" in resultado:
        raise HTTPException(status_code=404, detail=resultado["error"])

    return RutaResponse(
        algoritmo=   request.algoritmo,
        origen=      request.origen,
        destino=     request.destino,
        ruta=        resultado["ruta"],
        costo_total= resultado["costo_total"],
        pasos=       resultado["pasos"],
    )


@router.get("/estados-disponibles")
async def estados_disponibles():
    """Lista los estados que tienen conexiones en el grafo"""
    return {"estados": sorted(GRAFO_MEXICO.keys())}

#! Datos ESP32
@router.post("/ping-gps", response_model=PingResponse)
async def recibir_ping_esp32(
    ping: PingCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Recibe la ubicación del ESP32 y devuelve el nivel de peligro de la zona.
    También detecta ordeñamiento si el combustible baja más de lo esperado.
    """
    # 1. Detectar en qué estado está el punto GPS
    # Por ahora usamos el estado más cercano por coordenadas
    from algoritmos.a_estrella import COORDENADAS
    from math import sin, cos, acos, radians

    def dist(lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        val = sin(lat1)*sin(lat2) + cos(lat1)*cos(lat2)*cos(lon1-lon2)
        return acos(max(-1.0, min(1.0, val))) * 111.32

    lat  = float(ping.latitud)
    lon  = float(ping.longitud)

    estado_cercano = min(
        COORDENADAS.items(),
        key=lambda item: dist(lat, lon, item[1][0], item[1][1])
    )
    nombre_estado = estado_cercano[0]

    # 2. Buscar nivel de peligro del estado
    result = await db.execute(
        select(NivelPeligro)
        .join(NivelPeligro.estado)
        .where(NivelPeligro.estado.has(nombre=nombre_estado))
        .order_by(NivelPeligro.periodo.desc())
        .limit(1)
    )
    nivel_obj = result.scalar_one_or_none()
    nivel_str = nivel_obj.nivel if nivel_obj else "Sin datos"

    # 3. Detectar ordeñamiento
    # Consumo normal: ~0.35 litros/km para camión pesado
    # El sensor ultrasónico mide cm → asumimos 1cm = 2 litros en el recipiente
    alerta_ordeno = False
    if ping.nivel_combustible is not None:
        nivel_cm = float(ping.nivel_combustible)
        # Umbral: si el nivel baja más de 5cm en un ping → alerta
        if nivel_cm < 5.0:
            alerta_ordeno = True

    # 4. Guardar ping en BD
    nuevo_ping = PingTransportista(
        latitud=           ping.latitud,
        longitud=          ping.longitud,
        nivel_combustible= ping.nivel_combustible,
        velocidad=         ping.velocidad,
        alerta_ordeno=     alerta_ordeno,
    )
    db.add(nuevo_ping)
    await db.commit()

    return PingResponse(
        estado=        nombre_estado,
        nivel_peligro= nivel_str,
        alerta_ordeno= alerta_ordeno,
        mensaje=       f"⚠️ ALERTA: Posible ordeñamiento detectado" if alerta_ordeno else None,
    )