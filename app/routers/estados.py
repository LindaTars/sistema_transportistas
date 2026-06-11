# app/routers/estados.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Estado
from app.schemas import EstadoOut

router = APIRouter(prefix="/estados", tags=["Estados"])


@router.get("/", response_model=list[EstadoOut])
async def listar_estados(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Estado).where(Estado.activo == True))
    return result.scalars().all()


@router.get("/{estado_id}", response_model=EstadoOut)
async def obtener_estado(estado_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Estado).where(Estado.id == estado_id))
    estado = result.scalar_one_or_none()
    if not estado:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    return estado