from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import NivelPeligro
from app.schemas import NivelPeligroOut

router = APIRouter(prefix="/peligrosidad", tags=["Peligrosidad"])


@router.get("/", response_model=list[NivelPeligroOut])
async def listar_indices(
    nivel: Optional[str] = Query(None, description="Bajo|Medio|Alto|Crítico"),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(NivelPeligro)
        .options(selectinload(NivelPeligro.estado))
        .order_by(NivelPeligro.indice_peligrosidad.desc())
    )
    if nivel:
        stmt = stmt.where(NivelPeligro.nivel == nivel)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{estado_id}", response_model=NivelPeligroOut)
async def obtener_indice_estado(
    estado_id: int,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(NivelPeligro)
        .options(selectinload(NivelPeligro.estado))
        .where(NivelPeligro.estado_id == estado_id)
        .order_by(NivelPeligro.periodo.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    nivel = result.scalar_one_or_none()
    if not nivel:
        raise HTTPException(status_code=404, detail="Índice no encontrado")
    return nivel