import pytest
import sys
import os

# Add the current directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from app.models import Huerta, Poligono, CultivoActivo, Coordenada


def test_huerta_creation():
    """Test basic Huerta creation"""
    huerta = Huerta()
    assert len(huerta.poligonos) == 0
    assert len(huerta.cultivos_activos) == 0
    assert huerta.dimensiones["ancho"] == 800
    assert huerta.dimensiones["alto"] == 600


def test_polygon_creation():
    """Test polygon creation (RF-001)"""
    huerta = Huerta()
    polygon = Poligono(
        coordinates=[
            Coordenada(x=10, y=10),
            Coordenada(x=50, y=10),
            Coordenada(x=50, y=50),
            Coordenada(x=10, y=50)
        ],
        tipo="cultivo",
        nombre="Test Area"
    )
    
    polygon_id = huerta.agregar_poligono(polygon)
    assert polygon_id == "poly_1"
    assert len(huerta.poligonos) == 1
    assert huerta.poligonos[0].nombre == "Test Area"


def test_coordinate_query_empty():
    """Test coordinate query with no crops (RF-003)"""
    huerta = Huerta()
    result = huerta.obtener_planta_en_coordenada(100, 100)
    assert result is None


def test_add_active_crop():
    """Test adding active crop (RF-005)"""
    huerta = Huerta()
    crop = CultivoActivo(
        hortaliza_id=1,
        coordenadas=Coordenada(x=100, y=100),
        fecha_siembra="2024-01-15"
    )
    
    crop_id = huerta.agregar_cultivo_activo(crop)
    assert crop_id == "cultivo_1"
    assert len(huerta.cultivos_activos) == 1


def test_coordinate_query_with_crop():
    """Test coordinate query with existing crop (RF-003)"""
    huerta = Huerta()
    crop = CultivoActivo(
        hortaliza_id=1,
        coordenadas=Coordenada(x=100, y=100),
        fecha_siembra="2024-01-15"
    )
    
    huerta.agregar_cultivo_activo(crop)
    result = huerta.obtener_planta_en_coordenada(100, 100)
    assert result is not None
    assert result.hortaliza_id == 1


def test_collision_detection():
    """Test collision detection prevents overlapping crops"""
    huerta = Huerta()
    
    # Add first crop
    crop1 = CultivoActivo(
        hortaliza_id=1,
        coordenadas=Coordenada(x=100, y=100),
        fecha_siembra="2024-01-15"
    )
    huerta.agregar_cultivo_activo(crop1)
    
    # Try to add overlapping crop
    crop2 = CultivoActivo(
        hortaliza_id=2,
        coordenadas=Coordenada(x=105, y=105),  # Very close
        fecha_siembra="2024-01-15"
    )
    
    with pytest.raises(ValueError, match="Colisión detectada"):
        huerta.agregar_cultivo_activo(crop2)


def test_map_loading():
    """Test map loading functionality"""
    huerta = Huerta()
    
    # Add some data
    polygon = Poligono(
        coordinates=[Coordenada(x=0, y=0), Coordenada(x=10, y=0), Coordenada(x=10, y=10)],
        tipo="cultivo"
    )
    huerta.agregar_poligono(polygon)
    
    crop = CultivoActivo(
        hortaliza_id=1,
        coordenadas=Coordenada(x=50, y=50),
        fecha_siembra="2024-01-15"
    )
    huerta.agregar_cultivo_activo(crop)
    
    # Load map
    map_data = huerta.cargar_mapa()
    assert len(map_data["poligonos"]) == 1
    assert len(map_data["cultivos_activos"]) == 1
    assert map_data["dimensiones"]["ancho"] == 800