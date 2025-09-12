"""
Weather API integration module (RF-006)
Provides 7-day weather forecast functionality
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from pydantic import BaseModel


class WeatherDay(BaseModel):
    """Represents weather for a single day"""
    fecha: str
    temperatura_max: float
    temperatura_min: float
    humedad: int
    viento_velocidad: float
    precipitacion: float
    descripcion: str
    icono: str


class WeatherForecast(BaseModel):
    """7-day weather forecast"""
    ubicacion: str
    fecha_actualizacion: str
    dias: List[WeatherDay]


class WeatherService:
    """Service for weather data management (RF-006)"""
    
    def __init__(self):
        self.cache: Optional[WeatherForecast] = None
        self.cache_timestamp: Optional[datetime] = None
        self.cache_duration_hours = 3  # Cache data for 3 hours
    
    def obtener_pronostico_7_dias(self, ubicacion: str = "Buenos Aires") -> WeatherForecast:
        """
        Obtener pronóstico de 7 días (RF-006)
        En una implementación real, esto llamaría a una API externa como OpenWeatherMap
        """
        
        # Check cache first
        if self._is_cache_valid():
            return self.cache
        
        # Generate mock weather data for demonstration
        # In a real implementation, this would call an external API
        forecast = self._generate_mock_weather(ubicacion)
        
        # Update cache
        self.cache = forecast
        self.cache_timestamp = datetime.now()
        
        return forecast
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self.cache or not self.cache_timestamp:
            return False
        
        return (datetime.now() - self.cache_timestamp).total_seconds() < (self.cache_duration_hours * 3600)
    
    def _generate_mock_weather(self, ubicacion: str) -> WeatherForecast:
        """
        Generate mock weather data
        In a real implementation, this would be replaced with actual API calls
        """
        base_temp = 22  # Base temperature in Celsius
        dias = []
        
        weather_conditions = [
            {"desc": "Soleado", "icon": "☀️"},
            {"desc": "Parcialmente nublado", "icon": "⛅"},
            {"desc": "Nublado", "icon": "☁️"},
            {"desc": "Lluvia ligera", "icon": "🌦️"},
            {"desc": "Lluvia", "icon": "🌧️"},
        ]
        
        for i in range(7):
            fecha = (datetime.now() + timedelta(days=i)).date().isoformat()
            
            # Simulate temperature variation
            temp_variation = (i % 3) * 2 - 2  # -2, 0, 2, 0, -2, 0, 2
            temp_max = base_temp + temp_variation + 5
            temp_min = base_temp + temp_variation - 3
            
            # Simulate weather conditions
            condition = weather_conditions[i % len(weather_conditions)]
            
            # Simulate precipitation (higher chance on certain days)
            precipitacion = 0.0
            if "lluvia" in condition["desc"].lower():
                precipitacion = 5.0 + (i * 2)  # mm
            
            day = WeatherDay(
                fecha=fecha,
                temperatura_max=temp_max,
                temperatura_min=temp_min,
                humedad=60 + (i * 5),  # 60-90%
                viento_velocidad=10 + (i * 2),  # km/h
                precipitacion=precipitacion,
                descripcion=condition["desc"],
                icono=condition["icon"]
            )
            
            dias.append(day)
        
        return WeatherForecast(
            ubicacion=ubicacion,
            fecha_actualizacion=datetime.now().isoformat(),
            dias=dias
        )
    
    def obtener_alertas_climaticas(self) -> List[Dict[str, Any]]:
        """
        Obtener alertas climáticas importantes para la huerta
        Detecta condiciones como heladas, lluvia intensa, etc.
        """
        forecast = self.obtener_pronostico_7_dias()
        alertas = []
        
        for day in forecast.dias:
            # Alerta por helada
            if day.temperatura_min <= 2:
                alertas.append({
                    "tipo": "helada",
                    "fecha": day.fecha,
                    "severidad": "alta",
                    "mensaje": f"Riesgo de helada: {day.temperatura_min}°C",
                    "recomendacion": "Proteger cultivos sensibles al frío"
                })
            
            # Alerta por lluvia intensa
            if day.precipitacion > 15:
                alertas.append({
                    "tipo": "lluvia_intensa",
                    "fecha": day.fecha,
                    "severidad": "media",
                    "mensaje": f"Lluvia intensa esperada: {day.precipitacion}mm",
                    "recomendacion": "Verificar drenaje y proteger cultivos delicados"
                })
            
            # Alerta por calor extremo
            if day.temperatura_max > 35:
                alertas.append({
                    "tipo": "calor_extremo",
                    "fecha": day.fecha,
                    "severidad": "media",
                    "mensaje": f"Temperatura muy alta: {day.temperatura_max}°C",
                    "recomendacion": "Aumentar frecuencia de riego y proporcionar sombra"
                })
        
        return alertas


# Global weather service instance
weather_service = WeatherService()