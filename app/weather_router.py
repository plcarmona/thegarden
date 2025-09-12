"""
Weather API router (RF-006)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from .weather import weather_service

router = APIRouter()


@router.get("/pronostico")
async def obtener_pronostico(ubicacion: str = "Buenos Aires") -> Dict[str, Any]:
    """Obtener pronóstico del clima para los próximos 7 días (RF-006)"""
    try:
        forecast = weather_service.obtener_pronostico_7_dias(ubicacion)
        return forecast.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo pronóstico: {str(e)}")


@router.get("/alertas")
async def obtener_alertas_climaticas() -> List[Dict[str, Any]]:
    """Obtener alertas climáticas importantes para la huerta (RF-006)"""
    try:
        alertas = weather_service.obtener_alertas_climaticas()
        return alertas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo alertas: {str(e)}")