#!/usr/bin/env python3
"""
Demo script for The Garden GUI
Demonstrates core functionality without requiring a running server
"""

from database.kuzu_manager import kuzu_manager
from database.toml_loader import toml_loader
from datetime import datetime
import os
import shutil

def demo_gui_functionality():
    """Demonstrate GUI functionality through code"""
    print("🌱 The Garden GUI - Functionality Demo")
    print("=" * 50)
    
    # Clean up any existing database
    if os.path.exists("database/garden.kuzu"):
        if os.path.isfile("database/garden.kuzu"):
            os.remove("database/garden.kuzu")
        else:
            shutil.rmtree("database/garden.kuzu")
    
    print("\n1. 🔗 Database Initialization Demo")
    print("-" * 30)
    try:
        # Connect to database
        conn = kuzu_manager.connect()
        if conn:
            print("   ✅ Connected to KuzuDB successfully")
            
            # Initialize schema
            schema_success = kuzu_manager.initialize_schema()
            if schema_success:
                print("   ✅ Database schema initialized")
                
                # Load initial data
                kuzu_manager.load_initial_data()
                print("   ✅ Initial data loaded")
            else:
                print("   ❌ Schema initialization failed")
                return False
        else:
            print("   ❌ Failed to connect to KuzuDB")
            return False
            
    except Exception as e:
        print(f"   ❌ Database initialization error: {e}")
        return False
    
    print("\n2. 🌿 View Current Plants Demo")
    print("-" * 30)
    try:
        # Query existing plants
        result = kuzu_manager.execute_query("""
            MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
            RETURN p.id, h.nombre, p.coordenadas_x, p.coordenadas_y, p.fecha_siembra
            ORDER BY p.id
        """)
        
        plants = []
        if result and result.has_next():
            while result.has_next():
                row = result.get_next()
                plants.append({
                    'id': row[0],
                    'type': row[1], 
                    'x': row[2],
                    'y': row[3],
                    'date': row[4]
                })
        
        print(f"   📊 Found {len(plants)} existing plants:")
        for plant in plants:
            print(f"      • {plant['type']} ({plant['id']}) at ({plant['x']}, {plant['y']})")
            
    except Exception as e:
        print(f"   ❌ Error querying plants: {e}")
        return False
    
    print("\n3. ➕ Add New Plant Demo")
    print("-" * 30)
    try:
        # Get available plant types
        hortalizas = toml_loader.get_hortalizas()
        print(f"   📋 Available plant types: {len(hortalizas)}")
        
        # Simulate adding a new plant
        plant_type_id = 1  # Tomate
        x_coord = 150.0
        y_coord = 250.0
        plant_id = f"tomate_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Check coordinate usability
        intersecting = kuzu_manager.check_coordinate_in_structure(x_coord, y_coord)
        if intersecting:
            print(f"   ⚠️  Coordinates ({x_coord}, {y_coord}) intersect with structures:")
            for s in intersecting:
                print(f"      - {s['nombre']} ({s['tipo']})")
        else:
            print(f"   ✅ Coordinates ({x_coord}, {y_coord}) are usable")
        
        # Create the plant
        create_plant_query = """
        CREATE (p:Planta {
            id: $id,
            fecha_siembra: $fecha_siembra,
            coordenadas_x: $coordenadas_x,
            coordenadas_y: $coordenadas_y
        })
        """
        
        kuzu_manager.execute_query(create_plant_query, {
            'id': plant_id,
            'fecha_siembra': datetime.now().date(),
            'coordenadas_x': x_coord,
            'coordenadas_y': y_coord
        })
        
        # Create relationship
        relate_query = """
        MATCH (p:Planta {id: $planta_id}), (h:Hortaliza {id: $hortaliza_id})
        CREATE (p)-[:IS_OF_TYPE {fecha_relacion: $fecha}]->(h)
        """
        
        kuzu_manager.execute_query(relate_query, {
            'planta_id': plant_id,
            'hortaliza_id': plant_type_id,
            'fecha': datetime.now()
        })
        
        print(f"   ✅ Added new plant: {plant_id}")
        
    except Exception as e:
        print(f"   ❌ Error adding plant: {e}")
        return False
    
    print("\n4. 🗑️  Remove Plant Demo")
    print("-" * 30)
    try:
        # Remove the plant we just added
        remove_query = """
        MATCH (p:Planta {id: $plant_id})
        DETACH DELETE p
        """
        
        kuzu_manager.execute_query(remove_query, {'plant_id': plant_id})
        print(f"   ✅ Removed plant: {plant_id}")
        
    except Exception as e:
        print(f"   ❌ Error removing plant: {e}")
        return False
    
    print("\n5. 📊 Garden Statistics Demo")
    print("-" * 30)
    try:
        # Get statistics
        queries = [
            ("Plants", "MATCH (p:Planta) RETURN count(p)"),
            ("Plant Types", "MATCH (h:Hortaliza) RETURN count(h)"),
            ("Structures", "MATCH (e:Estructura) RETURN count(e)"),
            ("Gardens", "MATCH (hu:Huerta) RETURN count(hu)"),
        ]
        
        for name, query in queries:
            result = kuzu_manager.execute_query(query)
            if result and result.has_next():
                count = result.get_next()[0]
                print(f"   📈 {name}: {count}")
        
        # Show structures
        estructuras = kuzu_manager.query_all_estructuras()
        print(f"   🏗️  Garden structures: {len(estructuras)}")
        for e in estructuras:
            vertices = len(e['poligono']) if e['poligono'] else 0
            print(f"      • {e['nombre']} ({e['tipo']}) - {vertices} vertices")
            
    except Exception as e:
        print(f"   ❌ Error getting statistics: {e}")
        return False
    
    finally:
        kuzu_manager.close()
    
    print("\n" + "=" * 50)
    print("🎉 Demo Complete!")
    print("\n📝 Summary:")
    print("   ✅ Database initialization: Working")
    print("   ✅ Plant viewing: Working") 
    print("   ✅ Plant addition: Working")
    print("   ✅ Plant removal: Working")
    print("   ✅ Coordinate validation: Working")
    print("   ✅ Statistics: Working")
    
    print("\n🌐 Web GUI Features:")
    print("   • Modern responsive web interface")
    print("   • Real-time plant management")
    print("   • Coordinate validation with visual feedback")
    print("   • Garden statistics dashboard")
    print("   • Plant type selection from TOML config")
    print("   • Database connection status monitoring")
    
    return True


if __name__ == "__main__":
    success = demo_gui_functionality()
    print(f"\n{'✅ Demo successful!' if success else '❌ Demo failed!'}")