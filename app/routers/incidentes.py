# app/routers/incidentes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Incidente
from app.schemas import IncidenteCreate, IncidenteOut

router = APIRouter(prefix="/incidentes", tags=["Incidentes"])


@router.get("/", response_model=list[IncidenteOut])
async def listar_incidentes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Incidente)
        .options(
            selectinload(Incidente.estado),
            selectinload(Incidente.tipo_riesgo)
        )
        .order_by(Incidente.fecha_incidente.desc())
        .limit(50)
    )
    return result.scalars().all()


@router.get("/{incidente_id}", response_model=IncidenteOut)
async def obtener_incidente(incidente_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Incidente)
        .options(
            selectinload(Incidente.estado),
            selectinload(Incidente.tipo_riesgo)
        )
        .where(Incidente.id == incidente_id)
    )
    incidente = result.scalar_one_or_none()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return incidente


@router.post("/", response_model=IncidenteOut, status_code=201)
async def crear_incidente(datos: IncidenteCreate, db: AsyncSession = Depends(get_db)):
    incidente = Incidente(**datos.model_dump())
    db.add(incidente)
    await db.commit()
    await db.refresh(incidente)
    # Recargar con relaciones
    result = await db.execute(
        select(Incidente)
        .options(
            selectinload(Incidente.estado),
            selectinload(Incidente.tipo_riesgo)
        )
        .where(Incidente.id == incidente.id)
    )
    return result.scalar_one()