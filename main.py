#!/usr/bin/env python3
"""
The Garden - Database Interaction Tool
Simple command-line interface to interact with the KuzuDB graph database
"""

import sys
import os
from database.kuzu_manager import kuzu_manager


def print_banner():
    """Print application banner"""
    print("🌱 The Garden - Database Tool")
    print("=" * 40)


def initialize_database():
    """Initialize the database with schema and initial data"""
    print("📋 Initializing KuzuDB database...")
    
    # Remove old database
    import shutil
    if os.path.exists("database/garden.kuzu"):
        if os.path.isfile("database/garden.kuzu"):
            os.remove("database/garden.kuzu")
        else:
            shutil.rmtree("database/garden.kuzu")
    
    # Connect to database
    conn = kuzu_manager.connect()
    if not conn:
        print("❌ Could not connect to KuzuDB. Make sure it's installed:")
        print("   pip install kuzu")
        return False
    
    try:
        print("🔧 Creating database schema...")
        
        # Use the formal schema files
        kuzu_manager.initialize_schema()
        
        print("📦 Loading initial data...")
        
        # Use the formal initial data
        kuzu_manager.load_initial_data()
        
        print("✅ Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
    finally:
        kuzu_manager.close()


def query_database():
    """Interactive query interface"""
    print("🔍 Enter your Cypher queries (type 'exit' to return to main menu):")
    print("Examples:")
    print("  MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza) RETURN h.nombre, p.id LIMIT 5")
    print("  MATCH (p:Planta) RETURN count(p)")
    print("  MATCH (hu:Huerta) RETURN hu.nombre, hu.ancho, hu.alto")
    print()
    
    conn = kuzu_manager.connect()
    if not conn:
        print("❌ Could not connect to database")
        return
    
    try:
        while True:
            query = input("KuzuDB> ").strip()
            
            if query.lower() in ['exit', 'quit']:
                break
                
            if not query:
                continue
            
            try:
                result = kuzu_manager.execute_query(query)
                
                if result and result.has_next():
                    print("Results:")
                    count = 0
                    while result.has_next() and count < 20:  # Limit results for readability
                        row = result.get_next()
                        print(f"  {row}")
                        count += 1
                    
                    if result.has_next():
                        print("  ... (more results available)")
                else:
                    print("Query executed successfully (no results to display)")
                    
            except Exception as e:
                print(f"❌ Query error: {e}")
            
            print()  # Empty line for readability
            
    except KeyboardInterrupt:
        print("\n👋 Exiting query mode...")
    finally:
        kuzu_manager.close()


def search_by_coordinates():
    """Search plants by coordinates"""
    try:
        x = float(input("Enter X coordinate: "))
        y = float(input("Enter Y coordinate: "))
        radius = input("Enter search radius (default 50): ").strip()
        radius = float(radius) if radius else 50.0
        
        print(f"\n🔍 Searching plants near ({x}, {y}) with radius {radius}...")
        
        conn = kuzu_manager.connect()
        if not conn:
            print("❌ Could not connect to database")
            return
        
        try:
            # Use the new Spanish schema table names
            query = """
            MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
            WHERE sqrt(pow(p.coordenadas_x - $x, 2) + pow(p.coordenadas_y - $y, 2)) <= $radius
            RETURN p.id, h.nombre, p.coordenadas_x, p.coordenadas_y, 
                   sqrt(pow(p.coordenadas_x - $x, 2) + pow(p.coordenadas_y - $y, 2)) as distance
            ORDER BY distance
            """
            
            result = kuzu_manager.execute_query(query, {"x": x, "y": y, "radius": radius})
            
            plants = []
            if result and result.has_next():
                while result.has_next():
                    row = result.get_next()
                    plants.append({
                        'id': row[0],
                        'hortaliza_name': row[1],
                        'x': row[2],
                        'y': row[3],
                        'distance': row[4]
                    })
            
            if plants:
                print(f"\n✅ Found {len(plants)} plants:")
                for plant in plants:
                    print(f"  📍 {plant['hortaliza_name']} ({plant['id']})")
                    print(f"     Position: ({plant['x']}, {plant['y']})")
                    print(f"     Distance: {plant['distance']:.1f} units")
                    print()
            else:
                print("🔍 No plants found in the specified area")
                
        finally:
            kuzu_manager.close()
            
    except ValueError:
        print("❌ Invalid coordinate values. Please enter numbers.")
    except Exception as e:
        print(f"❌ Error searching: {e}")


def show_structures():
    """Show all garden structures and unusable areas"""
    print("🏗️ Garden Structures and Unusable Areas:")
    
    conn = kuzu_manager.connect()
    if not conn:
        print("❌ Could not connect to database")
        return
    
    try:
        estructuras = kuzu_manager.query_all_estructuras()
        
        if estructuras:
            print(f"\n✅ Found {len(estructuras)} structures:")
            for estructura in estructuras:
                print(f"\n  🏗️ {estructura['nombre']} ({estructura['id']})")
                print(f"     Type: {estructura['tipo']}")
                print(f"     Description: {estructura['descripcion']}")
                print(f"     Polygon: {len(estructura['poligono'])} vertices")
                # Show first few vertices
                vertices_str = ", ".join([f"({v[0]:.1f}, {v[1]:.1f})" for v in estructura['poligono'][:3]])
                if len(estructura['poligono']) > 3:
                    vertices_str += ", ..."
                print(f"     Vertices: {vertices_str}")
                print(f"     Created: {estructura['fecha_creacion']}")
        else:
            print("🔍 No structures found in database")
            
    except Exception as e:
        print(f"❌ Error listing structures: {e}")
    finally:
        kuzu_manager.close()


def check_coordinate_usability():
    """Check if coordinates are in an unusable area"""
    try:
        x = float(input("Enter X coordinate: "))
        y = float(input("Enter Y coordinate: "))
        
        print(f"\n🔍 Checking if coordinates ({x}, {y}) are usable for planting...")
        
        conn = kuzu_manager.connect()
        if not conn:
            print("❌ Could not connect to database")
            return
        
        try:
            intersecting = kuzu_manager.check_coordinate_in_structure(x, y)
            
            if intersecting:
                print(f"❌ Coordinates ({x}, {y}) are NOT usable for planting!")
                print(f"   Intersects with {len(intersecting)} structure(s):")
                for estructura in intersecting:
                    print(f"   - {estructura['nombre']} ({estructura['tipo']})")
                    print(f"     {estructura['descripcion']}")
            else:
                print(f"✅ Coordinates ({x}, {y}) are USABLE for planting!")
                print("   No structures blocking this area.")
                
        finally:
            kuzu_manager.close()
            
    except ValueError:
        print("❌ Invalid coordinate values. Please enter numbers.")
    except Exception as e:
        print(f"❌ Error checking coordinates: {e}")


def reload_toml_config():
    """Reload TOML configuration and reinitialize database"""
    print("🔄 Reloading TOML configuration...")
    
    try:
        from database.toml_loader import toml_loader
        toml_loader.reload()
        
        if toml_loader.validate_config():
            print("✅ TOML configuration reloaded successfully")
            
            choice = input("Do you want to reinitialize the database with new config? (y/n): ").lower()
            if choice == 'y':
                initialize_database()
        else:
            print("❌ TOML configuration validation failed")
            
    except Exception as e:
        print(f"❌ Error reloading TOML config: {e}")


def show_database_info():
    """Show database information and statistics"""
    print("📊 Database Information:")
    print(f"   📍 Location: {kuzu_manager.db_path}")
    print(f"   🔗 Available: {kuzu_manager._kuzu_available}")
    
    if not kuzu_manager._kuzu_available:
        print("   ⚠️ KuzuDB not available")
        return
    
    conn = kuzu_manager.connect()
    if not conn:
        print("❌ Could not connect to database")
        return
    
    try:
        # Get basic statistics
        print("\n📈 Statistics:")
        
        queries = [
            ("Total Plants", "MATCH (p:Planta) RETURN count(p)"),
            ("Total Gardens", "MATCH (hu:Huerta) RETURN count(hu)"),
            ("Total Vegetable Types", "MATCH (h:Hortaliza) RETURN count(h)"),
            ("Total Annotations", "MATCH (a:Anotation) RETURN count(a)"),
            ("Total Structures", "MATCH (e:Estructura) RETURN count(e)"),
        ]
        
        for name, query in queries:
            try:
                result = kuzu_manager.execute_query(query)
                if result and result.has_next():
                    count = result.get_next()[0]
                    print(f"   {name}: {count}")
                else:
                    print(f"   {name}: 0")
            except Exception as e:
                print(f"   {name}: Error ({e})")
        
        # List all plants with their vegetable types
        print("\n🌱 Plants in database:")
        try:
            result = kuzu_manager.execute_query("""
                MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
                RETURN p.id, h.nombre, p.coordenadas_x, p.coordenadas_y, p.fecha_siembra
            """)
            if result and result.has_next():
                while result.has_next():
                    row = result.get_next()
                    fecha_siembra = row[4] if row[4] else "No date"
                    print(f"   - {row[1]} ({row[0]}) at ({row[2]}, {row[3]}) planted: {fecha_siembra}")
            else:
                print("   No plants found")
        except Exception as e:
            print(f"   Error listing plants: {e}")
            
        # List all structures  
        print("\n🏗️ Structures in database:")
        try:
            estructuras = kuzu_manager.query_all_estructuras()
            if estructuras:
                for estructura in estructuras:
                    vertices_count = len(estructura['poligono']) if estructura['poligono'] else 0
                    print(f"   - {estructura['nombre']} ({estructura['tipo']}) - {vertices_count} vertices")
            else:
                print("   No structures found")
        except Exception as e:
            print(f"   Error listing structures: {e}")
        
    except Exception as e:
        print(f"❌ Error getting database info: {e}")
    finally:
        kuzu_manager.close()


def main():
    """Main application loop"""
    print_banner()
    
    if not kuzu_manager._kuzu_available:
        print("⚠️ KuzuDB is not available.")
        print("Please install it with: pip install kuzu")
        return 1
    
    while True:
        print("\n🌿 Choose an option:")
        print("1. Initialize database")
        print("2. Query database")
        print("3. Search plants by coordinates")
        print("4. Show database info")
        print("5. Show garden structures")
        print("6. Check coordinate usability")
        print("7. Reload TOML configuration")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            initialize_database()
        elif choice == '2':
            query_database()
        elif choice == '3':
            search_by_coordinates()
        elif choice == '4':
            show_database_info()
        elif choice == '5':
            show_structures()
        elif choice == '6':
            check_coordinate_usability()
        elif choice == '7':
            reload_toml_config()
        elif choice == '8':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-8.")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Goodbye!")
