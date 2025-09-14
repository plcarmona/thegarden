"""
Tests para el módulo de base de datos KuzuDB
Verifica que el gestor de base de datos funciona correctamente
"""
import pytest
import tempfile
import os
from database.kuzu_manager import KuzuDBManager


class TestKuzuDBManager:
    """Tests para verificar el gestor KuzuDB"""
    
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
    
    def test_query_safety(self):
        """Test que las consultas manejan errores correctamente"""
        manager = KuzuDBManager()
        
        if manager.is_available():
            # Test consulta inválida
            try:
                result = manager.execute_query("INVALID QUERY")
                # Si no lanza excepción, debe retornar None
                assert result is None
            except Exception:
                # Excepción es aceptable para consulta inválida
                pass
        else:
            # Sin KuzuDB disponible, debe retornar None
            result = manager.execute_query("MATCH (n) RETURN n")
            assert result is None
    
    def test_schema_files_exist(self):
        """Test que los archivos de schema existen"""
        schema_path = "database/schemas/garden_schema.sql"
        seeds_path = "database/seeds/initial_data.sql"
        
        assert os.path.exists(schema_path)
        assert os.path.exists(seeds_path)
        
        # Verificar que contienen algo
        with open(schema_path, "r") as f:
            schema_content = f.read()
            assert len(schema_content.strip()) > 0
        
        with open(seeds_path, "r") as f:
            seeds_content = f.read()
            assert len(seeds_content.strip()) > 0