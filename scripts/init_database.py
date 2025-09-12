#!/usr/bin/env python3
"""
Script para inicializar base de datos KuzuDB
Uso: python scripts/init_database.py
"""
import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.kuzu_manager import kuzu_manager


def main():
    print("🌱 Inicializando base de datos KuzuDB para The Garden...")
    
    try:
        # Conectar
        conn = kuzu_manager.connect()
        if not conn:
            print("⚠️ KuzuDB no está disponible. Verifique que esté instalado:")
            print("   pip install kuzu")
            return 1
            
        print("✓ Conexión establecida")
        
        # Inicializar schema
        print("📋 Creando schema...")
        kuzu_manager.initialize_schema()
        print("✓ Schema creado")
        
        # Cargar datos iniciales
        print("📦 Cargando datos iniciales...")
        kuzu_manager.load_initial_data()
        print("✓ Datos iniciales cargados")
        
        # Verificar que la base de datos funciona
        print("🔍 Verificando funcionamiento...")
        try:
            result = kuzu_manager.execute_query("MATCH (h:Hortaliza) RETURN count(h) as total")
            if result and result.has_next():
                row = result.get_next()
                count = row[0]
                print(f"✓ Base de datos funcionando - {count} hortalizas encontradas")
            else:
                print("⚠️ No se encontraron datos, pero la conexión funciona")
        except Exception as e:
            print(f"⚠️ Error verificando datos: {e}")
        
        print("\n🎉 ¡Base de datos KuzuDB inicializada correctamente!")
        print(f"   📍 Ubicación: {kuzu_manager.db_path}")
        print("   🚀 El sistema puede usar consultas de grafos ahora")
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        print("\n🔧 Pasos para solucionar:")
        print("   1. Instalar KuzuDB: pip install kuzu")
        print("   2. Verificar permisos de escritura en directorio database/")
        print("   3. Revisar archivos de schema y seeds en database/")
        return 1
    
    finally:
        kuzu_manager.close()
    
    return 0


if __name__ == "__main__":
    exit(main())