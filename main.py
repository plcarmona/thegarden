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
    
    # Connect to database
    conn = kuzu_manager.connect()
    if not conn:
        print("❌ Could not connect to KuzuDB. Make sure it's installed:")
        print("   pip install kuzu")
        return False
    
    try:
        # Initialize schema
        print("🔧 Creating database schema...")
        kuzu_manager.initialize_schema()
        
        # Load initial data
        print("📦 Loading initial data...")
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
    print("  MATCH (h:Hortaliza) RETURN h.nombre LIMIT 5")
    print("  MATCH (p:Planta) RETURN count(p)")
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
        radius = input("Enter search radius (default 20): ").strip()
        radius = float(radius) if radius else 20.0
        
        print(f"\n🔍 Searching plants near ({x}, {y}) with radius {radius}...")
        
        conn = kuzu_manager.connect()
        if not conn:
            print("❌ Could not connect to database")
            return
        
        try:
            plantas = kuzu_manager.query_plantas_by_coordinates(x, y, radius)
            
            if plantas:
                print(f"\n✅ Found {len(plantas)} plants:")
                for planta in plantas:
                    print(f"  📍 ID: {planta['id']}")
                    print(f"     Plant: {planta['hortaliza_nombre']}")
                    print(f"     Position: ({planta['coordenadas_x']}, {planta['coordenadas_y']})")
                    print(f"     Distance: {planta['distancia']:.1f} units")
                    print(f"     Status: {planta['estado']}")
                    print()
            else:
                print("🔍 No plants found in the specified area")
                
        finally:
            kuzu_manager.close()
            
    except ValueError:
        print("❌ Invalid coordinate values. Please enter numbers.")
    except Exception as e:
        print(f"❌ Error searching: {e}")


def show_database_info():
    """Show database information and statistics"""
    conn = kuzu_manager.connect()
    if not conn:
        print("❌ Could not connect to database")
        return
    
    try:
        print("📊 Database Information:")
        print(f"   📍 Location: {kuzu_manager.db_path}")
        print(f"   🔗 Connected: {kuzu_manager.is_available()}")
        
        if kuzu_manager.is_available():
            # Try to get some basic statistics
            queries = [
                ("Hortalizas", "MATCH (h:Hortaliza) RETURN count(h)"),
                ("Plants", "MATCH (p:Planta) RETURN count(p)"),
                ("Annotations", "MATCH (a:Anotaciones) RETURN count(a)"),
            ]
            
            print("\n📈 Statistics:")
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
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            initialize_database()
        elif choice == '2':
            query_database()
        elif choice == '3':
            search_by_coordinates()
        elif choice == '4':
            show_database_info()
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Goodbye!")