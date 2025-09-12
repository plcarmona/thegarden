# Guía de Implementación: Base de Datos KuzuDB para The Garden

## Visión General

Este documento describe los pasos detallados para implementar una base de datos KuzuDB que registre toda la información del sistema The Garden. KuzuDB es una base de datos de grafos optimizada para consultas analíticas, ideal para manejar las relaciones complejas entre especies, plantas individuales, ubicaciones espaciales y anotaciones.

## Arquitectura Propuesta

### Nodos Principales

#### 1. Hortaliza (Información de Especies)
Nodo que contiene la información base de cada tipo de hortaliza/especie.

**Propiedades:**
- `id`: INTEGER PRIMARY KEY
- `nombre`: STRING
- `descripcion`: STRING
- `ciclo_dias`: INTEGER (días de siembra a cosecha)
- `siembra_mes_inicio`: INTEGER (1-12)
- `siembra_mes_fin`: INTEGER (1-12)
- `plagas_comunes`: STRING[] (array de plagas)
- `cuidados`: STRING[] (array de cuidados)
- `tamano_promedio`: DOUBLE (m²)
- `distancia_min`: DOUBLE (metros)

#### 2. Planta (Información de Cultivos Puntuales)
Nodo que representa instancias individuales de cultivos (pueden haber muchas plantas de un tipo de hortaliza).

**Propiedades:**
- `id`: STRING PRIMARY KEY
- `fecha_siembra`: DATE
- `coordenadas_x`: DOUBLE
- `coordenadas_y`: DOUBLE
- `estado`: STRING (activo, cosechado, muerto)
- `fecha_cosecha`: DATE (opcional)
- `notas`: STRING (opcional)

#### 3. Huerta (Información Espacial)
Nodo que contiene la información espacial de cultivos y estructuras, permitiendo modificar la configuración activa.

**Propiedades:**
- `id`: STRING PRIMARY KEY
- `nombre`: STRING
- `ancho`: DOUBLE (dimensiones canvas)
- `alto`: DOUBLE (dimensiones canvas)
- `configuracion_activa`: BOOLEAN
- `fecha_creacion`: TIMESTAMP
- `descripcion`: STRING (opcional)

#### 4. Anotaciones (Sistema de Comentarios)
Nodo para agregar comentarios como filtro de otros tipos de datos, con diferentes niveles de especificidad.

**Propiedades:**
- `id`: STRING PRIMARY KEY
- `tipo`: STRING (evento, foto, nota, siembra, cosecha, riego, etc.)
- `nivel_especificidad`: STRING (tipo_planta, tiempo, individuo, estacion)
- `fecha`: TIMESTAMP
- `notas`: STRING
- `fotos`: STRING[] (URLs o paths)
- `temporada`: STRING (opcional, para filtros estacionales)
- `metadata`: STRING (JSON opcional para datos adicionales)

### Relaciones (Edges)

#### IS_OF_TYPE (Planta -> Hortaliza)
Relaciona una planta específica con su tipo de hortaliza.

**Propiedades:**
- `fecha_relacion`: TIMESTAMP

#### LOCATED_IN (Planta -> Huerta)
Relaciona una planta con la huerta donde está ubicada.

**Propiedades:**
- `fecha_plantacion`: TIMESTAMP
- `area_ocupada`: DOUBLE (m² opcional)

#### CONTAINS (Huerta -> Planta)
Inversa de LOCATED_IN, para consultas eficientes.

#### ANNOTATES (Anotaciones -> [Hortaliza|Planta|Huerta])
Relaciona anotaciones con cualquier tipo de nodo.

**Propiedades:**
- `relevancia`: DOUBLE (0.0 - 1.0)
- `fecha_anotacion`: TIMESTAMP

#### TEMPORAL_CONTEXT (Anotaciones -> Anotaciones)
Para agrupar anotaciones por contexto temporal (temporada, mes, año).

## Pasos de Implementación

### Fase 1: Preparación del Entorno

#### Paso 1.1: Instalar KuzuDB
```bash
# Agregar KuzuDB a requirements.txt
echo "kuzu>=0.0.8" >> requirements.txt
pip install kuzu
```

