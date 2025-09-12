from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel

from .models import huerta_instance, Poligono, CultivoActivo, Coordenada, Anotacion, Hortaliza


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


@router.get("/hortalizas")
async def listar_hortalizas() -> List[Dict[str, Any]]:
    """Lista todos los tipos de hortalizas disponibles (RF-002)"""
    hortalizas = huerta_instance.listar_hortalizas()
    return [h.model_dump() for h in hortalizas]


@router.get("/hortalizas/{hortaliza_id}")
async def obtener_hortaliza(hortaliza_id: int) -> Dict[str, Any]:
    """Obtiene información detallada de una hortaliza (RF-002)"""
    hortaliza = huerta_instance.obtener_hortaliza(hortaliza_id)
    if not hortaliza:
        raise HTTPException(status_code=404, detail="Hortaliza no encontrada")
    return hortaliza.model_dump()


@router.post("/anotaciones")
async def agregar_anotacion(anotacion: Anotacion) -> SuccessResponse:
    """Agregar una nueva anotación (RF-004)"""
    try:
        anotacion_id = huerta_instance.agregar_anotacion(anotacion)
        return SuccessResponse(success=True, id=anotacion_id, message="Anotación agregada correctamente")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/anotaciones/cultivo/{cultivo_id}")
async def obtener_anotaciones_cultivo(cultivo_id: str) -> List[Dict[str, Any]]:
    """Obtener anotaciones de un cultivo específico (RF-004)"""
    anotaciones = huerta_instance.obtener_anotaciones_por_cultivo(cultivo_id)
    return [a.model_dump() for a in anotaciones]


@router.get("/anotaciones/tipo/{hortaliza_id}")
async def obtener_anotaciones_tipo(hortaliza_id: int) -> List[Dict[str, Any]]:
    """Obtener anotaciones por tipo de planta (RF-004)"""
    anotaciones = huerta_instance.obtener_anotaciones_por_tipo_planta(hortaliza_id)
    return [a.model_dump() for a in anotaciones]


@router.get("/anotaciones/coordenada/{x}/{y}")
async def obtener_anotaciones_coordenada(x: float, y: float, radio: float = 25) -> List[Dict[str, Any]]:
    """Obtener anotaciones cerca de una coordenada (RF-004)"""
    anotaciones = huerta_instance.obtener_anotaciones_por_coordenada(x, y, radio)
    return [a.model_dump() for a in anotaciones]