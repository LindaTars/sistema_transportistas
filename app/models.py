from decimal import Decimal
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum,
    ForeignKey, Integer, Numeric, SmallInteger,
    String, Text, func
)
from sqlalchemy.orm import relationship
from app.database import Base


class Estado(Base):
    __tablename__ = "estados"

    id          = Column(Integer, primary_key=True)
    clave_inegi = Column(String(2),  nullable=False, unique=True)
    nombre      = Column(String(60), nullable=False, unique=True)
    region      = Column(Enum("Noroeste","Norte","Noreste",
                              "Centro-Occidente","Centro","Sur-Sureste"),
                         nullable=False)
    activo      = Column(Boolean, default=True)
    creado_en   = Column(DateTime, server_default=func.now())

    incidentes      = relationship("Incidente",    back_populates="estado")
    niveles_peligro = relationship("NivelPeligro", back_populates="estado")


class TipoRiesgo(Base):
    __tablename__ = "tipos_riesgo"

    id          = Column(SmallInteger, primary_key=True)
    codigo      = Column(String(20),  nullable=False, unique=True)
    nombre      = Column(String(80),  nullable=False)
    descripcion = Column(Text)
    peso_base   = Column(Numeric(4, 2), nullable=False, default=Decimal("1.00"))
    activo      = Column(Boolean, default=True)

    incidentes  = relationship("Incidente", back_populates="tipo_riesgo")


class Incidente(Base):
    __tablename__ = "incidentes"

    id                   = Column(Integer, primary_key=True)
    estado_id            = Column(Integer, ForeignKey("estados.id"),      nullable=False)
    tipo_riesgo_id       = Column(Integer, ForeignKey("tipos_riesgo.id"), nullable=False)
    fecha_incidente      = Column(Date,    nullable=False)
    municipio            = Column(String(100))
    descripcion          = Column(Text)
    victimas             = Column(Integer, default=0)
    perdida_estimada_mxn = Column(Numeric(14, 2))
    fuente               = Column(String(100))
    latitud              = Column(Numeric(10, 7))
    longitud             = Column(Numeric(10, 7))
    verificado           = Column(Boolean, default=False)
    creado_en            = Column(DateTime, server_default=func.now())
    actualizado_en       = Column(DateTime, server_default=func.now(),
                                  onupdate=func.now())

    estado      = relationship("Estado",     back_populates="incidentes")
    tipo_riesgo = relationship("TipoRiesgo", back_populates="incidentes")


class NivelPeligro(Base):
    __tablename__ = "niveles_peligro"

    id                  = Column(Integer, primary_key=True)
    estado_id           = Column(Integer, ForeignKey("estados.id"), nullable=False)
    periodo             = Column(Date,    nullable=False)
    total_incidentes    = Column(Integer, default=0)
    indice_peligrosidad = Column(Numeric(6, 2), default=Decimal("0.00"))
    nivel               = Column(Enum("Bajo","Medio","Alto","Crítico"), nullable=False)
    calculado_en        = Column(DateTime, server_default=func.now())

    estado = relationship("Estado", back_populates="niveles_peligro")


class PingTransportista(Base):
    __tablename__ = "pings_transportista"

    id                  = Column(Integer, primary_key=True)
    latitud             = Column(Numeric(10, 7), nullable=False)
    longitud            = Column(Numeric(10, 7), nullable=False)
    nivel_combustible   = Column(Numeric(6, 2))
    velocidad           = Column(Numeric(6, 2))
    alerta_ordeno       = Column(Boolean, default=False)
    creado_en           = Column(DateTime, server_default=func.now())