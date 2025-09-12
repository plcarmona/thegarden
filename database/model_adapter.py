"""
Model Adapter para The Garden
Adaptador entre modelos Pydantic y KuzuDB
Permite mantener compatibilidad con el sistema existente
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models import Hortaliza, CultivoActivo, Anotacion, Coordenada
from database.kuzu_manager import kuzu_manager


class ModelAdapter:
    """Adaptador entre modelos Pydantic y KuzuDB"""
    
    def __init__(self):
        self.kuzu = kuzu_manager
    
    def migrate_hortalizas_to_kuzu(self, hortalizas: Dict[int, Hortaliza]) -> bool:
        """Migrar hortalizas existentes a KuzuDB"""
        if not self.kuzu.is_available():
            return False
            
        try:
            for hortaliza in hortalizas.values():
                # Verificar si ya existe
                check_query = "MATCH (h:Hortaliza {id: $id}) RETURN h.id LIMIT 1"
                existing = self.kuzu.execute_query(check_query, {"id": hortaliza.id})
                
                if existing and existing.has_next():
                    continue  # Ya existe, saltar
                
                # Crear nueva hortaliza
                query = """
                CREATE (:Hortaliza {
                    id: $id,
                    nombre: $nombre,
                    descripcion: $descripcion,
                    ciclo_dias: $ciclo_dias,
                    siembra_mes_inicio: $siembra_mes_inicio,
                    siembra_mes_fin: $siembra_mes_fin,
                    plagas_comunes: $plagas_comunes,
                    cuidados: $cuidados,
                    tamano_promedio: $tamano_promedio,
                    distancia_min: $distancia_min
                })
                """
                
                self.kuzu.execute_query(query, {
                    "id": hortaliza.id,
                    "nombre": hortaliza.nombre,
                    "descripcion": hortaliza.descripcion,
                    "ciclo_dias": hortaliza.ciclo_dias,
                    "siembra_mes_inicio": hortaliza.siembra_mes_inicio,
                    "siembra_mes_fin": hortaliza.siembra_mes_fin,
                    "plagas_comunes": hortaliza.plagas_comunes,
                    "cuidados": hortaliza.cuidados,
                    "tamano_promedio": hortaliza.tamano_promedio,
                    "distancia_min": hortaliza.distancia_min
                })
                
            print(f"✓ {len(hortalizas)} hortalizas migradas a KuzuDB")
            return True
            
        except Exception as e:
            print(f"❌ Error migrando hortalizas: {e}")
            return False
    
    def create_planta_in_kuzu(self, cultivo: CultivoActivo, huerta_id: str = "huerta_default") -> bool:
        """Crear planta en KuzuDB con relaciones"""
        if not self.kuzu.is_available():
            return False
            
        try:
            # Verificar si ya existe
            check_query = "MATCH (p:Planta {id: $id}) RETURN p.id LIMIT 1"
            existing = self.kuzu.execute_query(check_query, {"id": cultivo.id})
            
            if existing and existing.has_next():
                return True  # Ya existe
            
            # Crear nodo Planta
            create_planta_query = """
            CREATE (:Planta {
                id: $id,
                fecha_siembra: $fecha_siembra,
                coordenadas_x: $coordenadas_x,
                coordenadas_y: $coordenadas_y,
                estado: $estado,
                fecha_cosecha: NULL,
                notas: $notas
            })
            """
            
            self.kuzu.execute_query(create_planta_query, {
                "id": cultivo.id,
                "fecha_siembra": cultivo.fecha_siembra,
                "coordenadas_x": cultivo.coordenadas.x,
                "coordenadas_y": cultivo.coordenadas.y,
                "estado": cultivo.estado,
                "notas": ""
            })
            
            # Crear relación IS_OF_TYPE
            create_relation_type_query = """
            MATCH (p:Planta {id: $planta_id}), (h:Hortaliza {id: $hortaliza_id})
            CREATE (p)-[:IS_OF_TYPE {fecha_relacion: $fecha}]->(h)
            """
            
            self.kuzu.execute_query(create_relation_type_query, {
                "planta_id": cultivo.id,
                "hortaliza_id": cultivo.hortaliza_id,
                "fecha": datetime.now().isoformat()
            })
            
            # Crear relación LOCATED_IN
            create_location_query = """
            MATCH (p:Planta {id: $planta_id}), (hu:Huerta {id: $huerta_id})
            CREATE (p)-[:LOCATED_IN {fecha_plantacion: $fecha, area_ocupada: 0.0}]->(hu),
                   (hu)-[:CONTAINS]->(p)
            """
            
            self.kuzu.execute_query(create_location_query, {
                "planta_id": cultivo.id,
                "huerta_id": huerta_id,
                "fecha": cultivo.fecha_siembra
            })
            
            print(f"✓ Planta {cultivo.id} creada en KuzuDB")
            return True
            
        except Exception as e:
            print(f"❌ Error creando planta en KuzuDB: {e}")
            return False
    
    def query_planta_by_coordinates(self, x: float, y: float, radius: float = 20.0) -> Optional[Dict]:
        """Consultar planta por coordenadas usando KuzuDB"""
        if not self.kuzu.is_available():
            return None
            
        try:
            plantas = self.kuzu.query_plantas_by_coordinates(x, y, radius)
            return plantas[0] if plantas else None
            
        except Exception as e:
            print(f"❌ Error consultando planta por coordenadas: {e}")
            return None
    
    def create_anotacion_in_kuzu(self, anotacion: Anotacion) -> bool:
        """Crear anotación en KuzuDB con relaciones"""
        if not self.kuzu.is_available():
            return False
            
        try:
            # Verificar si ya existe
            check_query = "MATCH (a:Anotaciones {id: $id}) RETURN a.id LIMIT 1"
            existing = self.kuzu.execute_query(check_query, {"id": anotacion.id})
            
            if existing and existing.has_next():
                return True  # Ya existe
            
            # Crear nodo Anotaciones
            create_annotation_query = """
            CREATE (:Anotaciones {
                id: $id,
                tipo: $tipo,
                nivel_especificidad: $nivel_especificidad,
                fecha: $fecha,
                notas: $notas,
                fotos: $fotos,
                temporada: $temporada,
                metadata: $metadata
            })
            """
            
            self.kuzu.execute_query(create_annotation_query, {
                "id": anotacion.id,
                "tipo": anotacion.tipo,
                "nivel_especificidad": anotacion.nivel_especificidad,
                "fecha": anotacion.fecha,
                "notas": anotacion.notas or "",
                "fotos": anotacion.fotos,
                "temporada": getattr(anotacion, 'temporada', ''),
                "metadata": "{}"
            })
            
            # Crear relaciones según el nivel de especificidad
            if anotacion.cultivo_id:
                # Relación con Planta específica
                relate_to_planta_query = """
                MATCH (a:Anotaciones {id: $annotation_id}), (p:Planta {id: $planta_id})
                CREATE (a)-[:ANNOTATES_PLANTA {
                    relevancia: $relevancia,
                    fecha_anotacion: $fecha
                }]->(p)
                """
                
                self.kuzu.execute_query(relate_to_planta_query, {
                    "annotation_id": anotacion.id,
                    "planta_id": anotacion.cultivo_id,
                    "relevancia": 1.0,
                    "fecha": anotacion.fecha
                })
            
            elif anotacion.hortaliza_id:
                # Relación con tipo de Hortaliza
                relate_to_hortaliza_query = """
                MATCH (a:Anotaciones {id: $annotation_id}), (h:Hortaliza {id: $hortaliza_id})
                CREATE (a)-[:ANNOTATES {
                    relevancia: $relevancia,
                    fecha_anotacion: $fecha
                }]->(h)
                """
                
                self.kuzu.execute_query(relate_to_hortaliza_query, {
                    "annotation_id": anotacion.id,
                    "hortaliza_id": anotacion.hortaliza_id,
                    "relevancia": 1.0,
                    "fecha": anotacion.fecha
                })
            
            print(f"✓ Anotación {anotacion.id} creada en KuzuDB")
            return True
            
        except Exception as e:
            print(f"❌ Error creando anotación en KuzuDB: {e}")
            return False
    
    def get_plantas_by_type(self, hortaliza_id: int) -> List[Dict]:
        """Obtener todas las plantas de un tipo específico"""
        if not self.kuzu.is_available():
            return []
            
        try:
            query = """
            MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza {id: $hortaliza_id})
            RETURN p.id, p.coordenadas_x, p.coordenadas_y, p.estado, p.fecha_siembra,
                   h.nombre, h.descripcion
            ORDER BY p.fecha_siembra DESC
            """
            
            result = self.kuzu.execute_query(query, {"hortaliza_id": hortaliza_id})
            plantas = []
            
            if result:
                while result.has_next():
                    row = result.get_next()
                    plantas.append({
                        "id": row[0],
                        "x": row[1],
                        "y": row[2], 
                        "estado": row[3],
                        "fecha_siembra": row[4],
                        "tipo": row[5],
                        "descripcion": row[6]
                    })
            
            return plantas
            
        except Exception as e:
            print(f"❌ Error obteniendo plantas por tipo: {e}")
            return []
    
    def get_spatial_query(self, x: float, y: float, radius: float = 50.0) -> List[Dict]:
        """Consulta espacial avanzada"""
        if not self.kuzu.is_available():
            return []
            
        try:
            query = """
            MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
            WHERE abs(p.coordenadas_x - $x) <= $radius 
            AND abs(p.coordenadas_y - $y) <= $radius
            RETURN p.id, h.nombre, p.coordenadas_x, p.coordenadas_y, p.estado,
                   sqrt(pow(p.coordenadas_x - $x, 2) + pow(p.coordenadas_y - $y, 2)) as distancia
            ORDER BY distancia
            LIMIT 10
            """
            
            result = self.kuzu.execute_query(query, {"x": x, "y": y, "radius": radius})
            plantas = []
            
            if result:
                while result.has_next():
                    row = result.get_next()
                    plantas.append({
                        "id": row[0],
                        "tipo": row[1],
                        "x": row[2],
                        "y": row[3],
                        "estado": row[4],
                        "distancia": row[5]
                    })
            
            return plantas
            
        except Exception as e:
            print(f"❌ Error en consulta espacial: {e}")
            return []


# Instancia global
model_adapter = ModelAdapter()