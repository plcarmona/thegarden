"""
Calendar functionality module (RF-007, RF-008)
Provides lunar calendar and planting/harvest calendar
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import math
from pydantic import BaseModel
from enum import Enum

from .models import huerta_instance


class FaseLunar(str, Enum):
    """Fases lunares"""
    NUEVA = "nueva"
    CRECIENTE = "creciente"
    LLENA = "llena"
    MENGUANTE = "menguante"


class EventoCalendario(BaseModel):
    """Evento en el calendario de huerta"""
    id: Optional[str] = None
    tipo: str  # siembra, cosecha, riego, etc.
    cultivo_id: Optional[str] = None
    hortaliza_id: Optional[int] = None
    fecha: str
    descripcion: str
    completado: bool = False


class InfoLunar(BaseModel):
    """Información lunar para una fecha"""
    fecha: str
    fase: FaseLunar
    iluminacion_porcentaje: float
    recomendacion_siembra: str
    actividades_recomendadas: List[str]


class CalendarService:
    """Service for calendar functionality (RF-007, RF-008)"""
    
    def __init__(self):
        self.eventos: List[EventoCalendario] = []
    
    def obtener_fase_lunar(self, fecha: datetime) -> InfoLunar:
        """
        Calcular la fase lunar para una fecha específica (RF-007)
        Algoritmo simplificado basado en el ciclo lunar de ~29.5 días
        """
        
        # Fecha base conocida de luna nueva: 2024-01-11
        fecha_base_luna_nueva = datetime(2024, 1, 11)
        ciclo_lunar = 29.530588853  # días
        
        # Calcular días desde la fecha base
        diferencia_dias = (fecha - fecha_base_luna_nueva).total_seconds() / (24 * 3600)
        
        # Calcular posición en el ciclo lunar (0-1)
        posicion_ciclo = (diferencia_dias % ciclo_lunar) / ciclo_lunar
        
        # Determinar fase lunar
        if posicion_ciclo < 0.125:
            fase = FaseLunar.NUEVA
        elif posicion_ciclo < 0.375:
            fase = FaseLunar.CRECIENTE
        elif posicion_ciclo < 0.625:
            fase = FaseLunar.LLENA
        else:
            fase = FaseLunar.MENGUANTE
        
        # Calcular porcentaje de iluminación
        iluminacion = abs(math.cos(posicion_ciclo * 2 * math.pi)) * 100
        
        # Generar recomendaciones
        recomendaciones = self._generar_recomendaciones_lunares(fase)
        
        return InfoLunar(
            fecha=fecha.date().isoformat(),
            fase=fase,
            iluminacion_porcentaje=round(iluminacion, 1),
            recomendacion_siembra=recomendaciones["siembra"],
            actividades_recomendadas=recomendaciones["actividades"]
        )
    
    def _generar_recomendaciones_lunares(self, fase: FaseLunar) -> Dict[str, Any]:
        """Generar recomendaciones según la fase lunar"""
        recomendaciones = {
            FaseLunar.NUEVA: {
                "siembra": "Ideal para sembrar plantas que crecen bajo tierra (raíces, tubérculos)",
                "actividades": [
                    "Sembrar zanahorias, remolachas, papas",
                    "Podar plantas",
                    "Preparar tierra nueva"
                ]
            },
            FaseLunar.CRECIENTE: {
                "siembra": "Excelente para sembrar plantas de hoja y fruto",
                "actividades": [
                    "Sembrar lechugas, espinacas, tomates",
                    "Transplantar",
                    "Fertilizar"
                ]
            },
            FaseLunar.LLENA: {
                "siembra": "Favorable para plantas de crecimiento rápido",
                "actividades": [
                    "Sembrar plantas de hoja verde",
                    "Cosechar frutas y hierbas",
                    "Regar abundantemente"
                ]
            },
            FaseLunar.MENGUANTE: {
                "siembra": "Momento para plantas perennes y de raíz",
                "actividades": [
                    "Podar y dar forma a plantas",
                    "Cosechar para almacenamiento",
                    "Controlar plagas"
                ]
            }
        }
        
        return recomendaciones[fase]
    
    def obtener_calendario_semanal(self, fecha_inicio: datetime) -> List[Dict[str, Any]]:
        """Obtener calendario lunar para una semana (RF-007)"""
        calendario = []
        
        for i in range(7):
            fecha_dia = fecha_inicio + timedelta(days=i)
            info_lunar = self.obtener_fase_lunar(fecha_dia)
            
            # Obtener eventos del día
            eventos_dia = self.obtener_eventos_fecha(fecha_dia.date().isoformat())
            
            calendario.append({
                "fecha": fecha_dia.date().isoformat(),
                "dia_semana": fecha_dia.strftime("%A"),
                "lunar": info_lunar.model_dump(),
                "eventos": [e.model_dump() for e in eventos_dia]
            })
        
        return calendario
    
    def generar_calendario_siembra_cosecha(self) -> List[EventoCalendario]:
        """
        Generar calendario de siembra y cosecha automático (RF-008)
        Basado en los cultivos activos y la información de hortalizas
        """
        eventos = []
        
        for cultivo in huerta_instance.cultivos_activos:
            hortaliza = huerta_instance.obtener_hortaliza(cultivo.hortaliza_id)
            if not hortaliza:
                continue
            
            # Fecha de siembra (ya ocurrió)
            evento_siembra = EventoCalendario(
                id=f"siembra_{cultivo.id}",
                tipo="siembra",
                cultivo_id=cultivo.id,
                hortaliza_id=cultivo.hortaliza_id,
                fecha=cultivo.fecha_siembra,
                descripcion=f"Siembra de {hortaliza.nombre}",
                completado=True
            )
            eventos.append(evento_siembra)
            
            # Calcular fecha de cosecha
            fecha_siembra = datetime.fromisoformat(cultivo.fecha_siembra)
            fecha_cosecha = fecha_siembra + timedelta(days=hortaliza.ciclo_dias)
            
            evento_cosecha = EventoCalendario(
                id=f"cosecha_{cultivo.id}",
                tipo="cosecha",
                cultivo_id=cultivo.id,
                hortaliza_id=cultivo.hortaliza_id,
                fecha=fecha_cosecha.date().isoformat(),
                descripcion=f"Cosecha de {hortaliza.nombre}",
                completado=False
            )
            eventos.append(evento_cosecha)
            
            # Eventos de cuidado (riego, fertilización)
            self._generar_eventos_cuidado(cultivo, hortaliza, eventos)
        
        return eventos
    
    def _generar_eventos_cuidado(self, cultivo, hortaliza, eventos: List[EventoCalendario]):
        """Generar eventos de cuidado para un cultivo"""
        fecha_siembra = datetime.fromisoformat(cultivo.fecha_siembra)
        
        # Evento de fertilización (a los 30 días)
        fecha_fertilizacion = fecha_siembra + timedelta(days=30)
        if fecha_fertilizacion > datetime.now():
            evento_fertilizacion = EventoCalendario(
                id=f"fertilizacion_{cultivo.id}",
                tipo="fertilizacion",
                cultivo_id=cultivo.id,
                hortaliza_id=cultivo.hortaliza_id,
                fecha=fecha_fertilizacion.date().isoformat(),
                descripcion=f"Fertilización de {hortaliza.nombre}",
                completado=False
            )
            eventos.append(evento_fertilizacion)
        
        # Eventos de riego (cada 3 días desde la siembra)
        fecha_riego = fecha_siembra
        while fecha_riego < fecha_siembra + timedelta(days=hortaliza.ciclo_dias):
            if fecha_riego > datetime.now() and fecha_riego < datetime.now() + timedelta(days=14):
                evento_riego = EventoCalendario(
                    id=f"riego_{cultivo.id}_{fecha_riego.strftime('%Y%m%d')}",
                    tipo="riego",
                    cultivo_id=cultivo.id,
                    hortaliza_id=cultivo.hortaliza_id,
                    fecha=fecha_riego.date().isoformat(),
                    descripcion=f"Riego de {hortaliza.nombre}",
                    completado=False
                )
                eventos.append(evento_riego)
            fecha_riego += timedelta(days=3)
    
    def obtener_eventos_fecha(self, fecha: str) -> List[EventoCalendario]:
        """Obtener eventos para una fecha específica"""
        return [e for e in self.eventos if e.fecha == fecha]
    
    def agregar_evento(self, evento: EventoCalendario) -> str:
        """Agregar un evento personalizado al calendario"""
        if not evento.id:
            evento.id = f"evento_{len(self.eventos) + 1}"
        
        self.eventos.append(evento)
        return evento.id
    
    def marcar_evento_completado(self, evento_id: str) -> bool:
        """Marcar un evento como completado"""
        for evento in self.eventos:
            if evento.id == evento_id:
                evento.completado = True
                return True
        return False
    
    def obtener_sugerencias_siembra(self, mes_actual: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtener sugerencias de siembra para el mes actual (RF-009)
        """
        if mes_actual is None:
            mes_actual = datetime.now().month
        
        sugerencias = []
        
        for hortaliza in huerta_instance.listar_hortalizas():
            # Verificar si es temporada de siembra
            es_temporada = False
            
            if hortaliza.siembra_mes_inicio <= hortaliza.siembra_mes_fin:
                # Temporada normal (ej: marzo a septiembre)
                es_temporada = hortaliza.siembra_mes_inicio <= mes_actual <= hortaliza.siembra_mes_fin
            else:
                # Temporada que cruza año (ej: octubre a febrero)
                es_temporada = mes_actual >= hortaliza.siembra_mes_inicio or mes_actual <= hortaliza.siembra_mes_fin
            
            if es_temporada:
                # Verificar espacio disponible (simplificado)
                espacio_usado = sum(h.tamano_promedio for h in huerta_instance.listar_hortalizas() 
                                  if any(c.hortaliza_id == h.id for c in huerta_instance.cultivos_activos))
                espacio_total = 20  # metros cuadrados estimados
                espacio_disponible = espacio_total - espacio_usado > hortaliza.tamano_promedio
                
                sugerencia = {
                    "hortaliza": hortaliza.model_dump(),
                    "recomendacion": "Alta" if espacio_disponible else "Baja",
                    "razon": "Temporada ideal y espacio disponible" if espacio_disponible 
                            else "Temporada ideal pero espacio limitado",
                    "dias_hasta_cosecha": hortaliza.ciclo_dias
                }
                sugerencias.append(sugerencia)
        
        return sorted(sugerencias, key=lambda x: x["recomendacion"], reverse=True)


# Global calendar service instance
calendar_service = CalendarService()