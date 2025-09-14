"""
Tests for TOML data loader functionality
Validates that configuration loading works correctly
"""
import pytest
import tempfile
import os
import toml
from database.toml_loader import TomlDataLoader


class TestTomlDataLoader:
    """Tests for TOML configuration loader"""
    
    def test_load_valid_config(self):
        """Test loading a valid TOML configuration"""
        # Create temporary TOML file
        config_data = {
            'metadata': {
                'version': '1.0',
                'description': 'Test config'
            },
            'hortalizas': [
                {
                    'id': 1,
                    'nombre': 'Test Veggie',
                    'descripcion': 'A test vegetable',
                    'ciclo_dias': 30,
                    'siembra_mes_inicio': 3,
                    'siembra_mes_fin': 6,
                    'plagas_comunes': ['Test pest'],
                    'cuidados': ['Test care'],
                    'tamano_promedio': 0.5,
                    'distancia_min': 0.2
                }
            ],
            'estructuras': {
                'estructura': [
                    {
                        'id': 'test_structure',
                        'nombre': 'Test Structure',
                        'tipo': 'test',
                        'descripcion': 'A test structure',
                        'poligono': [[0, 0], [10, 0], [10, 10], [0, 10]]
                    }
                ]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            toml.dump(config_data, f)
            temp_path = f.name
        
        try:
            loader = TomlDataLoader(temp_path)
            
            # Test metadata access
            assert loader._data['metadata']['version'] == '1.0'
            
            # Test hortalizas
            hortalizas = loader.get_hortalizas()
            assert len(hortalizas) == 1
            assert hortalizas[0]['nombre'] == 'Test Veggie'
            assert hortalizas[0]['ciclo_dias'] == 30
            
            # Test specific hortaliza by ID
            hortaliza = loader.get_hortaliza_by_id(1)
            assert hortaliza is not None
            assert hortaliza['nombre'] == 'Test Veggie'
            
            # Test non-existent hortaliza
            assert loader.get_hortaliza_by_id(999) is None
            
            # Test estructuras
            estructuras = loader.get_estructuras()
            assert len(estructuras) == 1
            assert estructuras[0]['nombre'] == 'Test Structure'
            assert len(estructuras[0]['poligono']) == 4
            
            # Test specific estructura by ID
            estructura = loader.get_estructura_by_id('test_structure')
            assert estructura is not None
            assert estructura['nombre'] == 'Test Structure'
            
            # Test validation
            assert loader.validate_config() == True
            
        finally:
            os.unlink(temp_path)
    
    def test_missing_config_file(self):
        """Test behavior when config file doesn't exist"""
        with pytest.raises(FileNotFoundError):
            TomlDataLoader('/nonexistent/path/config.toml')
    
    def test_invalid_toml(self):
        """Test behavior with invalid TOML syntax"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("invalid toml [syntax")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                TomlDataLoader(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_empty_config(self):
        """Test behavior with empty/minimal config"""
        config_data = {}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            toml.dump(config_data, f)
            temp_path = f.name
        
        try:
            loader = TomlDataLoader(temp_path)
            
            # Should return empty lists for missing sections
            assert loader.get_hortalizas() == []
            assert loader.get_estructuras() == []
            assert loader.get_hortaliza_by_id(1) is None
            assert loader.get_estructura_by_id('test') is None
            
        finally:
            os.unlink(temp_path)
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid config
        valid_config = {
            'hortalizas': [
                {
                    'id': 1,
                    'nombre': 'Test',
                    'descripcion': 'Test desc',
                    'ciclo_dias': 30
                }
            ],
            'estructuras': {
                'estructura': [
                    {
                        'id': 'test',
                        'nombre': 'Test Structure',
                        'tipo': 'test',
                        'poligono': [[0, 0], [1, 1]]
                    }
                ]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            toml.dump(valid_config, f)
            temp_path = f.name
        
        try:
            loader = TomlDataLoader(temp_path)
            assert loader.validate_config() == True
        finally:
            os.unlink(temp_path)
        
        # Invalid config - missing required field
        invalid_config = {
            'hortalizas': [
                {
                    'id': 1,
                    'descripcion': 'Missing nombre field',
                    'ciclo_dias': 30
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            toml.dump(invalid_config, f)
            temp_path = f.name
        
        try:
            loader = TomlDataLoader(temp_path)
            assert loader.validate_config() == False
        finally:
            os.unlink(temp_path)
    
    def test_reload_functionality(self):
        """Test config reloading"""
        config_data = {
            'hortalizas': [
                {
                    'id': 1,
                    'nombre': 'Original',
                    'descripcion': 'Original desc',
                    'ciclo_dias': 30
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            toml.dump(config_data, f)
            temp_path = f.name
        
        try:
            loader = TomlDataLoader(temp_path)
            
            # Initial load
            hortalizas = loader.get_hortalizas()
            assert hortalizas[0]['nombre'] == 'Original'
            
            # Modify file
            config_data['hortalizas'][0]['nombre'] = 'Modified'
            with open(temp_path, 'w') as f:
                toml.dump(config_data, f)
            
            # Reload
            loader.reload()
            hortalizas = loader.get_hortalizas()
            assert hortalizas[0]['nombre'] == 'Modified'
            
        finally:
            os.unlink(temp_path)