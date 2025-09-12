from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from .models import huerta_instance, Poligono, CultivoActivo, Coordenada


class SuccessResponse(BaseModel):
    success: bool
    id: str
    message: str

router = APIRouter()


@router.get("/mapa")
async def obtener_mapa() -> Dict[str, Any]:
    """Obtiene la configuración del mapa de la huerta (RF-001)"""
    return huerta_instance.cargar_mapa()


@router.post("/mapa/poligono")
async def agregar_poligono(poligono: Poligono) -> SuccessResponse:
    """Añade un nuevo polígono al mapa (RF-001)"""
    try:
        poligono_id = huerta_instance.agregar_poligono(poligono)
        return SuccessResponse(success=True, id=poligono_id, message="Polígono agregado correctamente")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/coordenada/{x}/{y}")
async def consultar_coordenada(x: float, y: float) -> Dict[str, Any]:
    """Consulta qué hay en una coordenada específica (RF-003)"""
    cultivo = huerta_instance.obtener_planta_en_coordenada(x, y)
    
    if cultivo:
        return {
            "existe_cultivo": True,
            "cultivo": cultivo.model_dump(),
            "coordenadas": {"x": x, "y": y}
        }
    else:
        return {
            "existe_cultivo": False,
            "cultivo": None,
            "coordenadas": {"x": x, "y": y}
        }


@router.post("/cultivos/activos")
async def agregar_cultivo_activo(cultivo: CultivoActivo) -> SuccessResponse:
    """Inicializa un nuevo cultivo activo (RF-005)"""
    try:
        cultivo_id = huerta_instance.agregar_cultivo_activo(cultivo)
        return SuccessResponse(success=True, id=cultivo_id, message="Cultivo activo agregado correctamente")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))