#### Paso 1.2: Crear Estructura de Directorio
```bash
mkdir -p database/
mkdir -p database/schemas/
mkdir -p database/migrations/
mkdir -p database/seeds/
```

### Fase 2: Definición del Schema

#### Paso 2.1: Crear Schema SQL (database/schemas/garden_schema.sql)
```sql
-- Crear tablas de nodos
CREATE NODE TABLE Hortaliza (
    id INTEGER PRIMARY KEY,
    nombre STRING,
    descripcion STRING,
    ciclo_dias INTEGER,
    siembra_mes_inicio INTEGER,
    siembra_mes_fin INTEGER,
    plagas_comunes STRING[],
    cuidados STRING[],
    tamano_promedio DOUBLE,
    distancia_min DOUBLE
);

CREATE NODE TABLE Planta (
    id STRING PRIMARY KEY,
    fecha_siembra DATE,
    coordenadas_x DOUBLE,
    coordenadas_y DOUBLE,
    estado STRING,
    fecha_cosecha DATE,
    notas STRING
);

CREATE NODE TABLE Huerta (
    id STRING PRIMARY KEY,
    nombre STRING,
    ancho DOUBLE,
    alto DOUBLE,
    configuracion_activa BOOLEAN,
    fecha_creacion TIMESTAMP,
    descripcion STRING
);

CREATE NODE TABLE Anotaciones (
    id STRING PRIMARY KEY,
    tipo STRING,
    nivel_especificidad STRING,
    fecha TIMESTAMP,
    notas STRING,
    fotos STRING[],
    temporada STRING,
    metadata STRING
);

-- Crear tablas de relaciones
CREATE REL TABLE IS_OF_TYPE (
    FROM Planta TO Hortaliza,
    fecha_relacion TIMESTAMP
);

CREATE REL TABLE LOCATED_IN (
    FROM Planta TO Huerta,
    fecha_plantacion TIMESTAMP,
    area_ocupada DOUBLE
);

CREATE REL TABLE CONTAINS (
    FROM Huerta TO Planta
);

CREATE REL TABLE ANNOTATES (
    FROM Anotaciones TO Hortaliza,
    relevancia DOUBLE,
    fecha_anotacion TIMESTAMP
);

CREATE REL TABLE ANNOTATES_PLANTA (
    FROM Anotaciones TO Planta,
    relevancia DOUBLE,
    fecha_anotacion TIMESTAMP
);

CREATE REL TABLE ANNOTATES_HUERTA (
    FROM Anotaciones TO Huerta,
    relevancia DOUBLE,
    fecha_anotacion TIMESTAMP
);

CREATE REL TABLE TEMPORAL_CONTEXT (
    FROM Anotaciones TO Anotaciones,
    tipo_contexto STRING
);
```

#### Paso 2.2: Crear Script de Datos Semilla (database/seeds/initial_data.sql)
```sql
-- Insertar hortalizas base (migrar datos existentes)
CREATE (:Hortaliza {
    id: 1, 
    nombre: "Tomate", 
    descripcion: "Solanum lycopersicum",
    ciclo_dias: 120, 
    siembra_mes_inicio: 9, 
    siembra_mes_fin: 11,
    plagas_comunes: ["Trips", "Mosca blanca", "Pulgones"],
    cuidados: ["Riego regular", "Tutoreo", "Poda de brotes laterales"],
    tamano_promedio: 1.5, 
    distancia_min: 0.6
});

CREATE (:Hortaliza {
    id: 2, 
    nombre: "Lechuga", 
    descripcion: "Lactuca sativa",
    ciclo_dias: 60, 
    siembra_mes_inicio: 3, 
    siembra_mes_fin: 9,
    plagas_comunes: ["Caracoles", "Babosas", "Pulgones"],
    cuidados: ["Riego frecuente", "Sombra parcial en verano"],
    tamano_promedio: 0.3, 
    distancia_min: 0.2
});

-- Crear huerta por defecto
CREATE (:Huerta {
    id: "huerta_default", 
    nombre: "Mi Huerta Principal", 
    ancho: 800.0, 
    alto: 600.0,
    configuracion_activa: true,
    fecha_creacion: timestamp(),
    descripcion: "Huerta principal del jardín"
});
```

