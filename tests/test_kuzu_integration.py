"""
Tests para integración KuzuDB
Verifica la funcionalidad de base de datos de grafos con fallback a sistema en memoria
"""
import pytest
import tempfile
import os
from app.models import Hortaliza, CultivoActivo, Anotacion, Coordenada, TipoAnotacion, NivelEspecificidad
from database.kuzu_manager import KuzuDBManager
from database.model_adapter import ModelAdapter


class TestKuzuIntegration:
    """Tests para verificar integración KuzuDB"""
    
    def test_kuzu_manager_creation(self):
        """Test creación básica del manager"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.kuzu")
            manager = KuzuDBManager(db_path)
            
            # Debe crearse sin errores
            assert manager.db_path == db_path
            
            # Si KuzuDB no está disponible, debe manejarlo gracefully
            if not manager._kuzu_available:
                assert not manager.is_available()
            else:
                # Si está disponible, debe conectarse
                conn = manager.connect()
                assert conn is not None
                manager.close()
    
    def test_model_adapter_creation(self):
        """Test creación del adaptador de modelos"""
        adapter = ModelAdapter()
        assert adapter.kuzu is not None
    
    def test_compatibility_mode(self):
        """Test que el sistema funciona sin KuzuDB instalado"""
        # Crear manager en directorio temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.kuzu")
            manager = KuzuDBManager(db_path)
            
            # Operaciones deben fallar gracefully si KuzuDB no está disponible
            if not manager.is_available():
                result = manager.execute_query("MATCH (n) RETURN n")
                assert result is None
                
                plantas = manager.query_plantas_by_coordinates(100, 100)
                assert plantas == []
            
            # Cerrar debe funcionar sin errores
            manager.close()
    
    def test_migration_without_kuzu(self):
        """Test migración de datos funciona sin KuzuDB"""
        adapter = ModelAdapter()
        
        # Crear datos de prueba
        hortalizas = {
            1: Hortaliza(
                id=1, nombre="Test", descripcion="Test plant",
                ciclo_dias=60, siembra_mes_inicio=1, siembra_mes_fin=12,
                plagas_comunes=[], cuidados=[], tamano_promedio=1.0, distancia_min=0.5
            )
        }
        
        # Migración debe fallar gracefully si KuzuDB no está disponible
        result = adapter.migrate_hortalizas_to_kuzu(hortalizas)
        
        if not adapter.kuzu.is_available():
            assert result is False
        # Si KuzuDB está disponible, debería funcionar
        # (pero no podemos garantizar que esté instalado en el entorno de test)
    
    def test_cultivo_creation_without_kuzu(self):
        """Test creación de cultivo funciona sin KuzuDB"""
        adapter = ModelAdapter()
        
        cultivo = CultivoActivo(
            id="test_cultivo",
            hortaliza_id=1,
            coordenadas=Coordenada(x=100, y=100),
            fecha_siembra="2024-01-15"
        )
        
        # Debe fallar gracefully si KuzuDB no está disponible
        result = adapter.create_planta_in_kuzu(cultivo)
        
        if not adapter.kuzu.is_available():
            assert result is False
    
    def test_query_without_kuzu(self):
        """Test consultas funcionan sin KuzuDB"""
        adapter = ModelAdapter()
        
        # Consulta por coordenadas debe devolver vacío si KuzuDB no está disponible
        result = adapter.query_planta_by_coordinates(100, 100)
        
        if not adapter.kuzu.is_available():
            assert result is None
        
        # Consultas espaciales deben devolver lista vacía
        plantas = adapter.get_spatial_query(100, 100)
        
        if not adapter.kuzu.is_available():
            assert plantas == []
    
    def test_anotacion_creation_without_kuzu(self):
        """Test creación de anotación funciona sin KuzuDB"""
        adapter = ModelAdapter()
        
        anotacion = Anotacion(
            id="test_anotacion",
            tipo=TipoAnotacion.NOTA,
            nivel_especificidad=NivelEspecificidad.INDIVIDUO,
            fecha="2024-01-15T10:00:00",
            notas="Test annotation"
        )
        
        # Debe fallar gracefully si KuzuDB no está disponible
        result = adapter.create_anotacion_in_kuzu(anotacion)
        
        if not adapter.kuzu.is_available():
            assert result is False
    
    def test_initialization_script_safety(self):
        """Test que scripts de inicialización manejan errores correctamente"""
        # Verificar que los archivos de schema y seeds existen
        schema_path = "database/schemas/garden_schema.sql"
        seeds_path = "database/seeds/initial_data.sql"
        
        assert os.path.exists(schema_path), f"Schema file missing: {schema_path}"
        assert os.path.exists(seeds_path), f"Seeds file missing: {seeds_path}"
        
        # Verificar contenido básico
        with open(schema_path, 'r') as f:
            schema_content = f.read()
            assert "CREATE NODE TABLE Hortaliza" in schema_content
            assert "CREATE NODE TABLE Planta" in schema_content
            assert "CREATE NODE TABLE Huerta" in schema_content
            assert "CREATE NODE TABLE Anotaciones" in schema_content
        
        with open(seeds_path, 'r') as f:
            seeds_content = f.read()
            assert "CREATE (:Hortaliza" in seeds_content
            assert "CREATE (:Huerta" in seeds_content
    
    def test_fallback_behavior(self):
        """Test que el sistema mantiene funcionalidad sin KuzuDB"""
        # Importar modelos principales
        from app.models import Huerta, huerta_instance
        
        # El sistema debe funcionar normalmente sin KuzuDB
        assert len(huerta_instance.hortalizas_db) > 0
        assert huerta_instance.dimensiones["ancho"] == 800
        
        # Operaciones básicas deben funcionar
        cultivo = CultivoActivo(
            hortaliza_id=1,
            coordenadas=Coordenada(x=50, y=50),
            fecha_siembra="2024-01-15"
        )
        
        cultivo_id = huerta_instance.agregar_cultivo_activo(cultivo)
        assert cultivo_id is not None
        
        # Consulta debe funcionar
        planta = huerta_instance.obtener_planta_en_coordenada(50, 50)
        assert planta is not None
        assert planta.hortaliza_id == 1