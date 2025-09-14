#!/usr/bin/env python3
"""
Web GUI Server for The Garden
Provides a Flask-based web interface with API endpoints for the garden database
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS

# Add the database module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.kuzu_manager import kuzu_manager
from database.toml_loader import toml_loader

app = Flask(__name__, 
           static_folder='gui',
           template_folder='gui')
CORS(app)  # Enable CORS for frontend

# Global state
gui_data = {
    'plants': [],
    'annotations': [],
    'structures': [],
    'vegetables': []
}

def load_data_from_db():
    """Load all data from the database"""
    global gui_data
    
    if not kuzu_manager._kuzu_available:
        print("⚠️ KuzuDB not available, using mock data")
        return False
    
    conn = kuzu_manager.connect()
    if not conn:
        print("❌ Could not connect to database")
        return False
    
    try:
        # Load plants with their vegetable types
        plants_query = """
        MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
        RETURN p.id, h.nombre, p.coordenadas_x, p.coordenadas_y, p.fecha_siembra
        """
        result = kuzu_manager.execute_query(plants_query)
        plants = []
        if result and result.has_next():
            while result.has_next():
                row = result.get_next()
                plants.append({
                    'id': row[0],
                    'vegetable_name': row[1],
                    'x': float(row[2]) if row[2] is not None else 0.0,
                    'y': float(row[3]) if row[3] is not None else 0.0,
                    'planting_date': row[4] if row[4] else None
                })
        gui_data['plants'] = plants
        
        # Load annotations
        annotations_query = """
        MATCH (a:Anotation)
        RETURN a.id, a.titulo, a.contenido, a.tipo, a.fecha_creacion
        """
        result = kuzu_manager.execute_query(annotations_query)
        annotations = []
        if result and result.has_next():
            while result.has_next():
                row = result.get_next()
                annotations.append({
                    'id': row[0],
                    'title': row[1] if row[1] else 'No title',
                    'content': row[2] if row[2] else 'No content',
                    'type': row[3] if row[3] else 'observation',
                    'created_date': row[4] if row[4] else datetime.now().strftime('%Y-%m-%d'),
                    'x': 200 + len(annotations) * 50,  # Mock positions for now
                    'y': 150 + len(annotations) * 30
                })
        gui_data['annotations'] = annotations
        
        # Load structures
        structures = kuzu_manager.query_all_estructuras()
        gui_data['structures'] = structures
        
        # Load available vegetables
        vegetables_query = """
        MATCH (h:Hortaliza)
        RETURN h.id, h.nombre, h.descripcion
        """
        result = kuzu_manager.execute_query(vegetables_query)
        vegetables = []
        if result and result.has_next():
            while result.has_next():
                row = result.get_next()
                vegetables.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2] if row[2] else ''
                })
        gui_data['vegetables'] = vegetables
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading data from database: {e}")
        return False
    finally:
        kuzu_manager.close()

def load_mock_data():
    """Load mock data for development"""
    global gui_data
    
    gui_data['plants'] = [
        {'id': 'plant_001', 'x': 100.0, 'y': 150.0, 'vegetable_name': 'Tomate', 'planting_date': '2024-01-15'},
        {'id': 'plant_002', 'x': 200.0, 'y': 100.0, 'vegetable_name': 'Lechuga', 'planting_date': '2024-01-20'},
        {'id': 'plant_003', 'x': 150.0, 'y': 250.0, 'vegetable_name': 'Zanahoria', 'planting_date': '2024-02-01'},
        {'id': 'plant_004', 'x': 300.0, 'y': 180.0, 'vegetable_name': 'Pimiento', 'planting_date': '2024-02-05'},
        {'id': 'plant_005', 'x': 80.0, 'y': 300.0, 'vegetable_name': 'Espinaca', 'planting_date': '2024-02-10'}
    ]
    
    gui_data['structures'] = [
        {
            'id': 'struct_001',
            'name': 'Casa de Herramientas',
            'type': 'edificio',
            'description': 'Pequeña caseta para almacenar herramientas',
            'polygon': [[50.0, 50.0], [150.0, 50.0], [150.0, 120.0], [50.0, 120.0]]
        },
        {
            'id': 'struct_002',
            'name': 'Camino Principal',
            'type': 'camino',
            'description': 'Sendero principal del jardín',
            'polygon': [[0.0, 200.0], [400.0, 200.0], [400.0, 220.0], [0.0, 220.0]]
        }
    ]
    
    gui_data['annotations'] = [
        {
            'id': 'ann_001',
            'title': 'Riego diario necesario',
            'content': 'Las tomateras necesitan riego diario durante el verano. Revisar sistema de goteo.',
            'type': 'observation',
            'created_date': '2024-02-15',
            'x': 100.0,
            'y': 130.0
        },
        {
            'id': 'ann_002',
            'title': 'Plagas detectadas',
            'content': 'Se observaron pulgones en las lechugas. Aplicar tratamiento orgánico.',
            'type': 'problem',
            'created_date': '2024-02-14',
            'x': 200.0,
            'y': 80.0
        },
        {
            'id': 'ann_003',
            'title': 'Cosecha de zanahorias',
            'content': 'Las zanahorias están listas para cosechar. Aproximadamente 2kg esperados.',
            'type': 'harvest',
            'created_date': '2024-02-16',
            'x': 150.0,
            'y': 270.0
        }
    ]
    
    gui_data['vegetables'] = [
        {'id': 1, 'name': 'Tomate', 'description': 'Solanum lycopersicum - Hortaliza de fruto muy popular'},
        {'id': 2, 'name': 'Lechuga', 'description': 'Lactuca sativa - Hortaliza de hoja de crecimiento rápido'},
        {'id': 3, 'name': 'Zanahoria', 'description': 'Daucus carota - Hortaliza de raíz rica en betacaroteno'},
        {'id': 4, 'name': 'Pimiento', 'description': 'Capsicum annuum - Hortaliza de fruto versátil'},
        {'id': 5, 'name': 'Espinaca', 'description': 'Spinacia oleracea - Hortaliza de hoja rica en hierro'}
    ]

@app.route('/')
def index():
    """Serve the main GUI page"""
    return send_from_directory('gui', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files from gui directory"""
    return send_from_directory('gui', filename)