### Fase 3: Implementación de Capa de Acceso a Datos

#### Paso 3.1: Crear Gestor de Base de Datos (database/kuzu_manager.py)
```python
import kuzu
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os

class KuzuDBManager:
    def __init__(self, db_path: str = "database/garden.kuzu"):
        self.db_path = db_path
        self.db = None
        self.conn = None
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Crear directorio de base de datos si no existe"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    def connect(self):
        """Conectar a la base de datos"""
        if self.db is None:
            self.db = kuzu.Database(self.db_path)
            self.conn = kuzu.Connection(self.db)
        return self.conn
    
    def initialize_schema(self):
        """Inicializar schema desde archivo SQL"""
        conn = self.connect()
        
        # Leer y ejecutar schema
        with open("database/schemas/garden_schema.sql", "r") as f:
            schema_commands = f.read().split(";")
        
        for command in schema_commands:
            command = command.strip()
            if command:
                try:
                    conn.execute(command)
                except Exception as e:
                    print(f"Error ejecutando comando: {command[:100]}...")
                    print(f"Error: {e}")
    
    def load_initial_data(self):
        """Cargar datos iniciales desde archivo de semillas"""
        conn = self.connect()
        
        with open("database/seeds/initial_data.sql", "r") as f:
            seed_commands = f.read().split(";")
        
        for command in seed_commands:
            command = command.strip()
            if command and not command.startswith("--"):
                try:
                    conn.execute(command)
                except Exception as e:
                    print(f"Error cargando datos: {e}")
    
    def execute_query(self, query: str, parameters: Dict = None) -> Any:
        """Ejecutar consulta con parámetros opcionales"""
        conn = self.connect()
        try:
            if parameters:
                return conn.execute(query, parameters)
            else:
                return conn.execute(query)
        except Exception as e:
            print(f"Error ejecutando consulta: {query}")
            print(f"Error: {e}")
            raise
    
    def close(self):
        """Cerrar conexión"""
        if self.conn:
            self.conn.close()
        if self.db:
            self.db.close()

# Instancia global
kuzu_manager = KuzuDBManager()
```

#### Paso 3.2: Crear Adaptador de Modelos (database/model_adapter.py)
```python
from typing import List, Dict, Any, Optional
from app.models import Hortaliza, CultivoActivo, Anotacion, Coordenada
from database.kuzu_manager import kuzu_manager
from datetime import datetime

class ModelAdapter:
    """Adaptador entre modelos Pydantic y KuzuDB"""
    
    def __init__(self):
        self.kuzu = kuzu_manager
    
    def migrate_hortalizas_to_kuzu(self, hortalizas: Dict[int, Hortaliza]):
        """Migrar hortalizas existentes a KuzuDB"""
        for hortaliza in hortalizas.values():
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
    
    def create_planta_in_kuzu(self, cultivo: CultivoActivo, huerta_id: str = "huerta_default"):
        """Crear planta en KuzuDB con relaciones"""
        
        # Crear nodo Planta
        create_planta_query = """
        CREATE (:Planta {
            id: $id,
            fecha_siembra: $fecha_siembra,
            coordenadas_x: $coordenadas_x,
            coordenadas_y: $coordenadas_y,
            estado: $estado,
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
        CREATE (p)-[:LOCATED_IN {fecha_plantacion: $fecha}]->(hu),
               (hu)-[:CONTAINS]->(p)
        """
        
        self.kuzu.execute_query(create_location_query, {
            "planta_id": cultivo.id,
            "huerta_id": huerta_id,
            "fecha": cultivo.fecha_siembra
        })
    
    def query_planta_by_coordinates(self, x: float, y: float, radius: float = 20.0) -> Optional[Dict]:
        """Consultar planta por coordenadas (RF-003)"""
        query = """
        MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
        WHERE abs(p.coordenadas_x - $x) <= $radius 
        AND abs(p.coordenadas_y - $y) <= $radius
        RETURN p.id, p.fecha_siembra, p.estado, h.nombre, h.descripcion
        LIMIT 1
        """
        
        result = self.kuzu.execute_query(query, {
            "x": x, "y": y, "radius": radius
        })
        
        return result.get_next() if result.has_next() else None
    
    def create_anotacion_in_kuzu(self, anotacion: Anotacion):
        """Crear anotación en KuzuDB con relaciones"""
        
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

# Instancia global
model_adapter = ModelAdapter()
```

