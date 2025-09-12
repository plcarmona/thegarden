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


# =============================================
# ENDPOINTS KUZUDB ANALYTICS
# =============================================

@router.get("/analytics/plants-by-type/{hortaliza_id}")
async def get_plants_by_type(hortaliza_id: int):
    """Obtener todas las plantas de un tipo específico usando KuzuDB"""
    try:
        from database.model_adapter import model_adapter
        
        plantas = model_adapter.get_plantas_by_type(hortaliza_id)
        
        return {
            "hortaliza_id": hortaliza_id,
            "total_plantas": len(plantas),
            "plantas": plantas
        }
        
    except Exception as e:
        return {"error": f"KuzuDB query failed: {e}", "plantas": []}


@router.get("/analytics/spatial-query/{x}/{y}")
async def spatial_query(x: float, y: float, radius: float = 50.0):
    """Consulta espacial avanzada usando KuzuDB"""
    try:
        from database.model_adapter import model_adapter
        
        nearby_plants = model_adapter.get_spatial_query(x, y, radius)
        
        return {
            "center": {"x": x, "y": y}, 
            "radius": radius,
            "total_found": len(nearby_plants),
            "nearby_plants": nearby_plants
        }
        
    except Exception as e:
        return {"error": f"Spatial query failed: {e}", "nearby_plants": []}


@router.get("/analytics/database-status")
async def database_status():
    """Verificar estado de KuzuDB y estadísticas generales"""
    try:
        from database.kuzu_manager import kuzu_manager
        
        if not kuzu_manager.is_available():
            return {
                "kuzu_available": False,
                "message": "KuzuDB no disponible. Sistema funcionando con datos en memoria.",
                "fallback_mode": True
            }
        
        # Obtener estadísticas básicas
        stats = {}
        queries = [
            ("total_hortalizas", "MATCH (h:Hortaliza) RETURN count(h)"),
            ("total_plantas_activas", "MATCH (p:Planta {estado: 'activo'}) RETURN count(p)"),
            ("total_anotaciones", "MATCH (a:Anotaciones) RETURN count(a)"),
            ("total_huertas", "MATCH (hu:Huerta) RETURN count(hu)")
        ]
        
        for stat_name, query in queries:
            try:
                result = kuzu_manager.execute_query(query)
                if result and result.has_next():
                    stats[stat_name] = result.get_next()[0]
                else:
                    stats[stat_name] = 0
            except:
                stats[stat_name] = "error"
        
        return {
            "kuzu_available": True,
            "database_path": kuzu_manager.db_path,
            "statistics": stats,
            "fallback_mode": False
        }
        
    except Exception as e:
        return {
            "kuzu_available": False,
            "error": str(e),
            "fallback_mode": True
        }


@router.get("/analytics/density-analysis")
async def density_analysis():
    """Análisis de densidad de cultivos usando KuzuDB"""
    try:
        from database.kuzu_manager import kuzu_manager
        
        if not kuzu_manager.is_available():
            return {"error": "KuzuDB no disponible", "density_data": []}
        
        query = """
        MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
        WITH toInteger(p.coordenadas_x / 100) * 100 as grid_x, 
             toInteger(p.coordenadas_y / 100) * 100 as grid_y, 
             count(p) as plantas_por_celda,
             collect(DISTINCT h.nombre) as tipos
        WHERE plantas_por_celda > 0
        RETURN grid_x, grid_y, plantas_por_celda, tipos
        ORDER BY plantas_por_celda DESC
        """
        
        result = kuzu_manager.execute_query(query)
        density_data = []
        
        if result:
            while result.has_next():
                row = result.get_next()
                density_data.append({
                    "grid_x": row[0],
                    "grid_y": row[1], 
                    "plant_count": row[2],
                    "plant_types": row[3]
                })
        
        return {
            "analysis_type": "density_by_grid",
            "grid_size": "100x100 pixels",
            "total_areas": len(density_data),
            "density_data": density_data
        }
        
    except Exception as e:
        return {"error": f"Density analysis failed: {e}", "density_data": []}


@router.post("/analytics/init-kuzu") 
async def initialize_kuzu_database():
    """Inicializar base de datos KuzuDB manualmente"""
    try:
        from database.kuzu_manager import kuzu_manager
        
        # Conectar
        conn = kuzu_manager.connect()
        if not conn:
            return {
                "success": False,
                "message": "KuzuDB no está disponible. Instale con: pip install kuzu"
            }
        
        # Inicializar schema
        kuzu_manager.initialize_schema()
        
        # Cargar datos iniciales
        kuzu_manager.load_initial_data()
        
        # Migrar datos actuales
        from database.model_adapter import model_adapter
        model_adapter.migrate_hortalizas_to_kuzu(huerta_instance.hortalizas_db)
        
        # Migrar cultivos activos
        for cultivo in huerta_instance.cultivos_activos:
            model_adapter.create_planta_in_kuzu(cultivo)
        
        # Migrar anotaciones
        for anotacion in huerta_instance.anotaciones:
            model_adapter.create_anotacion_in_kuzu(anotacion)
        
        return {
            "success": True,
            "message": "KuzuDB inicializado correctamente",
            "database_path": kuzu_manager.db_path
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error inicializando KuzuDB"
        }