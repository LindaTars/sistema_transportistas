from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import estados, incidentes, peligrosidad, rutas
import app.models
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Sistema de Peligrosidad para Transportistas",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(estados.router)
app.include_router(incidentes.router)
app.include_router(peligrosidad.router)
app.include_router(rutas.router)

app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")


@app.get("/")
async def root():
    return {"mensaje": "API Sistema Transportistas funcionando"}