### Fase 4: Integración con Modelos Existentes

#### Paso 4.1: Modificar models.py para Usar KuzuDB
```python
# En app/models.py, agregar al final:

from database.model_adapter import model_adapter

class HuertaKuzu(Huerta):
    """Versión extendida de Huerta con soporte KuzuDB"""
    
    def __init__(self):
        super().__init__()
        # Migrar datos existentes a KuzuDB al inicializar
        try:
            model_adapter.kuzu.connect()
            model_adapter.migrate_hortalizas_to_kuzu(self.hortalizas_db)
        except Exception as e:
            print(f"Error inicializando KuzuDB: {e}")
    
    def agregar_cultivo_activo(self, cultivo: CultivoActivo) -> str:
        """Override para persistir también en KuzuDB"""
        # Llamar método padre
        cultivo_id = super().agregar_cultivo_activo(cultivo)
        
        # Persistir en KuzuDB
        try:
            model_adapter.create_planta_in_kuzu(cultivo)
        except Exception as e:
            print(f"Error persistiendo cultivo en KuzuDB: {e}")
        
        return cultivo_id
    
    def obtener_planta_en_coordenada(self, x: float, y: float) -> Optional[CultivoActivo]:
        """Override para consultar desde KuzuDB"""
        try:
            # Intentar consulta desde KuzuDB primero
            kuzu_result = model_adapter.query_planta_by_coordinates(x, y)
            if kuzu_result:
                # Convertir resultado de KuzuDB a modelo Pydantic
                # (implementar conversión según estructura de respuesta)
                pass
        except Exception as e:
            print(f"Error consultando KuzuDB: {e}")
        
        # Fallback a consulta en memoria
        return super().obtener_planta_en_coordenada(x, y)
    
    def agregar_anotacion(self, anotacion: Anotacion) -> str:
        """Override para persistir también en KuzuDB"""
        # Llamar método padre
        anotacion_id = super().agregar_anotacion(anotacion)
        
        # Persistir en KuzuDB
        try:
            model_adapter.create_anotacion_in_kuzu(anotacion)
        except Exception as e:
            print(f"Error persistiendo anotación en KuzuDB: {e}")
        
        return anotacion_id
```

### Fase 5: Scripts de Utilidad

#### Paso 5.1: Script de Inicialización (scripts/init_database.py)
```python
#!/usr/bin/env python3
"""
Script para inicializar base de datos KuzuDB
"""
import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.kuzu_manager import kuzu_manager

def main():
    print("Inicializando base de datos KuzuDB...")
    
    try:
        # Conectar
        kuzu_manager.connect()
        print("✓ Conexión establecida")
        
        # Inicializar schema
        kuzu_manager.initialize_schema()
        print("✓ Schema creado")
        
        # Cargar datos iniciales
        kuzu_manager.load_initial_data()
        print("✓ Datos iniciales cargados")
        
        print("\n🌱 Base de datos inicializada correctamente!")
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return 1
    
    finally:
        kuzu_manager.close()
    
    return 0

if __name__ == "__main__":
    exit(main())
```

