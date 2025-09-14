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
        
        # Create basic node tables
        kuzu_manager.execute_query("CREATE NODE TABLE Plant (id STRING PRIMARY KEY, name STRING, x DOUBLE, y DOUBLE)")
        kuzu_manager.execute_query("CREATE NODE TABLE Garden (id STRING PRIMARY KEY, name STRING, width DOUBLE, height DOUBLE)")
        
        # Create relationship table
        kuzu_manager.execute_query("CREATE REL TABLE GROWS_IN (FROM Plant TO Garden)")
        
        print("📦 Loading initial data...")
        
        # Create garden
        kuzu_manager.execute_query("CREATE (g:Garden {id: 'main_garden', name: 'My Garden', width: 800.0, height: 600.0})")
        
        # Create plants
        kuzu_manager.execute_query("CREATE (p:Plant {id: 'tomato_1', name: 'Tomato Plant', x: 100.0, y: 100.0})")
        kuzu_manager.execute_query("CREATE (p:Plant {id: 'lettuce_1', name: 'Lettuce Plant', x: 200.0, y: 150.0})")
        kuzu_manager.execute_query("CREATE (p:Plant {id: 'carrot_1', name: 'Carrot Plant', x: 150.0, y: 200.0})")
        
        # Create relationships
        kuzu_manager.execute_query("""
            MATCH (p:Plant {id: 'tomato_1'}), (g:Garden {id: 'main_garden'})
            CREATE (p)-[:GROWS_IN]->(g)
        """)
        
        kuzu_manager.execute_query("""
            MATCH (p:Plant {id: 'lettuce_1'}), (g:Garden {id: 'main_garden'})
            CREATE (p)-[:GROWS_IN]->(g)
        """)
        
        kuzu_manager.execute_query("""
            MATCH (p:Plant {id: 'carrot_1'}), (g:Garden {id: 'main_garden'})
            CREATE (p)-[:GROWS_IN]->(g)
        """)
        
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
    print("  MATCH (p:Plant) RETURN p.name LIMIT 5")
    print("  MATCH (p:Plant) RETURN count(p)")
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
            # Simple distance-based query using parameters to avoid SQL injection
            query = """
            MATCH (p:Plant)
            WHERE sqrt(pow(p.x - $x, 2) + pow(p.y - $y, 2)) <= $radius
            RETURN p.id, p.name, p.x, p.y, sqrt(pow(p.x - $x, 2) + pow(p.y - $y, 2)) as distance
            ORDER BY distance
            """
            
            result = kuzu_manager.execute_query(query, {"x": x, "y": y, "radius": radius})
            
            plants = []
            if result and result.has_next():
                while result.has_next():
                    row = result.get_next()
                    plants.append({
                        'id': row[0],
                        'name': row[1],
                        'x': row[2],
                        'y': row[3],
                        'distance': row[4]
                    })
            
            if plants:
                print(f"\n✅ Found {len(plants)} plants:")
                for plant in plants:
                    print(f"  📍 {plant['name']} ({plant['id']})")
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
            ("Total Plants", "MATCH (p:Plant) RETURN count(p)"),
            ("Total Gardens", "MATCH (g:Garden) RETURN count(g)"),
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
        
        # List all plants
        print("\n🌱 Plants in database:")
        try:
            result = kuzu_manager.execute_query("MATCH (p:Plant) RETURN p.id, p.name, p.x, p.y")
            if result and result.has_next():
                while result.has_next():
                    row = result.get_next()
                    print(f"   - {row[1]} ({row[0]}) at ({row[2]}, {row[3]})")
            else:
                print("   No plants found")
        except Exception as e:
            print(f"   Error listing plants: {e}")
        
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
