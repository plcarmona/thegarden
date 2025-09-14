"""
KuzuDB Manager para The Garden
Gestiona conexiones y operaciones con la base de datos de grafos KuzuDB
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from contextlib import contextmanager
from .toml_loader import toml_loader


class KuzuDBManager:
    """Gestor principal para operaciones con KuzuDB"""
    
    def __init__(self, db_path: str = "database/garden.kuzu"):
        self.db_path = db_path
        self.db = None
        self.conn = None
        self._kuzu_available = self._check_kuzu_availability()
        self._connection_count = 0  # Track connections for debugging
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
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        except (OSError, PermissionError) as e:
            print(f"⚠️ No se pudo crear directorio para base de datos: {e}")
            self._kuzu_available = False
        
    def connect(self):
        """Conectar a la base de datos KuzuDB - creates a fresh connection"""
        if not self._kuzu_available:
            return None
            
        try:
            import kuzu
            # Always create fresh connection instances to avoid concurrency issues
            db = kuzu.Database(self.db_path)
            conn = kuzu.Connection(db)
            self._connection_count += 1
            if self._connection_count == 1:  # Only print on first connection
                print(f"✓ Conectado a KuzuDB: {self.db_path}")
            
            # Check if database is initialized, auto-initialize if needed  
            # Use the new connection for initialization check
            if not self._is_database_initialized(conn):
                print("⚠️ Database not initialized, auto-initializing schema...")
                if self._initialize_schema_with_connection(conn):
                    print("✓ Database schema auto-initialized successfully")
                    print("ℹ️  Use the Initialize DB button to load initial data (hortalizas, structures, etc.)")
                else:
                    print("❌ Auto-initialization failed")
            
            return conn
            
        except Exception as e:
            print(f"❌ Error conectando a KuzuDB: {e}")
            return None
    
    def _is_database_initialized(self, conn) -> bool:
        """Check if the database has been initialized with required tables"""
        if not conn:
            return False
        
        try:
            # Test for key tables by trying a simple count query
            conn.execute("MATCH (n:Anotation) RETURN count(n) LIMIT 1")
            conn.execute("MATCH (n:Estructura) RETURN count(n) LIMIT 1") 
            conn.execute("MATCH (n:Hortaliza) RETURN count(n) LIMIT 1")
            return True
        except Exception:
            # If any query fails, database is not properly initialized
            return False
    
    def is_available(self) -> bool:
        """Verificar si KuzuDB está disponible y conectado"""
        return self._kuzu_available

    @contextmanager
    def get_connection(self):
        """Context manager for database connections to ensure proper cleanup"""
        conn = None
        try:
            conn = self.connect()
            yield conn
        finally:
            # KuzuDB connections are automatically cleaned up when out of scope
            # No explicit close needed, but we track this for debugging
            if conn:
                self._connection_count = max(0, self._connection_count - 1)
    
    def _initialize_schema_with_connection(self, conn):
        """Initialize schema using provided connection"""
        if not self.is_available():
            print("⚠️ KuzuDB no disponible, saltando inicialización de schema")
            return False
            
        if conn is None:
            print("❌ Error: No se pudo usar la conexión para inicializar schema")
            return False
            
        schema_path = "database/schemas/garden_schema.sql"
        
        if not os.path.exists(schema_path):
            print(f"⚠️ Schema file no encontrado: {schema_path}")
            return False
        
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
            
            # Validate that key tables were created successfully
            try:
                validation_queries = [
                    "MATCH (n:Hortaliza) RETURN count(n) LIMIT 1",
                    "MATCH (n:Planta) RETURN count(n) LIMIT 1", 
                    "MATCH (n:Huerta) RETURN count(n) LIMIT 1",
                    "MATCH (n:Anotation) RETURN count(n) LIMIT 1",
                    "MATCH (n:Estructura) RETURN count(n) LIMIT 1"
                ]
                
                failed_tables = []
                for query in validation_queries:
                    try:
                        conn.execute(query)
                    except Exception as e:
                        table_name = query.split(":")[1].split(")")[0]
                        failed_tables.append(table_name)
                
                if failed_tables:
                    print(f"❌ Schema validation failed - missing tables: {', '.join(failed_tables)}")
                    print("   Database initialization incomplete!")
                    return False
                else:
                    print("✓ Schema validation successful - all tables created")
                    
            except Exception as e:
                print(f"⚠️ Schema validation error: {e}")
            
            print("✓ Schema inicializado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error general inicializando schema: {e}")
            return False
    
    def initialize_schema(self):
        """Inicializar schema desde archivo SQL"""
        if not self.is_available():
            print("⚠️ KuzuDB no disponible, saltando inicialización de schema")
            return False
            
        # Use existing connection if available, otherwise connect
        conn = self.conn if self.conn else self.connect()
        if conn is None:
            print("❌ Error: No se pudo establecer conexión a KuzuDB para inicializar schema")
            return False
            
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
            
            # Validate that key tables were created successfully
            try:
                validation_queries = [
                    "MATCH (n:Hortaliza) RETURN count(n) LIMIT 1",
                    "MATCH (n:Planta) RETURN count(n) LIMIT 1", 
                    "MATCH (n:Huerta) RETURN count(n) LIMIT 1",
                    "MATCH (n:Anotation) RETURN count(n) LIMIT 1",
                    "MATCH (n:Estructura) RETURN count(n) LIMIT 1"
                ]
                
                failed_tables = []
                for query in validation_queries:
                    try:
                        conn.execute(query)
                    except Exception as e:
                        table_name = query.split(":")[1].split(")")[0]
                        failed_tables.append(table_name)
                
                if failed_tables:
                    print(f"❌ Schema validation failed - missing tables: {', '.join(failed_tables)}")
                    print("   Database initialization incomplete!")
                    return False
                else:
                    print("✓ Schema validation successful - all tables created")
                    
            except Exception as e:
                print(f"⚠️ Schema validation error: {e}")
            
            print("✓ Schema inicializado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error general inicializando schema: {e}")
            return False
            
    def _create_fresh_connection(self):
        """Create a fresh connection without auto-initialization"""
        if not self._kuzu_available:
            return None
            
        try:
            import kuzu
            db = kuzu.Database(self.db_path)
            conn = kuzu.Connection(db)
            return conn
        except Exception as e:
            print(f"❌ Error creating fresh connection: {e}")
            return None
    
    def load_initial_data(self):
        """Cargar datos iniciales desde TOML y archivos de semillas"""
        if not self.is_available():
            print("⚠️ KuzuDB no disponible, saltando carga de datos iniciales")
            return
            
        print("📦 Loading initial data...")
        
        # Use a single connection for all operations to avoid lock issues
        with self.get_connection() as conn:
            if conn is None:
                print("❌ Error: No se pudo establecer conexión a KuzuDB para cargar datos iniciales")
                return
            
            # First load basic data (garden) from SQL seeds
            self._load_sql_seeds(conn)
            
            # Then load hortalizas from TOML
            self._load_hortalizas_from_toml(conn)
            
            # Load structures from TOML
            self._load_estructuras_from_toml(conn)
            
            # Create relationships for sample plants
            self._create_sample_relationships(conn)
        
        print("✓ Todos los datos iniciales cargados")

    def initialize_database(self):
        """Initialize database with schema and initial data using single connection"""
        if not self.is_available():
            print("⚠️ KuzuDB no disponible, saltando inicialización completa")
            return False
            
        try:
            # Initialize schema first
            if not self.initialize_schema():
                print("❌ Schema creation failed - aborting initialization")
                return False
            
            # Load initial data
            self.load_initial_data()
            
            return True
            
        except Exception as e:
            print(f"❌ Error general inicializando base de datos: {e}")
            return False
    
    def _load_sql_seeds(self, conn=None):
        """Load basic data from SQL seeds file"""
        seeds_path = "database/seeds/initial_data.sql"
        
        if not os.path.exists(seeds_path):
            print(f"⚠️ Seeds file no encontrado: {seeds_path}")
            return
        
        # Use provided connection or create a new one
        use_existing = conn is not None
        if not use_existing:
            conn = self.connect()
            if conn is None:
                print("❌ Error: No se pudo establecer conexión a KuzuDB para cargar datos SQL")
                return
        
        try:
            with open(seeds_path, "r", encoding="utf-8") as f:
                seeds_content = f.read()
            
            # Only load huerta, plantas and anotaciones from SQL, skip hortalizas
            commands = [cmd.strip() for cmd in seeds_content.split(';') if cmd.strip()]
            
            for command in commands:
                # Skip comentarios and hortalizas creation
                if (command.startswith('--') or not command or 
                    'CREATE (h:Hortaliza' in command or
                    'Hortaliza {' in command):
                    continue
                try:
                    conn.execute(command)
                    print(f"✓ SQL datos cargados: {command[:50]}...")
                except Exception as e:
                    print(f"⚠️ Error cargando SQL (puede ser normal): {e}")
                    
        except Exception as e:
            print(f"❌ Error general cargando SQL seeds: {e}")
    
    def _load_hortalizas_from_toml(self, conn=None):
        """Load hortalizas from TOML configuration"""
        try:
            hortalizas = toml_loader.get_hortalizas()
            
            # Use provided connection or create a new one
            use_existing = conn is not None
            if not use_existing:
                conn = self.connect()
                if conn is None:
                    print("❌ Error: No se pudo establecer conexión a KuzuDB para cargar hortalizas")
                    return
            
            for hortaliza in hortalizas:
                # Convert arrays to proper format for KuzuDB
                plagas_str = str(hortaliza.get('plagas_comunes', []))
                cuidados_str = str(hortaliza.get('cuidados', []))
                
                query = """
                CREATE (h:Hortaliza {
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
                
                params = {
                    'id': hortaliza['id'],
                    'nombre': hortaliza['nombre'],
                    'descripcion': hortaliza['descripcion'],
                    'ciclo_dias': hortaliza['ciclo_dias'],
                    'siembra_mes_inicio': hortaliza['siembra_mes_inicio'],
                    'siembra_mes_fin': hortaliza['siembra_mes_fin'],
                    'plagas_comunes': hortaliza.get('plagas_comunes', []),
                    'cuidados': hortaliza.get('cuidados', []),
                    'tamano_promedio': hortaliza.get('tamano_promedio', 0.0),
                    'distancia_min': hortaliza.get('distancia_min', 0.0)
                }
                
                try:
                    conn.execute(query, params)
                    print(f"✓ Hortaliza cargada desde TOML: {hortaliza['nombre']}")
                except Exception as e:
                    print(f"⚠️ Error cargando hortaliza {hortaliza['nombre']}: {e}")
                    
        except Exception as e:
            print(f"❌ Error general cargando hortalizas desde TOML: {e}")
    
    def _load_estructuras_from_toml(self, conn=None):
        """Load structures from TOML configuration"""
        try:
            estructuras = toml_loader.get_estructuras()
            
            # Use provided connection or create a new one
            use_existing = conn is not None
            if not use_existing:
                conn = self.connect()
                if conn is None:
                    print("❌ Error: No se pudo establecer conexión a KuzuDB para cargar estructuras")
                    return
            
            for estructura in estructuras:
                query = """
                CREATE (e:Estructura {
                    id: $id,
                    nombre: $nombre,
                    tipo: $tipo,
                    descripcion: $descripcion,
                    poligono: $poligono,
                    fecha_creacion: $fecha_creacion
                })
                """
                
                params = {
                    'id': estructura['id'],
                    'nombre': estructura['nombre'],
                    'tipo': estructura['tipo'],
                    'descripcion': estructura.get('descripcion', ''),
                    'poligono': estructura['poligono'],
                    'fecha_creacion': datetime.now()
                }
                
                try:
                    conn.execute(query, params)
                    print(f"✓ Estructura cargada desde TOML: {estructura['nombre']}")
                    
                    # Create relationship with default garden
                    rel_query = """
                    MATCH (e:Estructura {id: $estructura_id}), (h:Huerta {id: "huerta_default"})
                    CREATE (e)-[:BLOCKS_AREA {fecha_relacion: $fecha}]->(h)
                    """
                    conn.execute(rel_query, {
                        'estructura_id': estructura['id'],
                        'fecha': datetime.now()
                    })
                    print(f"✓ Relación estructura-huerta creada: {estructura['nombre']}")
                    
                except Exception as e:
                    print(f"⚠️ Error cargando estructura {estructura['nombre']}: {e}")
                    
        except Exception as e:
            print(f"❌ Error general cargando estructuras desde TOML: {e}")
    
    def _create_sample_relationships(self, conn=None):
        """Create relationships for sample plants with TOML-loaded hortalizas"""
        try:
            # Use provided connection or create a new one
            use_existing = conn is not None
            if not use_existing:
                conn = self.connect()
                if conn is None:
                    print("❌ Error: No se pudo establecer conexión a KuzuDB para crear relaciones")
                    return
            
            # Sample plant relationships (matching the original SQL)
            relationships = [
                ("tomate_001", 1),      # Tomate
                ("lechuga_001", 2),     # Lechuga  
                ("zanahoria_001", 3),   # Zanahoria
            ]
            
            for planta_id, hortaliza_id in relationships:
                query = """
                MATCH (p:Planta {id: $planta_id}), (h:Hortaliza {id: $hortaliza_id})
                CREATE (p)-[:IS_OF_TYPE {fecha_relacion: $fecha}]->(h)
                """
                try:
                    conn.execute(query, {
                        'planta_id': planta_id,
                        'hortaliza_id': hortaliza_id,
                        'fecha': datetime.now()
                    })
                    print(f"✓ Relación planta-hortaliza creada: {planta_id} -> {hortaliza_id}")
                except Exception as e:
                    print(f"⚠️ Error creando relación {planta_id}-{hortaliza_id}: {e}")
                    
        except Exception as e:
            print(f"❌ Error general creando relaciones de ejemplo: {e}")
    
    def execute_query(self, query: str, parameters: Dict = None, connection=None):
        """Ejecutar consulta con parámetros opcionales"""
        if not self.is_available():
            print("⚠️ KuzuDB no disponible para ejecutar consulta")
            return None
        
        # Use provided connection or create a new one
        conn = connection if connection else self.connect()
        if not conn:
            return None
            
        try:
            if parameters:
                return conn.execute(query, parameters)
            else:
                return conn.execute(query)
        except Exception as e:
            print(f"❌ Error ejecutando consulta KuzuDB: {query[:100]}...")
            print(f"   Error: {e}")
            raise
        finally:
            # Only close if we created the connection
            if not connection:
                self.close(conn)
    
    def query_plantas_by_coordinates(self, x: float, y: float, radius: float = 20.0, connection=None) -> List[Dict]:
        """Consulta optimizada para obtener plantas por coordenadas"""
        if not self.is_available():
            return []
            
        query = """
        MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
        WHERE abs(p.coordenadas_x - $x) <= $radius 
        AND abs(p.coordenadas_y - $y) <= $radius
        RETURN p.id, p.fecha_siembra, p.fecha_cosecha, p.coordenadas_x, p.coordenadas_y,
               h.nombre, h.descripcion,
               sqrt(pow(p.coordenadas_x - $x, 2) + pow(p.coordenadas_y - $y, 2)) as distancia
        ORDER BY distancia
        LIMIT 5
        """
        
        try:
            result = self.execute_query(query, {"x": x, "y": y, "radius": radius}, connection=connection)
            plantas = []
            
            if result and result.has_next():
                while result.has_next():
                    row = result.get_next()
                    plantas.append({
                        "id": row[0],
                        "fecha_siembra": row[1], 
                        "fecha_cosecha": row[2],
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
    
    def query_all_estructuras(self, connection=None) -> List[Dict]:
        """Get all structures/unusable areas"""
        if not self.is_available():
            return []
            
        query = """
        MATCH (e:Estructura)
        RETURN e.id, e.nombre, e.tipo, e.descripcion, e.poligono, e.fecha_creacion
        ORDER BY e.nombre
        """
        
        try:
            result = self.execute_query(query, connection=connection)
            estructuras = []
            
            if result and result.has_next():
                while result.has_next():
                    row = result.get_next()
                    estructuras.append({
                        "id": row[0],
                        "nombre": row[1],
                        "tipo": row[2],
                        "descripcion": row[3],
                        "poligono": row[4],
                        "fecha_creacion": row[5]
                    })
                    
            return estructuras
            
        except Exception as e:
            print(f"Error consultando estructuras: {e}")
            return []
    
    def check_coordinate_in_structure(self, x: float, y: float, connection=None) -> List[Dict]:
        """Check if coordinates are inside any structure (unusable area)"""
        if not self.is_available():
            return []
            
        # Get all structures and check manually (KuzuDB doesn't have built-in point-in-polygon)
        estructuras = self.query_all_estructuras(connection=connection)
        intersecting = []
        
        for estructura in estructuras:
            if self._point_in_polygon(x, y, estructura['poligono']):
                intersecting.append(estructura)
        
        return intersecting
    
    def _point_in_polygon(self, x: float, y: float, polygon: List[List[float]]) -> bool:
        """Ray casting algorithm to check if point is inside polygon"""
        if not polygon or len(polygon) < 3:
            return False
            
        n = len(polygon)
        inside = False
        
        j = n - 1
        for i in range(n):
            if ((polygon[i][1] > y) != (polygon[j][1] > y)) and \
               (x < (polygon[j][0] - polygon[i][0]) * (y - polygon[i][1]) / (polygon[j][1] - polygon[i][1]) + polygon[i][0]):
                inside = not inside
            j = i
            
        return inside
    
    def query_all_annotations(self, connection=None) -> List[Dict]:
        """Get all annotations ordered by date (most recent first)"""
        if not self.is_available():
            return []
            
        query = """
        MATCH (a:Anotation)
        RETURN a.id, a.tipo, a.comentario, a.fecha
        ORDER BY a.fecha DESC
        """
        
        try:
            result = self.execute_query(query, connection=connection)
            annotations = []
            
            if result and result.has_next():
                while result.has_next():
                    row = result.get_next()
                    annotations.append({
                        "id": row[0],
                        "tipo": row[1],
                        "comentario": row[2],
                        "fecha": row[3]
                    })
                    
            return annotations
            
        except Exception as e:
            print(f"Error consultando anotaciones: {e}")
            return []
    
    def add_annotation(self, tipo: str, comentario: str, target_type: str = "garden", target_id: str = None) -> bool:
        """Add a new annotation to the database"""
        if not self.is_available():
            return False
            
        # Generate unique annotation ID
        annotation_id = f"anotacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Create the annotation
            create_annotation_query = """
            CREATE (a:Anotation {
                id: $id,
                tipo: $tipo,
                comentario: $comentario,
                fecha: $fecha
            })
            """
            
            self.execute_query(create_annotation_query, {
                'id': annotation_id,
                'tipo': tipo,
                'comentario': comentario,
                'fecha': datetime.now()
            })
            
            # Create relationship based on target type
            if target_type == "plant" and target_id:
                relate_query = """
                MATCH (p:Planta {id: $target_id}), (a:Anotation {id: $annotation_id})
                CREATE (p)-[:HAS_ANOTATION {fecha_relacion: $fecha}]->(a)
                """
                self.execute_query(relate_query, {
                    'target_id': target_id,
                    'annotation_id': annotation_id,
                    'fecha': datetime.now()
                })
            elif target_type == "garden":
                # Default to relating with the default garden
                relate_query = """
                MATCH (hu:Huerta {id: "huerta_default"}), (a:Anotation {id: $annotation_id})
                CREATE (hu)-[:HAS_ANOTATION_HUERTA {fecha_relacion: $fecha}]->(a)
                """
                self.execute_query(relate_query, {
                    'annotation_id': annotation_id,
                    'fecha': datetime.now()
                })
            elif target_type == "vegetable" and target_id:
                relate_query = """
                MATCH (h:Hortaliza {id: $target_id}), (a:Anotation {id: $annotation_id})
                CREATE (h)-[:HAS_ANOTATION_HORTALIZA {fecha_relacion: $fecha}]->(a)
                """
                self.execute_query(relate_query, {
                    'target_id': int(target_id),
                    'annotation_id': annotation_id,
                    'fecha': datetime.now()
                })
            
            return True
            
        except Exception as e:
            print(f"Error añadiendo anotación: {e}")
            return False

    def close(self, connection=None):
        """Cerrar conexión - for isolated connections, pass the connection to close"""
        if connection:
            # Close a specific connection (new approach)
            try:
                connection.close()
                print("✓ KuzuDB connection closed")
            except:
                pass
        else:
            # Legacy approach for backward compatibility
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