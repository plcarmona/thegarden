"""
Calendar API router (RF-007, RF-008, RF-009)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime

from .calendar import calendar_service, EventoCalendario

router = APIRouter()


@router.get("/lunar")
async def obtener_calendario_lunar(fecha: Optional[str] = None) -> Dict[str, Any]:
    """Obtener información del calendario lunar para una fecha (RF-007)"""
    try:
        if fecha:
            fecha_obj = datetime.fromisoformat(fecha)
        else:
            fecha_obj = datetime.now()
        
        info_lunar = calendar_service.obtener_fase_lunar(fecha_obj)
        return info_lunar.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error obteniendo información lunar: {str(e)}")


@router.get("/lunar/semanal")
async def obtener_calendario_lunar_semanal(fecha_inicio: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtener calendario lunar para una semana (RF-007)"""
    try:
        if fecha_inicio:
            fecha_obj = datetime.fromisoformat(fecha_inicio)
        else:
            fecha_obj = datetime.now()
        
        calendario = calendar_service.obtener_calendario_semanal(fecha_obj)
        return calendario
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error obteniendo calendario semanal: {str(e)}")


@router.get("/siembra-cosecha")
async def obtener_calendario_siembra_cosecha() -> List[Dict[str, Any]]:
    """Obtener calendario de siembra y cosecha (RF-008)"""
    try:
        eventos = calendar_service.generar_calendario_siembra_cosecha()
        return [e.model_dump() for e in eventos]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando calendario: {str(e)}")


@router.post("/eventos")
async def agregar_evento(evento: EventoCalendario) -> Dict[str, Any]:
    """Agregar un evento personalizado al calendario"""
    try:
        evento_id = calendar_service.agregar_evento(evento)
        return {"success": True, "id": evento_id, "message": "Evento agregado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error agregando evento: {str(e)}")


@router.put("/eventos/{evento_id}/completar")
async def completar_evento(evento_id: str) -> Dict[str, Any]:
    """Marcar un evento como completado"""
    try:
        success = calendar_service.marcar_evento_completado(evento_id)
        if success:
            return {"success": True, "message": "Evento marcado como completado"}
        else:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error completando evento: {str(e)}")


@router.get("/sugerencias")
async def obtener_sugerencias_siembra(mes: Optional[int] = None) -> List[Dict[str, Any]]:
    """Obtener sugerencias de siembra para el mes actual (RF-009)"""
    try:
        sugerencias = calendar_service.obtener_sugerencias_siembra(mes)
        return sugerencias
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo sugerencias: {str(e)}")


@router.get("/eventos/{fecha}")
async def obtener_eventos_fecha(fecha: str) -> List[Dict[str, Any]]:
    """Obtener eventos para una fecha específica"""
    try:
        eventos = calendar_service.obtener_eventos_fecha(fecha)
        return [e.model_dump() for e in eventos]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error obteniendo eventos: {str(e)}")