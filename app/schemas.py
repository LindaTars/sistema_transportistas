# app/schemas.py
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


# ── ESTADOS ──────────────────────────────────────────
class EstadoOut(BaseModel):
    id: int
    clave_inegi: str
    nombre: str
    region: str

    model_config = {"from_attributes": True}


# ── TIPOS DE RIESGO ───────────────────────────────────
class TipoRiesgoOut(BaseModel):
    id: int
    codigo: str
    nombre: str
    peso_base: Decimal

    model_config = {"from_attributes": True}


# ── INCIDENTES ────────────────────────────────────────
class IncidenteCreate(BaseModel):
    estado_id:            int
    tipo_riesgo_id:       int
    fecha_incidente:      date
    municipio:            Optional[str] = None
    descripcion:          Optional[str] = None
    victimas:             int           = Field(0, ge=0)
    perdida_estimada_mxn: Optional[Decimal] = None
    fuente:               Optional[str] = None
    latitud:              Optional[Decimal] = None
    longitud:             Optional[Decimal] = None


class IncidenteOut(IncidenteCreate):
    id:         int
    verificado: bool
    creado_en:  datetime
    estado:     EstadoOut
    tipo_riesgo: TipoRiesgoOut

    model_config = {"from_attributes": True}


# ── NIVELES DE PELIGRO ────────────────────────────────
class NivelPeligroOut(BaseModel):
    id:                  int
    estado:              EstadoOut
    periodo:             date
    total_incidentes:    int
    indice_peligrosidad: Decimal
    nivel:               str
    calculado_en:        datetime

    model_config = {"from_attributes": True}


# ── PING ESP32 ────────────────────────────────────────
class PingCreate(BaseModel):
    latitud:           Decimal = Field(..., ge=-90,  le=90)
    longitud:          Decimal = Field(..., ge=-180, le=180)
    nivel_combustible: Optional[Decimal] = Field(None, ge=0)
    velocidad:         Optional[Decimal] = Field(None, ge=0)


class PingResponse(BaseModel):
    estado:         Optional[str] = None
    nivel_peligro:  Optional[str] = None
    alerta_ordeno:  bool = False
    mensaje:        Optional[str] = None


# ── RUTAS (algoritmos) ────────────────────────────────
class RutaRequest(BaseModel):
    origen:   str = Field(..., description="Nombre del estado origen")
    destino:  str = Field(..., description="Nombre del estado destino")
    algoritmo: str = Field("a_estrella",
                           description="ucs | a_estrella | manhattan | genetico")


class RutaResponse(BaseModel):
    algoritmo:    str
    origen:       str
    destino:      str
    ruta:         list[str]
    costo_total:  float
    pasos:        int