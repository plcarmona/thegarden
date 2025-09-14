"""
TOML Data Loader for The Garden
Handles loading and parsing of configuration data from TOML files
"""
import os
import toml
from typing import Dict, List, Any, Optional
from datetime import datetime


class TomlDataLoader:
    """Loads and manages TOML configuration data for the garden"""
    
    def __init__(self, config_path: str = "config/hortalizas.toml"):
        self.config_path = config_path
        self._data = None
        self._load_data()
    
    def _load_data(self):
        """Load data from TOML file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._data = toml.load(f)
        except Exception as e:
            raise ValueError(f"Error loading TOML config: {e}")
    
    def get_hortalizas(self) -> List[Dict[str, Any]]:
        """Get list of all hortalizas from TOML config"""
        if not self._data or 'hortalizas' not in self._data:
            return []
        return self._data['hortalizas']
    
    def get_estructuras(self) -> List[Dict[str, Any]]:
        """Get list of all structures from TOML config"""
        if not self._data or 'estructuras' not in self._data or 'estructura' not in self._data['estructuras']:
            return []
        return self._data['estructuras']['estructura']
    
    def get_hortaliza_by_id(self, hortaliza_id: int) -> Optional[Dict[str, Any]]:
        """Get specific hortaliza by ID"""
        hortalizas = self.get_hortalizas()
        for hortaliza in hortalizas:
            if hortaliza.get('id') == hortaliza_id:
                return hortaliza
        return None
    
    def get_estructura_by_id(self, estructura_id: str) -> Optional[Dict[str, Any]]:
        """Get specific structure by ID"""
        estructuras = self.get_estructuras()
        for estructura in estructuras:
            if estructura.get('id') == estructura_id:
                return estructura
        return None
    
    def validate_config(self) -> bool:
        """Validate that the TOML config has required fields"""
        if not self._data:
            return False
        
        # Check hortalizas
        hortalizas = self.get_hortalizas()
        for hortaliza in hortalizas:
            required_fields = ['id', 'nombre', 'descripcion', 'ciclo_dias']
            for field in required_fields:
                if field not in hortaliza:
                    print(f"Missing required field '{field}' in hortaliza: {hortaliza}")
                    return False
        
        # Check estructuras (optional)
        estructuras = self.get_estructuras()
        for estructura in estructuras:
            required_fields = ['id', 'nombre', 'tipo', 'poligono']
            for field in required_fields:
                if field not in estructura:
                    print(f"Missing required field '{field}' in structure: {estructura}")
                    return False
        
        return True
    
    def reload(self):
        """Reload data from TOML file"""
        self._load_data()


# Global instance for easy access
toml_loader = TomlDataLoader()