from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel
import json
from datetime import datetime
from enum import Enum


class Coordenada(BaseModel):
    """Representa una coordenada (x, y) en el mapa de la huerta"""
    x: float
    y: float


class Poligono(BaseModel):
    """Representa un polígono en el mapa de la huerta"""
    id: Optional[str] = None
    coordinates: List[Coordenada]
    tipo: str = "cultivo"  # tipo de área: cultivo, sendero, estructura, etc.
    nombre: Optional[str] = None


class TipoAnotacion(str, Enum):
    """Tipos de anotaciones disponibles"""
    EVENTO = "evento"
    FOTO = "foto"
    NOTA = "nota"
    SIEMBRA = "siembra"
    COSECHA = "cosecha"
    RIEGO = "riego"
    FERTILIZACION = "fertilizacion"
    PODA = "poda"


class NivelEspecificidad(str, Enum):
    """Niveles de especificidad para anotaciones"""
    TIPO_PLANTA = "tipo_planta"
    TIEMPO = "tiempo"
    INDIVIDUO = "individuo"
    ESTACION = "estacion"


class Anotacion(BaseModel):
    """Representa una anotación en el sistema (RF-004)"""
    id: Optional[str] = None
    tipo: TipoAnotacion
    nivel_especificidad: NivelEspecificidad
    fecha: str
    notas: Optional[str] = None
    fotos: List[str] = []  # URLs o paths de fotos
    cultivo_id: Optional[str] = None  # Para anotaciones específicas de cultivo
    hortaliza_id: Optional[int] = None  # Para anotaciones por tipo de planta
    coordenadas: Optional[Coordenada] = None  # Para anotaciones por ubicación


class Hortaliza(BaseModel):
    """Información de un tipo de hortaliza (RF-002 database)"""
    id: int
    nombre: str
    descripcion: str
    ciclo_dias: int  # Días de siembra a cosecha
    siembra_mes_inicio: int  # Mes ideal para inicio de siembra (1-12)
    siembra_mes_fin: int  # Mes ideal para fin de siembra (1-12)
    plagas_comunes: List[str] = []
    cuidados: List[str] = []
    tamano_promedio: float = 1.0  # En metros cuadrados
    distancia_min: float = 0.3  # Distancia mínima entre plantas en metros


class CultivoActivo(BaseModel):
    """Representa un cultivo activo en una posición específica"""
    id: Optional[str] = None
    hortaliza_id: int
    coordenadas: Coordenada
    fecha_siembra: str
    estado: str = "activo"