#### Paso 5.2: Script de Consultas de Ejemplo (scripts/sample_queries.py)
```python
#!/usr/bin/env python3
"""
Ejemplos de consultas KuzuDB para The Garden
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.kuzu_manager import kuzu_manager

def query_plantas_por_tipo():
    """Consultar todas las plantas de un tipo específico"""
    query = """
    MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza {nombre: "Tomate"})
    RETURN p.id, p.coordenadas_x, p.coordenadas_y, p.estado, p.fecha_siembra
    """
    return kuzu_manager.execute_query(query)

def query_anotaciones_por_temporada():
    """Consultar anotaciones por temporada"""
    query = """
    MATCH (a:Anotaciones {temporada: "primavera"})
    RETURN a.tipo, a.notas, a.fecha
    ORDER BY a.fecha
    """
    return kuzu_manager.execute_query(query)

def query_plantas_cercanas(x: float, y: float, radius: float = 50.0):
    """Encontrar plantas cerca de una coordenada"""
    query = """
    MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
    WHERE abs(p.coordenadas_x - $x) <= $radius 
    AND abs(p.coordenadas_y - $y) <= $radius
    RETURN p.id, h.nombre, p.coordenadas_x, p.coordenadas_y,
           sqrt(pow(p.coordenadas_x - $x, 2) + pow(p.coordenadas_y - $y, 2)) as distancia
    ORDER BY distancia
    """
    return kuzu_manager.execute_query(query, {"x": x, "y": y, "radius": radius})

def query_historial_cultivo():
    """Consultar historial completo de un cultivo"""
    query = """
    MATCH (p:Planta {id: $planta_id})-[:IS_OF_TYPE]->(h:Hortaliza)
    OPTIONAL MATCH (a:Anotaciones)-[:ANNOTATES_PLANTA]->(p)
    RETURN p.*, h.nombre, h.descripcion, 
           collect({
               anotacion_id: a.id,
               tipo: a.tipo, 
               fecha: a.fecha, 
               notas: a.notas
           }) as anotaciones
    """
    return kuzu_manager.execute_query(query, {"planta_id": "cultivo_1"})

def main():
    print("🔍 Ejecutando consultas de ejemplo...")
    
    try:
        kuzu_manager.connect()
        
        print("\n1. Plantas de Tomate:")
        result = query_plantas_por_tipo()
        while result.has_next():
            print(f"  - {result.get_next()}")
        
        print("\n2. Plantas cercanas a (100, 100):")
        result = query_plantas_cercanas(100, 100)
        while result.has_next():
            print(f"  - {result.get_next()}")
        
        print("\n3. Anotaciones de primavera:")
        result = query_anotaciones_por_temporada()
        while result.has_next():
            print(f"  - {result.get_next()}")
            
    except Exception as e:
        print(f"❌ Error ejecutando consultas: {e}")
        return 1
    
    finally:
        kuzu_manager.close()
    
    return 0

if __name__ == "__main__":
    exit(main())
```

### Fase 6: Testing

#### Paso 6.1: Crear Tests para KuzuDB (tests/test_kuzu_integration.py)
```python
import pytest
import os
import tempfile
from app.models import Hortaliza, CultivoActivo, Anotacion, Coordenada, TipoAnotacion, NivelEspecificidad
from database.kuzu_manager import KuzuDBManager
from database.model_adapter import ModelAdapter

@pytest.fixture
def temp_kuzu_db():
    """Fixture para base de datos temporal"""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test.kuzu")
        manager = KuzuDBManager(db_path)
        yield manager
        manager.close()

def test_kuzu_connection(temp_kuzu_db):
    """Test conexión básica a KuzuDB"""
    conn = temp_kuzu_db.connect()
    assert conn is not None
    
def test_create_hortaliza_node(temp_kuzu_db):
    """Test creación de nodo Hortaliza"""
    conn = temp_kuzu_db.connect()
    
    # Crear tabla de nodos
    conn.execute("""
        CREATE NODE TABLE Hortaliza (
            id INTEGER PRIMARY KEY,
            nombre STRING,
            descripcion STRING
        )
    """)
    
    # Insertar hortaliza
    conn.execute("""
        CREATE (:Hortaliza {
            id: 1,
            nombre: "Tomate Test",
            descripcion: "Test description"
        })
    """)
    
    # Consultar
    result = conn.execute("MATCH (h:Hortaliza) RETURN h.nombre")
    assert result.has_next()
    row = result.get_next()
    assert row[0] == "Tomate Test"

def test_coordinate_query(temp_kuzu_db):
    """Test consulta por coordenadas"""
    adapter = ModelAdapter()
    adapter.kuzu = temp_kuzu_db
    
    # Setup básico (crear tablas)
    conn = temp_kuzu_db.connect()
    conn.execute("""
        CREATE NODE TABLE Planta (
            id STRING PRIMARY KEY,
            coordenadas_x DOUBLE,
            coordenadas_y DOUBLE,
            estado STRING
        )
    """)
    
    # Crear planta
    conn.execute("""
        CREATE (:Planta {
            id: "test_plant",
            coordenadas_x: 100.0,
            coordenadas_y: 100.0,
            estado: "activo"
        })
    """)
    
    # Consultar por coordenadas cercanas
    result = conn.execute("""
        MATCH (p:Planta)
        WHERE abs(p.coordenadas_x - 100.0) <= 20.0 
        AND abs(p.coordenadas_y - 100.0) <= 20.0
        RETURN p.id
    """)
    
    assert result.has_next()
    row = result.get_next()
    assert row[0] == "test_plant"

def test_annotation_relationships(temp_kuzu_db):
    """Test relaciones de anotaciones"""
    conn = temp_kuzu_db.connect()
    
    # Crear tablas
    conn.execute("CREATE NODE TABLE Planta (id STRING PRIMARY KEY)")
    conn.execute("CREATE NODE TABLE Anotaciones (id STRING PRIMARY KEY, tipo STRING)")
    conn.execute("CREATE REL TABLE ANNOTATES (FROM Anotaciones TO Planta)")
    
    # Crear datos
    conn.execute('CREATE (:Planta {id: "plant1"})')
    conn.execute('CREATE (:Anotaciones {id: "ann1", tipo: "nota"})')
    
    # Crear relación
    conn.execute("""
        MATCH (a:Anotaciones {id: "ann1"}), (p:Planta {id: "plant1"})
        CREATE (a)-[:ANNOTATES]->(p)
    """)
    
    # Consultar relación
    result = conn.execute("""
        MATCH (a:Anotaciones)-[r:ANNOTATES]->(p:Planta)
        RETURN a.id, p.id
    """)
    
    assert result.has_next()
    row = result.get_next()
    assert row[0] == "ann1"
    assert row[1] == "plant1"
```