# API Endpoints

@app.route('/api/plants')
def get_plants():
    """Get all plants"""
    return jsonify(gui_data['plants'])

@app.route('/api/plants', methods=['POST'])
def add_plant():
    """Add a new plant"""
    data = request.get_json()
    
    if not kuzu_manager._kuzu_available:
        # Mock mode - add locally
        new_plant = {
            'id': f"plant_{datetime.now().timestamp()}",
            'x': data['x'],
            'y': data['y'],
            'vegetable_name': next((v['name'] for v in gui_data['vegetables'] if v['id'] == data['vegetable_id']), 'Unknown'),
            'planting_date': data.get('planting_date')
        }
        gui_data['plants'].append(new_plant)
        return jsonify(new_plant), 201
    
    # Try to add to database
    conn = kuzu_manager.connect()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        # Generate unique plant ID
        plant_id = f"plant_{int(datetime.now().timestamp())}"
        
        # Create plant node
        create_plant_query = """
        CREATE (p:Planta {
            id: $plant_id,
            coordenadas_x: $x,
            coordenadas_y: $y,
            fecha_siembra: $planting_date
        })
        """
        
        kuzu_manager.execute_query(create_plant_query, {
            'plant_id': plant_id,
            'x': data['x'],
            'y': data['y'],
            'planting_date': data.get('planting_date', '')
        })
        
        # Create relationship to vegetable type
        create_relationship_query = """
        MATCH (p:Planta {id: $plant_id}), (h:Hortaliza {id: $vegetable_id})
        CREATE (p)-[:IS_OF_TYPE]->(h)
        """
        
        kuzu_manager.execute_query(create_relationship_query, {
            'plant_id': plant_id,
            'vegetable_id': data['vegetable_id']
        })
        
        # Get the created plant with vegetable info
        get_plant_query = """
        MATCH (p:Planta {id: $plant_id})-[:IS_OF_TYPE]->(h:Hortaliza)
        RETURN p.id, h.nombre, p.coordenadas_x, p.coordenadas_y, p.fecha_siembra
        """
        
        result = kuzu_manager.execute_query(get_plant_query, {'plant_id': plant_id})
        if result and result.has_next():
            row = result.get_next()
            new_plant = {
                'id': row[0],
                'vegetable_name': row[1],
                'x': float(row[2]),
                'y': float(row[3]),
                'planting_date': row[4]
            }
            gui_data['plants'].append(new_plant)
            return jsonify(new_plant), 201
        
        return jsonify({'error': 'Plant created but could not retrieve'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Failed to add plant: {str(e)}'}), 500
    finally:
        kuzu_manager.close()

@app.route('/api/plants/<plant_id>', methods=['DELETE'])
def remove_plant(plant_id):
    """Remove a plant"""
    if not kuzu_manager._kuzu_available:
        # Mock mode - remove locally
        gui_data['plants'] = [p for p in gui_data['plants'] if p['id'] != plant_id]
        return jsonify({'message': 'Plant removed (mock mode)'}), 200
    
    conn = kuzu_manager.connect()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        # Delete plant and its relationships
        delete_query = """
        MATCH (p:Planta {id: $plant_id})
        DETACH DELETE p
        """
        
        kuzu_manager.execute_query(delete_query, {'plant_id': plant_id})
        
        # Remove from local cache
        gui_data['plants'] = [p for p in gui_data['plants'] if p['id'] != plant_id]
        
        return jsonify({'message': 'Plant removed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to remove plant: {str(e)}'}), 500
    finally:
        kuzu_manager.close()

@app.route('/api/annotations')
def get_annotations():
    """Get all annotations"""
    return jsonify(gui_data['annotations'])

@app.route('/api/annotations', methods=['POST'])
def add_annotation():
    """Add a new annotation"""
    data = request.get_json()
    
    if not kuzu_manager._kuzu_available:
        # Mock mode - add locally
        new_annotation = {
            'id': f"ann_{int(datetime.now().timestamp())}",
            'title': data['title'],
            'content': data['content'],
            'type': data['type'],
            'created_date': data.get('created_date', datetime.now().strftime('%Y-%m-%d')),
            'x': 200.0 + len(gui_data['annotations']) * 50,
            'y': 150.0 + len(gui_data['annotations']) * 30
        }
        gui_data['annotations'].append(new_annotation)
        return jsonify(new_annotation), 201
    
    conn = kuzu_manager.connect()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        # Generate unique annotation ID
        annotation_id = f"ann_{int(datetime.now().timestamp())}"
        
        # Create annotation node
        create_annotation_query = """
        CREATE (a:Anotation {
            id: $annotation_id,
            titulo: $title,
            contenido: $content,
            tipo: $type,
            fecha_creacion: $created_date
        })
        """
        
        kuzu_manager.execute_query(create_annotation_query, {
            'annotation_id': annotation_id,
            'title': data['title'],
            'content': data['content'],
            'type': data['type'],
            'created_date': data.get('created_date', datetime.now().strftime('%Y-%m-%d'))
        })
        
        new_annotation = {
            'id': annotation_id,
            'title': data['title'],
            'content': data['content'],
            'type': data['type'],
            'created_date': data.get('created_date', datetime.now().strftime('%Y-%m-%d')),
            'x': 200.0 + len(gui_data['annotations']) * 50,
            'y': 150.0 + len(gui_data['annotations']) * 30
        }
        
        gui_data['annotations'].append(new_annotation)
        return jsonify(new_annotation), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to add annotation: {str(e)}'}), 500
    finally:
        kuzu_manager.close()

@app.route('/api/structures')
def get_structures():
    """Get all structures"""
    return jsonify(gui_data['structures'])

@app.route('/api/vegetables')
def get_vegetables():
    """Get all available vegetables"""
    return jsonify(gui_data['vegetables'])

@app.route('/api/initialize', methods=['POST'])
def initialize_database():
    """Initialize the database"""
    if not kuzu_manager._kuzu_available:
        return jsonify({'error': 'KuzuDB not available'}), 500
    
    try:
        # Remove old database
        import shutil
        if os.path.exists("database/garden.kuzu"):
            if os.path.isfile("database/garden.kuzu"):
                os.remove("database/garden.kuzu")
            else:
                shutil.rmtree("database/garden.kuzu")
        
        # Connect and initialize
        conn = kuzu_manager.connect()
        if not conn:
            return jsonify({'error': 'Could not connect to database'}), 500
        
        # Initialize schema and data
        schema_success = kuzu_manager.initialize_schema()
        if not schema_success:
            return jsonify({'error': 'Schema initialization failed'}), 500
        
        kuzu_manager.load_initial_data()
        kuzu_manager.close()
        
        # Reload data
        if load_data_from_db():
            return jsonify({'message': 'Database initialized successfully'}), 200
        else:
            return jsonify({'error': 'Database initialized but could not reload data'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to initialize database: {str(e)}'}), 500

@app.route('/api/reload')
def reload_data():
    """Reload data from database"""
    if load_data_from_db():
        return jsonify({'message': 'Data reloaded successfully', 'data': gui_data}), 200
    else:
        load_mock_data()
        return jsonify({'message': 'Loaded mock data (database unavailable)', 'data': gui_data}), 200

def main():
    """Main entry point"""
    print("🌱 The Garden - Web GUI Server")
    print("=" * 40)
    
    # Load initial data
    if not load_data_from_db():
        print("⚠️ Could not load from database, using mock data")
        load_mock_data()
    else:
        print("✅ Data loaded from database")
    
    print(f"📊 Loaded: {len(gui_data['plants'])} plants, {len(gui_data['annotations'])} annotations, {len(gui_data['structures'])} structures")
    print("\n🌐 Starting web server...")
    print("   Open your browser to: http://localhost:5000")
    print("   Press Ctrl+C to stop")
    
    # Run Flask app
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == '__main__':
    main()