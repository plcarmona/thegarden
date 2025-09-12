import pytest
import sys
import os
from datetime import datetime

# Add the current directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from app.models import Huerta, Anotacion, TipoAnotacion, NivelEspecificidad, Coordenada
from app.weather import WeatherService
from app.calendar import CalendarService


def test_hortalizas_database():
    """Test hortalizas database (RF-002)"""
    huerta = Huerta()
    
    # Test listing hortalizas
    hortalizas = huerta.listar_hortalizas()
    assert len(hortalizas) == 4
    
    # Test getting specific hortaliza
    tomate = huerta.obtener_hortaliza(1)
    assert tomate is not None
    assert tomate.nombre == "Tomate"
    assert tomate.ciclo_dias == 120
    
    # Test non-existent hortaliza
    inexistente = huerta.obtener_hortaliza(999)
    assert inexistente is None


def test_annotation_system():
    """Test annotation system (RF-004)"""
    huerta = Huerta()
    
    # Create annotation
    anotacion = Anotacion(
        tipo=TipoAnotacion.EVENTO,
        nivel_especificidad=NivelEspecificidad.INDIVIDUO,
        fecha="2024-01-15",
        notas="Primera siembra de tomates",
        cultivo_id="cultivo_1"
    )
    
    # Add annotation
    anotacion_id = huerta.agregar_anotacion(anotacion)
    assert anotacion_id == "anotacion_1"
    assert len(huerta.anotaciones) == 1
    
    # Test getting annotations by cultivo
    anotaciones_cultivo = huerta.obtener_anotaciones_por_cultivo("cultivo_1")
    assert len(anotaciones_cultivo) == 1
    assert anotaciones_cultivo[0].notas == "Primera siembra de tomates"


def test_annotation_by_coordinates():
    """Test annotations by coordinates (RF-004)"""
    huerta = Huerta()
    
    # Create annotation with coordinates
    anotacion = Anotacion(
        tipo=TipoAnotacion.NOTA,
        nivel_especificidad=NivelEspecificidad.INDIVIDUO,
        fecha="2024-01-15",
        notas="Problema de plagas en esta zona",
        coordenadas=Coordenada(x=100, y=100)
    )
    
    huerta.agregar_anotacion(anotacion)
    
    # Test getting annotations by coordinates
    anotaciones_cercanas = huerta.obtener_anotaciones_por_coordenada(105, 105)
    assert len(anotaciones_cercanas) == 1
    
    # Test far coordinates
    anotaciones_lejanas = huerta.obtener_anotaciones_por_coordenada(200, 200)
    assert len(anotaciones_lejanas) == 0


def test_weather_service():
    """Test weather service (RF-006)"""
    weather_service = WeatherService()
    
    # Test getting 7-day forecast
    forecast = weather_service.obtener_pronostico_7_dias("Buenos Aires")
    assert forecast.ubicacion == "Buenos Aires"
    assert len(forecast.dias) == 7
    
    # Test first day has valid data
    primer_dia = forecast.dias[0]
    assert primer_dia.fecha is not None
    assert primer_dia.temperatura_max > primer_dia.temperatura_min
    assert 0 <= primer_dia.humedad <= 100
    
    # Test alerts
    alertas = weather_service.obtener_alertas_climaticas()
    assert isinstance(alertas, list)


def test_weather_cache():
    """Test weather service caching"""
    weather_service = WeatherService()
    
    # First call
    forecast1 = weather_service.obtener_pronostico_7_dias()
    timestamp1 = weather_service.cache_timestamp
    
    # Second call (should use cache)
    forecast2 = weather_service.obtener_pronostico_7_dias()
    timestamp2 = weather_service.cache_timestamp
    
    assert timestamp1 == timestamp2  # Cache was used
    assert forecast1.fecha_actualizacion == forecast2.fecha_actualizacion


def test_lunar_calendar():
    """Test lunar calendar (RF-007)"""
    calendar_service = CalendarService()
    
    # Test lunar phase calculation
    fecha = datetime(2024, 1, 15)
    info_lunar = calendar_service.obtener_fase_lunar(fecha)
    
    assert info_lunar.fecha == "2024-01-15"
    assert info_lunar.fase in ["nueva", "creciente", "llena", "menguante"]
    assert 0 <= info_lunar.iluminacion_porcentaje <= 100
    assert len(info_lunar.actividades_recomendadas) > 0


def test_weekly_calendar():
    """Test weekly calendar (RF-007)"""
    calendar_service = CalendarService()
    
    fecha_inicio = datetime(2024, 1, 15)
    calendario_semanal = calendar_service.obtener_calendario_semanal(fecha_inicio)
    
    assert len(calendario_semanal) == 7
    
    # Check first day
    primer_dia = calendario_semanal[0]
    assert primer_dia["fecha"] == "2024-01-15"
    assert "lunar" in primer_dia
    assert "eventos" in primer_dia


def test_planting_suggestions():
    """Test planting suggestions (RF-009)"""
    calendar_service = CalendarService()
    
    # Test suggestions for September (month 9)
    sugerencias = calendar_service.obtener_sugerencias_siembra(9)
    
    assert isinstance(sugerencias, list)
    
    # Should have suggestions for tomatoes (siembra_mes_inicio=9)
    sugerencias_tomate = [s for s in sugerencias if s["hortaliza"]["nombre"] == "Tomate"]
    assert len(sugerencias_tomate) > 0
    assert sugerencias_tomate[0]["recomendacion"] in ["Alta", "Baja"]


def test_calendar_events():
    """Test calendar event management"""
    calendar_service = CalendarService()
    
    from app.calendar import EventoCalendario
    
    # Create event
    evento = EventoCalendario(
        tipo="siembra",
        fecha="2024-01-15",
        descripcion="Siembra de tomates",
        completado=False
    )
    
    # Add event
    evento_id = calendar_service.agregar_evento(evento)
    assert evento_id == "evento_1"
    
    # Get events for date
    eventos_fecha = calendar_service.obtener_eventos_fecha("2024-01-15")
    assert len(eventos_fecha) == 1
    
    # Mark as completed
    success = calendar_service.marcar_evento_completado(evento_id)
    assert success is True
    assert eventos_fecha[0].completado is True


def test_map_loading_with_annotations():
    """Test map loading includes annotations"""
    huerta = Huerta()
    
    # Add annotation
    anotacion = Anotacion(
        tipo=TipoAnotacion.NOTA,
        nivel_especificidad=NivelEspecificidad.INDIVIDUO,
        fecha="2024-01-15",
        notas="Test annotation"
    )
    huerta.agregar_anotacion(anotacion)
    
    # Load map
    map_data = huerta.cargar_mapa()
    assert "anotaciones" in map_data
    assert len(map_data["anotaciones"]) == 1
    assert map_data["anotaciones"][0]["notas"] == "Test annotation"