### Fase 7: Integración Final

#### Paso 7.1: Actualizar main.py
```python
# Al final de main.py, agregar inicialización de KuzuDB

@app.on_event("startup")
async def startup_event():
    """Inicializar KuzuDB al startup"""
    try:
        from database.kuzu_manager import kuzu_manager
        kuzu_manager.connect()
        print("✓ KuzuDB conectado")
    except Exception as e:
        print(f"⚠️ Warning: KuzuDB no disponible - {e}")

@app.on_event("shutdown") 
async def shutdown_event():
    """Cerrar KuzuDB al shutdown"""
    try:
        from database.kuzu_manager import kuzu_manager
        kuzu_manager.close()
        print("✓ KuzuDB desconectado")
    except Exception as e:
        print(f"Error cerrando KuzuDB: {e}")
```

#### Paso 7.2: Agregar Endpoints para Consultas KuzuDB
```python
# En app/huerta.py, agregar endpoints adicionales

@router.get("/analytics/plants-by-type/{hortaliza_id}")
async def get_plants_by_type(hortaliza_id: int):
    """Obtener todas las plantas de un tipo específico usando KuzuDB"""
    try:
        from database.kuzu_manager import kuzu_manager
        
        query = """
        MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza {id: $hortaliza_id})
        RETURN p.id, p.coordenadas_x, p.coordenadas_y, p.estado, h.nombre
        """
        
        result = kuzu_manager.execute_query(query, {"hortaliza_id": hortaliza_id})
        plants = []
        while result.has_next():
            row = result.get_next()
            plants.append({
                "id": row[0],
                "x": row[1], 
                "y": row[2],
                "estado": row[3],
                "tipo": row[4]
            })
        
        return {"plants": plants}
        
    except Exception as e:
        return {"error": f"KuzuDB query failed: {e}"}

@router.get("/analytics/spatial-query/{x}/{y}")
async def spatial_query(x: float, y: float, radius: float = 50.0):
    """Consulta espacial avanzada usando KuzuDB"""
    try:
        from database.kuzu_manager import kuzu_manager
        
        query = """
        MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
        WHERE abs(p.coordenadas_x - $x) <= $radius 
        AND abs(p.coordenadas_y - $y) <= $radius
        RETURN p.id, h.nombre, p.coordenadas_x, p.coordenadas_y,
               sqrt(pow(p.coordenadas_x - $x, 2) + pow(p.coordenadas_y - $y, 2)) as distancia
        ORDER BY distancia
        """
        
        result = kuzu_manager.execute_query(query, {
            "x": x, "y": y, "radius": radius
        })
        
        nearby_plants = []
        while result.has_next():
            row = result.get_next()
            nearby_plants.append({
                "id": row[0],
                "tipo": row[1],
                "x": row[2],
                "y": row[3], 
                "distancia": row[4]
            })
        
        return {"nearby_plants": nearby_plants, "center": {"x": x, "y": y}, "radius": radius}
        
    except Exception as e:
        return {"error": f"Spatial query failed: {e}"}
```