class Huerta:
    """Clase principal para manejar el mapa de la huerta"""
    
    def __init__(self):
        self.poligonos: List[Poligono] = []
        self.cultivos_activos: List[CultivoActivo] = []
        self.anotaciones: List[Anotacion] = []  # RF-004: Sistema de anotaciones
        self.dimensiones = {"ancho": 800, "alto": 600}  # Canvas dimensions
        
        # RF-002: Base de datos de hortalizas
        self.hortalizas_db = self._inicializar_hortalizas()
        
        # KuzuDB integration
        self._kuzu_available = self._init_kuzu_integration()
    
    def _init_kuzu_integration(self) -> bool:
        """Inicializar integración con KuzuDB"""
        try:
            from database.model_adapter import model_adapter
            
            # Migrar hortalizas existentes a KuzuDB
            if model_adapter.kuzu.is_available():
                model_adapter.migrate_hortalizas_to_kuzu(self.hortalizas_db)
                return True
            return False
        except Exception as e:
            print(f"⚠️ KuzuDB no disponible: {e}")
            return False
    
    def _inicializar_hortalizas(self) -> Dict[int, Hortaliza]:
        """Inicializar base de datos de hortalizas (RF-002)"""
        hortalizas = [
            Hortaliza(
                id=1, nombre="Tomate", descripcion="Solanum lycopersicum",
                ciclo_dias=120, siembra_mes_inicio=9, siembra_mes_fin=11,
                plagas_comunes=["Trips", "Mosca blanca", "Pulgones"],
                cuidados=["Riego regular", "Tutoreo", "Poda de brotes laterales"],
                tamano_promedio=1.5, distancia_min=0.6
            ),
            Hortaliza(
                id=2, nombre="Lechuga", descripcion="Lactuca sativa",
                ciclo_dias=60, siembra_mes_inicio=3, siembra_mes_fin=9,
                plagas_comunes=["Caracoles", "Babosas", "Pulgones"],
                cuidados=["Riego frecuente", "Sombra parcial en verano"],
                tamano_promedio=0.3, distancia_min=0.2
            ),
            Hortaliza(
                id=3, nombre="Zanahoria", descripcion="Daucus carota",
                ciclo_dias=90, siembra_mes_inicio=8, siembra_mes_fin=2,
                plagas_comunes=["Mosca de la zanahoria", "Nematodos"],
                cuidados=["Suelo suelto", "Raleo de plántulas"],
                tamano_promedio=0.1, distancia_min=0.1
            ),
            Hortaliza(
                id=4, nombre="Pepino", descripcion="Cucumis sativus",
                ciclo_dias=75, siembra_mes_inicio=10, siembra_mes_fin=12,
                plagas_comunes=["Oídio", "Trips", "Arañuela"],
                cuidados=["Tutoreo", "Riego abundante", "Fertilización"],
                tamano_promedio=2.0, distancia_min=0.8
            )
        ]
        return {h.id: h for h in hortalizas}
    
    def obtener_hortaliza(self, hortaliza_id: int) -> Optional[Hortaliza]:
        """Obtener información de una hortaliza por ID"""
        return self.hortalizas_db.get(hortaliza_id)
    
    def listar_hortalizas(self) -> List[Hortaliza]:
        """Listar todas las hortalizas disponibles"""
        return list(self.hortalizas_db.values())
    
    def agregar_anotacion(self, anotacion: Anotacion) -> str:
        """Agregar una nueva anotación (RF-004) con soporte KuzuDB"""
        if not anotacion.id:
            anotacion.id = f"anotacion_{len(self.anotaciones) + 1}"
        
        # Auto-generar fecha si no se proporciona
        if not anotacion.fecha:
            anotacion.fecha = datetime.now().isoformat()
        
        # Agregar a sistema en memoria
        self.anotaciones.append(anotacion)
        
        # Persistir en KuzuDB si está disponible
        if self._kuzu_available:
            try:
                from database.model_adapter import model_adapter
                model_adapter.create_anotacion_in_kuzu(anotacion)
            except Exception as e:
                print(f"⚠️ Error persistiendo anotación en KuzuDB: {e}")
        
        return anotacion.id
    
    def obtener_anotaciones_por_cultivo(self, cultivo_id: str) -> List[Anotacion]:
        """Obtener anotaciones específicas de un cultivo"""
        return [a for a in self.anotaciones if a.cultivo_id == cultivo_id]
    
    def obtener_anotaciones_por_tipo_planta(self, hortaliza_id: int) -> List[Anotacion]:
        """Obtener anotaciones por tipo de planta"""
        return [a for a in self.anotaciones 
                if a.nivel_especificidad == NivelEspecificidad.TIPO_PLANTA 
                and a.hortaliza_id == hortaliza_id]
    
    def obtener_anotaciones_por_coordenada(self, x: float, y: float, radio: float = 25) -> List[Anotacion]:
        """Obtener anotaciones cerca de una coordenada"""
        anotaciones_cercanas = []
        for anotacion in self.anotaciones:
            if anotacion.coordenadas:
                dist = ((anotacion.coordenadas.x - x) ** 2 + 
                       (anotacion.coordenadas.y - y) ** 2) ** 0.5
                if dist <= radio:
                    anotaciones_cercanas.append(anotacion)
        return anotaciones_cercanas
    
    def cargar_mapa(self) -> dict:
        """Cargar la configuración actual del mapa"""
        return {
            "poligonos": [p.model_dump() for p in self.poligonos],
            "cultivos_activos": [c.model_dump() for c in self.cultivos_activos],
            "anotaciones": [a.model_dump() for a in self.anotaciones],
            "dimensiones": self.dimensiones
        }
        """Cargar la configuración actual del mapa"""
        return {
            "poligonos": [p.model_dump() for p in self.poligonos],
            "cultivos_activos": [c.model_dump() for c in self.cultivos_activos],
            "dimensiones": self.dimensiones
        }
    
    def agregar_poligono(self, poligono: Poligono) -> str:
        """Agregar un nuevo polígono al mapa"""
        # Generate simple ID if not provided
        if not poligono.id:
            poligono.id = f"poly_{len(self.poligonos) + 1}"
        
        self.poligonos.append(poligono)
        return poligono.id
    
    def obtener_planta_en_coordenada(self, x: float, y: float) -> Optional[CultivoActivo]:
        """Obtener el cultivo activo en una coordenada específica (implementa RF-003) con KuzuDB"""
        
        # Intentar consulta desde KuzuDB primero si está disponible
        if self._kuzu_available:
            try:
                from database.model_adapter import model_adapter
                kuzu_result = model_adapter.query_planta_by_coordinates(x, y)
                if kuzu_result:
                    # Convertir resultado de KuzuDB a modelo Pydantic
                    # Buscar el cultivo en memoria que coincida
                    for cultivo in self.cultivos_activos:
                        if cultivo.id == kuzu_result.get('id'):
                            return cultivo
            except Exception as e:
                print(f"⚠️ Error consultando KuzuDB: {e}")
        
        # Fallback a consulta en memoria
        for cultivo in self.cultivos_activos:
            dist = ((cultivo.coordenadas.x - x) ** 2 + (cultivo.coordenadas.y - y) ** 2) ** 0.5
            if dist < 20:  # 20 pixel tolerance
                return cultivo
        return None
    
    def agregar_cultivo_activo(self, cultivo: CultivoActivo) -> str:
        """Inicializar un nuevo cultivo activo (implementa RF-005) con soporte KuzuDB"""
        # Check for collisions
        if self._verificar_colision(cultivo.coordenadas):
            raise ValueError("Colisión detectada: ya existe un cultivo en esta posición")
        
        # Generate simple ID if not provided
        if not cultivo.id:
            cultivo.id = f"cultivo_{len(self.cultivos_activos) + 1}"
        
        # Agregar a sistema en memoria
        self.cultivos_activos.append(cultivo)
        
        # Persistir en KuzuDB si está disponible
        if self._kuzu_available:
            try:
                from database.model_adapter import model_adapter
                model_adapter.create_planta_in_kuzu(cultivo)
            except Exception as e:
                print(f"⚠️ Error persistiendo cultivo en KuzuDB: {e}")
        
        return cultivo.id
    
    def _verificar_colision(self, coordenadas: Coordenada, radio: float = 25) -> bool:
        """Verificar si hay colisión con cultivos existentes"""
        for cultivo in self.cultivos_activos:
            dist = ((cultivo.coordenadas.x - coordenadas.x) ** 2 + 
                   (cultivo.coordenadas.y - coordenadas.y) ** 2) ** 0.5
            if dist < radio:
                return True
        return False


# Global instance (in a real app, this would be managed by dependency injection)
huerta_instance = Huerta()