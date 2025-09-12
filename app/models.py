from typing import List, Optional, Tuple
from pydantic import BaseModel
import json


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
        self.dimensiones = {"ancho": 800, "alto": 600}  # Canvas dimensions
    
    def cargar_mapa(self) -> dict:
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
        """Obtener el cultivo activo en una coordenada específica (implementa RF-003)"""
        # Simple distance-based lookup (could be improved with spatial indexing)
        for cultivo in self.cultivos_activos:
            dist = ((cultivo.coordenadas.x - x) ** 2 + (cultivo.coordenadas.y - y) ** 2) ** 0.5
            if dist < 20:  # 20 pixel tolerance
                return cultivo
        return None
    
    def agregar_cultivo_activo(self, cultivo: CultivoActivo) -> str:
        """Inicializar un nuevo cultivo activo (implementa RF-005)"""
        # Check for collisions
        if self._verificar_colision(cultivo.coordenadas):
            raise ValueError("Colisión detectada: ya existe un cultivo en esta posición")
        
        # Generate simple ID if not provided
        if not cultivo.id:
            cultivo.id = f"cultivo_{len(self.cultivos_activos) + 1}"
        
        self.cultivos_activos.append(cultivo)
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