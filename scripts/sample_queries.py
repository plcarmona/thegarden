#!/usr/bin/env python3
"""
Ejemplos de consultas KuzuDB para The Garden
Demuestra las capacidades analíticas del sistema de grafos
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.kuzu_manager import kuzu_manager


def query_plantas_por_tipo():
    """Consultar todas las plantas de un tipo específico"""
    print("\n📊 Plantas por tipo (Tomate):")
    query = """
    MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza {nombre: "Tomate"})
    RETURN p.id, p.coordenadas_x, p.coordenadas_y, p.estado, p.fecha_siembra
    ORDER BY p.fecha_siembra
    """
    
    result = kuzu_manager.execute_query(query)
    if result:
        count = 0
        while result.has_next():
            count += 1
            row = result.get_next()
            print(f"  🍅 {row[0]} - Pos:({row[1]}, {row[2]}) - Estado:{row[3]} - Sembrada:{row[4]}")
        
        if count == 0:
            print("  📝 No hay plantas de tomate registradas")
    return result


def query_anotaciones_por_temporada():
    """Consultar anotaciones por temporada"""
    print("\n📝 Anotaciones de verano:")
    query = """
    MATCH (a:Anotaciones {temporada: "verano"})
    RETURN a.tipo, a.notas, a.fecha, a.nivel_especificidad
    ORDER BY a.fecha
    """
    
    result = kuzu_manager.execute_query(query)
    if result:
        count = 0
        while result.has_next():
            count += 1
            row = result.get_next()
            print(f"  📋 {row[0]} ({row[3]}) - {row[2]} - {row[1][:50]}...")
        
        if count == 0:
            print("  📝 No hay anotaciones de verano registradas")
    return result


def query_plantas_cercanas(x: float, y: float, radius: float = 50.0):
    """Encontrar plantas cerca de una coordenada"""
    print(f"\n🎯 Plantas cerca de ({x}, {y}) en radio {radius}:")
    
    plantas = kuzu_manager.query_plantas_by_coordinates(x, y, radius)
    
    if plantas:
        for planta in plantas:
            print(f"  🌱 {planta['hortaliza_nombre']} - ID:{planta['id']} - "
                  f"Distancia:{planta['distancia']:.1f} - Estado:{planta['estado']}")
    else:
        print("  📍 No hay plantas en el área especificada")
    
    return plantas


def query_historial_cultivo(planta_id: str = "tomate_001"):
    """Consultar historial completo de un cultivo"""
    print(f"\n📚 Historial del cultivo {planta_id}:")
    query = """
    MATCH (p:Planta {id: $planta_id})-[:IS_OF_TYPE]->(h:Hortaliza)
    OPTIONAL MATCH (a:Anotaciones)-[:ANNOTATES_PLANTA]->(p)
    RETURN p.fecha_siembra, p.estado, p.coordenadas_x, p.coordenadas_y,
           h.nombre, h.descripcion,
           a.tipo, a.fecha, a.notas
    ORDER BY a.fecha
    """
    
    result = kuzu_manager.execute_query(query, {"planta_id": planta_id})
    if result:
        cultivo_info = None
        anotaciones = []
        
        while result.has_next():
            row = result.get_next()
            if cultivo_info is None:
                cultivo_info = {
                    "fecha_siembra": row[0],
                    "estado": row[1], 
                    "posicion": (row[2], row[3]),
                    "tipo": row[4],
                    "descripcion": row[5]
                }
            
            if row[6]:  # Si hay anotación
                anotaciones.append({
                    "tipo": row[6],
                    "fecha": row[7],
                    "notas": row[8]
                })
        
        if cultivo_info:
            print(f"  🌱 Tipo: {cultivo_info['tipo']}")
            print(f"  📅 Fecha siembra: {cultivo_info['fecha_siembra']}")
            print(f"  📍 Posición: {cultivo_info['posicion']}")
            print(f"  🔄 Estado: {cultivo_info['estado']}")
            print(f"  📝 Anotaciones: {len(anotaciones)}")
            
            for i, anotacion in enumerate(anotaciones):
                print(f"    {i+1}. {anotacion['tipo']} ({anotacion['fecha']}) - {anotacion['notas']}")
        else:
            print(f"  ❌ Cultivo {planta_id} no encontrado")
    
    return result


def query_estadisticas_generales():
    """Estadísticas generales del jardín"""
    print("\n📈 Estadísticas generales:")
    
    queries = [
        ("Total hortalizas", "MATCH (h:Hortaliza) RETURN count(h)"),
        ("Total plantas activas", "MATCH (p:Planta {estado: 'activo'}) RETURN count(p)"),
        ("Total anotaciones", "MATCH (a:Anotaciones) RETURN count(a)"),
        ("Huertas configuradas", "MATCH (hu:Huerta) RETURN count(hu)")
    ]
    
    for nombre, query in queries:
        try:
            result = kuzu_manager.execute_query(query)
            if result and result.has_next():
                count = result.get_next()[0]
                print(f"  📊 {nombre}: {count}")
            else:
                print(f"  📊 {nombre}: 0")
        except Exception as e:
            print(f"  ❌ Error consultando {nombre}: {e}")


def query_analisis_densidad():
    """Análisis de densidad de cultivos"""
    print("\n🗺️ Análisis de densidad por área (cuadrículas de 100x100):")
    query = """
    MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
    WITH toInteger(p.coordenadas_x / 100) * 100 as grid_x, 
         toInteger(p.coordenadas_y / 100) * 100 as grid_y, 
         count(p) as plantas_por_celda,
         collect(h.nombre) as tipos
    WHERE plantas_por_celda > 0
    RETURN grid_x, grid_y, plantas_por_celda, tipos
    ORDER BY plantas_por_celda DESC
    """
    
    try:
        result = kuzu_manager.execute_query(query)
        if result:
            while result.has_next():
                row = result.get_next()
                print(f"  📍 Área ({row[0]}-{row[0]+100}, {row[1]}-{row[1]+100}): "
                      f"{row[2]} plantas - Tipos: {row[3]}")
        else:
            print("  📊 No hay datos de densidad disponibles")
    except Exception as e:
        print(f"  ❌ Error en análisis de densidad: {e}")


def main():
    print("🔍 Ejecutando consultas de ejemplo en KuzuDB...")
    
    try:
        # Conectar
        if not kuzu_manager.connect():
            print("❌ No se puede conectar a KuzuDB. Ejecute primero:")
            print("   python scripts/init_database.py")
            return 1
        
        # Ejecutar consultas de ejemplo
        query_estadisticas_generales()
        query_plantas_por_tipo()
        query_plantas_cercanas(150, 100)
        query_anotaciones_por_temporada()
        query_historial_cultivo()
        query_analisis_densidad()
        
        print("\n✅ Consultas completadas exitosamente")
        print("\n💡 Estas consultas demuestran las capacidades analíticas de KuzuDB:")
        print("   - Consultas por coordenadas geoespaciales")
        print("   - Análisis de relaciones entre plantas y tipos") 
        print("   - Historial temporal de cultivos")
        print("   - Análisis de densidad espacial")
        print("   - Filtros por diferentes niveles de especificidad")
        
    except Exception as e:
        print(f"❌ Error ejecutando consultas: {e}")
        return 1
    
    finally:
        kuzu_manager.close()
    
    return 0


if __name__ == "__main__":
    exit(main())