## Cronograma de Implementación

### Semana 1: Preparación
- [ ] Instalar KuzuDB y configurar entorno
- [ ] Crear estructura de directorios
- [ ] Definir schemas SQL

### Semana 2: Desarrollo Core  
- [ ] Implementar KuzuDBManager
- [ ] Crear ModelAdapter
- [ ] Desarrollar scripts de inicialización

### Semana 3: Integración
- [ ] Integrar con modelos existentes
- [ ] Crear endpoints adicionales
- [ ] Implementar consultas analíticas

### Semana 4: Testing y Optimización
- [ ] Tests completos de integración
- [ ] Optimización de consultas
- [ ] Documentación final

## Consultas de Ejemplo Útiles

### 1. Plantas por Temporada de Siembra
```sql
MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
WHERE h.siembra_mes_inicio <= $mes_actual <= h.siembra_mes_fin
RETURN h.nombre, count(p) as cantidad_plantada
ORDER BY cantidad_plantada DESC
```

### 2. Análisis de Densidad Espacial
```sql
MATCH (p:Planta)
WITH p.coordenadas_x / 50 as grid_x, p.coordenadas_y / 50 as grid_y, count(p) as plantas_por_celda
WHERE plantas_por_celda > 3
RETURN grid_x * 50 as zona_x, grid_y * 50 as zona_y, plantas_por_celda
ORDER BY plantas_por_celda DESC
```

### 3. Historial de Anotaciones por Cultivo
```sql
MATCH (p:Planta {id: $planta_id})-[:IS_OF_TYPE]->(h:Hortaliza)
OPTIONAL MATCH (a:Anotaciones)-[:ANNOTATES_PLANTA]->(p)
RETURN p.fecha_siembra, h.nombre,
       collect({fecha: a.fecha, tipo: a.tipo, notas: a.notas}) as historial
ORDER BY a.fecha
```

### 4. Recomendaciones de Rotación
```sql
MATCH (p1:Planta)-[:LOCATED_IN]->(hu:Huerta),
      (p1)-[:IS_OF_TYPE]->(h1:Hortaliza)
WHERE p1.estado = 'cosechado'
OPTIONAL MATCH (p2:Planta)-[:LOCATED_IN]->(hu),
                (p2)-[:IS_OF_TYPE]->(h2:Hortaliza)
WHERE p2.estado = 'activo' 
AND abs(p1.coordenadas_x - p2.coordenadas_x) < h2.distancia_min
AND abs(p1.coordenadas_y - p2.coordenadas_y) < h2.distancia_min
RETURN p1.coordenadas_x, p1.coordenadas_y, h1.nombre as cultivado_antes, 
       h2.nombre as actualmente, 
       CASE WHEN p2 IS NULL THEN 'disponible' ELSE 'ocupado' END as estado_area
```

## Consideraciones de Rendimiento

1. **Índices Espaciales**: KuzuDB optimiza consultas por coordenadas automáticamente
2. **Batch Inserts**: Para cargas masivas de datos, usar transacciones por lotes
3. **Consultas Materializadas**: Para análisis frecuentes, considerar vistas materializadas
4. **Particionado Temporal**: Separar datos por temporada para consultas más rápidas

## Migración de Datos Existentes

1. **Backup Previo**: Respaldar datos actuales en JSON/CSV
2. **Migración Gradual**: Mantener ambos sistemas durante transición
3. **Validación**: Comparar resultados entre sistema viejo y nuevo
4. **Rollback Plan**: Procedimiento para revertir si es necesario

Este documento proporciona una guía completa para implementar KuzuDB en The Garden, manteniendo la funcionalidad existente y agregando capacidades analíticas avanzadas.