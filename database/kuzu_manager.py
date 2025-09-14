"""
KuzuDB Manager para The Garden
Gestiona conexiones y operaciones con la base de datos de grafos KuzuDB
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class KuzuDBManager:
    """Gestor principal para operaciones con KuzuDB"""
    
    def __init__(self, db_path: str = "database/garden.kuzu"):
        self.db_path = db_path
        self.db = None
        self.conn = None
        self._kuzu_available = self._check_kuzu_availability()
        if self._kuzu_available:
            self._ensure_db_exists()
    
    def _check_kuzu_availability(self) -> bool:
        """Verificar si KuzuDB está disponible"""
        try:
            import kuzu
            return True
        except ImportError:
            print("⚠️ KuzuDB no está disponible. Funcionando en modo compatibilidad.")
            return False
    
    def _ensure_db_exists(self):
        """Crear directorio de base de datos si no existe"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    def connect(self):
        """Conectar a la base de datos KuzuDB"""
        if not self._kuzu_available:
            return None
            
        if self.db is None or self.conn is None:
            try:
                import kuzu
                self.db = kuzu.Database(self.db_path)
                self.conn = kuzu.Connection(self.db)
                print(f"✓ Conectado a KuzuDB: {self.db_path}")
            except Exception as e:
                print(f"❌ Error conectando a KuzuDB: {e}")
                self._kuzu_available = False
                return None
        return self.conn
    
    def is_available(self) -> bool:
        """Verificar si KuzuDB está disponible y conectado"""
        return self._kuzu_available and self.conn is not None
    
    def initialize_schema(self):
        """Inicializar schema desde archivo SQL"""
        if not self.is_available():
            print("⚠️ KuzuDB no disponible, saltando inicialización de schema")
            return
            
        conn = self.connect()
        schema_path = "database/schemas/garden_schema.sql"
        
        if not os.path.exists(schema_path):
            print(f"⚠️ Schema file no encontrado: {schema_path}")
            return
        
        try:
            # Leer y ejecutar schema
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_content = f.read()
            
            # Dividir por comandos (separados por ';') y filtrar contenido de comentarios
            commands = []
            for cmd in schema_content.split(';'):
                cmd = cmd.strip()
                if not cmd:
                    continue
                
                # Extraer las líneas que no son comentarios
                lines = []
                for line in cmd.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('--'):
                        lines.append(line)
                
                # Si hay contenido después de quitar comentarios, añadirlo
                if lines:
                    clean_command = '\n'.join(lines)
                    if clean_command:
                        commands.append(clean_command)
            
            for command in commands:
                # Los comandos ya están limpios de comentarios
                try:
                    print(f"🔧 Executing: {command[:80]}...")
                    conn.execute(command)
                    print(f"✓ Success")
                except Exception as e:
                    print(f"❌ Error ejecutando comando: {command[:100]}...")
                    print(f"   Error: {e}")
                    # No fallar completamente, continuar con próximo comando
                    
            print("✓ Schema inicializado correctamente")
            
        except Exception as e:
            print(f"❌ Error general inicializando schema: {e}")
    
    def load_initial_data(self):
        """Cargar datos iniciales desde archivo de semillas"""
        if not self.is_available():
            print("⚠️ KuzuDB no disponible, saltando carga de datos iniciales")
            return
            
        conn = self.connect()
        seeds_path = "database/seeds/initial_data.sql"
        
        if not os.path.exists(seeds_path):
            print(f"⚠️ Seeds file no encontrado: {seeds_path}")
            return
        
        try:
            with open(seeds_path, "r", encoding="utf-8") as f:
                seeds_content = f.read()
            
            # Dividir por comandos
            commands = [cmd.strip() for cmd in seeds_content.split(';') if cmd.strip()]
            
            for command in commands:
                # Saltar comentarios
                if command.startswith('--') or not command:
                    continue
                try:
                    conn.execute(command)
                    print(f"✓ Datos cargados: {command[:50]}...")
                except Exception as e:
                    print(f"⚠️ Error cargando datos (puede ser normal si ya existen): {e}")
                    # No fallar, los datos pueden ya existir
                    
            print("✓ Datos iniciales cargados")
            
        except Exception as e:
            print(f"❌ Error general cargando datos iniciales: {e}")
    
    def execute_query(self, query: str, parameters: Dict = None):
        """Ejecutar consulta con parámetros opcionales"""
        if not self.is_available():
            print("⚠️ KuzuDB no disponible para ejecutar consulta")
            return None
            
        conn = self.connect()
        try:
            if parameters:
                return conn.execute(query, parameters)
            else:
                return conn.execute(query)
        except Exception as e:
            print(f"❌ Error ejecutando consulta KuzuDB: {query[:100]}...")
            print(f"   Error: {e}")
            raise
    
    def query_plantas_by_coordinates(self, x: float, y: float, radius: float = 20.0) -> List[Dict]:
        """Consulta optimizada para obtener plantas por coordenadas"""
        if not self.is_available():
            return []
            
        query = """
        MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
        WHERE abs(p.coordenadas_x - $x) <= $radius 
        AND abs(p.coordenadas_y - $y) <= $radius
        RETURN p.id, p.fecha_siembra, p.estado, p.coordenadas_x, p.coordenadas_y,
               h.nombre, h.descripcion,
               sqrt(pow(p.coordenadas_x - $x, 2) + pow(p.coordenadas_y - $y, 2)) as distancia
        ORDER BY distancia
        LIMIT 5
        """
        
        try:
            result = self.execute_query(query, {"x": x, "y": y, "radius": radius})
            plantas = []
            
            if result and result.has_next():
                while result.has_next():
                    row = result.get_next()
                    plantas.append({
                        "id": row[0],
                        "fecha_siembra": row[1], 
                        "estado": row[2],
                        "coordenadas_x": row[3],
                        "coordenadas_y": row[4],
                        "hortaliza_nombre": row[5],
                        "hortaliza_descripcion": row[6],
                        "distancia": row[7]
                    })
                    
            return plantas
            
        except Exception as e:
            print(f"Error en consulta por coordenadas: {e}")
            return []
    
    def close(self):
        """Cerrar conexión"""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            finally:
                self.conn = None
        if self.db:
            try:
                self.db.close() 
            except:
                pass
            finally:
                self.db = None
        print("✓ KuzuDB desconectado")


# Instancia global singleton
kuzu_manager = KuzuDBManager()