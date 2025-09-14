#!/usr/bin/env python3
"""
The Garden - Web GUI Application
Web-based graphical interface for managing garden plants and database
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
import os
from datetime import datetime
from database.kuzu_manager import kuzu_manager
from database.toml_loader import toml_loader

app = Flask(__name__, template_folder='templates', static_folder='gui')
app.secret_key = 'garden_secret_key_2024'  # For session management and flash messages

# Global state
db_status = {
    'connected': False,
    'available': kuzu_manager._kuzu_available,
    'message': 'Not connected'
}


@app.route('/')
def index():
    """Main page"""
    return send_from_directory('gui', 'index.html')


@app.route('/garden-gui.js')
def serve_js():
    """Serve the JavaScript file"""
    return send_from_directory('gui', 'garden-gui.js')


@app.route('/api/db_status')
def api_db_status():
    """Get current database status"""
    return jsonify(db_status)


@app.route('/api/initialize_db', methods=['POST'])
def api_initialize_db():
    """Initialize the database"""
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
            raise Exception("Could not connect to KuzuDB")
        
        try:
            # Initialize schema and data
            schema_success = kuzu_manager.initialize_schema()
            if not schema_success:
                raise Exception("Schema initialization failed")
            
            kuzu_manager.load_initial_data()
            
            db_status['connected'] = True
            db_status['message'] = 'Database initialized and connected'
            
            return jsonify({'success': True, 'message': 'Database initialized successfully!'})
        finally:
            kuzu_manager.close(conn)  # Pass the specific connection to close
        
    except Exception as e:
        db_status['connected'] = False
        db_status['message'] = f'Initialization failed: {str(e)}'
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/connect_db', methods=['POST'])
def api_connect_db():
    """Connect to the database"""
    try:
        if not kuzu_manager._kuzu_available:
            raise Exception("KuzuDB is not available. Please install it with: pip install kuzu")
        
        conn = kuzu_manager.connect()
        if conn:
            db_status['connected'] = True
            db_status['message'] = 'Connected successfully'
            kuzu_manager.close(conn)  # Pass the specific connection to close
            return jsonify({'success': True, 'message': 'Connected to database successfully'})
        else:
            raise Exception("Failed to connect to database")
            
    except Exception as e:
        db_status['connected'] = False
        db_status['message'] = f'Connection failed: {str(e)}'
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/plants')
def api_get_plants():
    """Get all plants from database"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            return jsonify({'success': False, 'message': 'Could not connect to database'})
        
        try:
            # Update status since we successfully connected
            db_status['connected'] = True
            db_status['message'] = 'Connected successfully'
            
            # Query all plants
            result = kuzu_manager.execute_query("""
                MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
                RETURN p.id, h.nombre, p.coordenadas_x, p.coordenadas_y, p.fecha_siembra
                ORDER BY p.id
            """, connection=conn)
            
            plants = []
            if result and result.has_next():
                while result.has_next():
                    row = result.get_next()

                    plant_date = row[4] if row[4] else "Unknown"
                    
                    # Format date for display
                    if isinstance(plant_date, datetime):
                        plant_date = plant_date.strftime("%Y-%m-%d %H:%M")
                    
                    plants.append({
                        'id': row[0],
                        'type': row[1],
                        'x': row[2],
                        'y': row[3],
                        'date': plant_date
                    })
            
            return jsonify({'success': True, 'plants': plants})
        finally:
            kuzu_manager.close(conn)  # Pass the specific connection to close
        
    except Exception as e:
        db_status['connected'] = False
        db_status['message'] = f'Connection failed: {str(e)}'
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/vegetables')
def api_vegetables():
    """Get available vegetables (alias for hortalizas)"""
    try:
        hortalizas_config = toml_loader.get_hortalizas()
        if hortalizas_config:
            vegetables = [{
                'id': h['id'],
                'name': h['nombre'],
                'description': h['descripcion']
            } for h in hortalizas_config]
            return jsonify(vegetables)
        else:
            return jsonify([])
    except Exception as e:
        return jsonify([])  # Return empty array on error


@app.route('/api/initialize', methods=['POST'])
def api_initialize():
    """Initialize database (alias for initialize_db)"""
    return api_initialize_db()


@app.route('/api/annotations')
def api_annotations():
    """Get all annotations from database"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            return jsonify({'success': False, 'message': 'Could not connect to database'})
        
        try:
            # Update status since we successfully connected
            db_status['connected'] = True
            db_status['message'] = 'Connected successfully'
            
            annotations = kuzu_manager.query_all_annotations(connection=conn)
            
            # Format annotations for frontend
            formatted_annotations = []
            for annotation in annotations:
                fecha = annotation['fecha']
                if isinstance(fecha, datetime):
                    fecha_str = fecha.strftime("%Y-%m-%d %H:%M")
                else:
                    fecha_str = str(fecha) if fecha else "Unknown"
                    
                formatted_annotations.append({
                    'id': annotation['id'],
                    'type': annotation['tipo'],
                    'content': annotation['comentario'],
                    'date': fecha_str
                })
            
            return jsonify({'success': True, 'annotations': formatted_annotations})
        finally:
            kuzu_manager.close(conn)  # Pass the specific connection to close
        
    except Exception as e:
        db_status['connected'] = False
        db_status['message'] = f'Connection failed: {str(e)}'
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/structures')
def api_structures():
    """Get all structures from database"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            return jsonify({'success': False, 'message': 'Could not connect to database'})
        
        try:
            # Update status since we successfully connected
            db_status['connected'] = True
            db_status['message'] = 'Connected successfully'
            
            structures = kuzu_manager.query_all_estructuras(connection=conn)
            
            # Format structures for frontend
            formatted_structures = []
            for structure in structures:
                fecha = structure['fecha_creacion']
                if isinstance(fecha, datetime):
                    fecha_str = fecha.strftime("%Y-%m-%d %H:%M")
                else:
                    fecha_str = str(fecha) if fecha else "Unknown"
                    
                formatted_structures.append({
                    'id': structure['id'],
                    'name': structure['nombre'],
                    'type': structure['tipo'],
                    'description': structure['descripcion'],
                    'polygon': structure['poligono'],
                    'date': fecha_str
                })
            
            return jsonify({'success': True, 'structures': formatted_structures})
        finally:
            kuzu_manager.close(conn)  # Pass the specific connection to close
        
    except Exception as e:
        db_status['connected'] = False
        db_status['message'] = f'Connection failed: {str(e)}'
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/hortalizas')
def api_get_hortalizas():
    """Get available plant types"""
    try:
        hortalizas_config = toml_loader.get_hortalizas()
        if hortalizas_config:
            hortalizas = [{
                'id': h['id'],
                'name': h['nombre'],
                'description': h['descripcion']
            } for h in hortalizas_config]
            return jsonify({'success': True, 'hortalizas': hortalizas})
        else:
            return jsonify({'success': False, 'message': 'No plant types found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/check_coordinates')
def api_check_coordinates():
    """Check if coordinates are usable for planting"""
    if not db_status['connected']:
        return jsonify({'success': False, 'message': 'Database not connected'})
    
    try:
        x = float(request.args.get('x', 0))
        y = float(request.args.get('y', 0))
        
        conn = kuzu_manager.connect()
        if not conn:
            raise Exception("Could not connect to database")
        
        try:
            intersecting = kuzu_manager.check_coordinate_in_structure(x, y, connection=conn)
            
            if intersecting:
                structure_names = [s['nombre'] for s in intersecting]
                return jsonify({
                    'success': True,
                    'usable': False,
                    'message': f"Blocked by: {', '.join(structure_names)}",
                    'structures': structure_names
                })
            else:
                return jsonify({
                    'success': True,
                    'usable': True,
                    'message': 'Coordinates are usable',
                    'structures': []
                })
        finally:
            kuzu_manager.close(conn)  # Pass the specific connection to close
            
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid coordinate values'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/plants', methods=['POST'])
def api_add_plant():
    """Add a new plant to the database"""
    try:
        data = request.json
        # Accept both vegetable_id and plant_type_id for compatibility
        plant_type_id = int(data.get('vegetable_id') or data.get('plant_type_id'))
        x_coord = float(data.get('x'))
        y_coord = float(data.get('y'))
        
        # Get hortaliza name
        hortalizas_config = toml_loader.get_hortalizas()
        hortaliza = next((h for h in hortalizas_config if h['id'] == plant_type_id), None)
        if not hortaliza:
            raise Exception("Invalid plant type")
        
        hortaliza_name = hortaliza['nombre']
        
        # Generate unique plant ID
        plant_id = f"{hortaliza_name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Check coordinate usability
        conn = kuzu_manager.connect()
        if not conn:
            return jsonify({'success': False, 'message': 'Could not connect to database'})
        
        try:
            # Update status since we successfully connected
            db_status['connected'] = True
            db_status['message'] = 'Connected successfully'
            
            intersecting = kuzu_manager.check_coordinate_in_structure(x_coord, y_coord, connection=conn)
            if intersecting and not data.get('force_add', False):
                structure_names = [s['nombre'] for s in intersecting]
                return jsonify({
                    'success': False,
                    'needs_confirmation': True,
                    'message': f"Coordinates intersect with structures: {', '.join(structure_names)}. Add anyway?",
                    'structures': structure_names
                })
            
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
                'fecha_siembra': datetime.now().date(),  # Use date() instead of datetime
                'coordenadas_x': x_coord,
                'coordenadas_y': y_coord
            }, connection=conn)
            
            # Create relationship with hortaliza
            relate_query = """
            MATCH (p:Planta {id: $planta_id}), (h:Hortaliza {id: $hortaliza_id})
            CREATE (p)-[:IS_OF_TYPE {fecha_relacion: $fecha}]->(h)
            """
            
            kuzu_manager.execute_query(relate_query, {
                'planta_id': plant_id,
                'hortaliza_id': plant_type_id,
                'fecha': datetime.now()
            }, connection=conn)
            
            # Create relationship with default garden
            garden_relate_query = """
            MATCH (p:Planta {id: $planta_id}), (h:Huerta {id: "huerta_default"})
            CREATE (p)-[:PART_OF {fecha_relacion: $fecha}]->(h)
            """
            
            kuzu_manager.execute_query(garden_relate_query, {
                'planta_id': plant_id,
                'fecha': datetime.now()
            }, connection=conn)
            
            # Return the created plant object for frontend
            return jsonify({
                'success': True,
                'message': f'Plant {plant_id} added successfully!',
                'plant': {
                    'id': plant_id,
                    'type': hortaliza_name,
                    'x': x_coord,
                    'y': y_coord,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M")
                }
            })
        finally:
            kuzu_manager.close(conn)  # Pass the specific connection to close
        
        # Return the created plant object for frontend
        return jsonify({
            'success': True,
            'message': f'Plant {plant_id} added successfully!',
            'plant_id': plant_id,
            'id': plant_id,
            'x': x_coord,
            'y': y_coord,
            'type': hortaliza_name,
            'vegetable_name': hortaliza_name,
            'planting_date': datetime.now().date().isoformat(),
            'date': datetime.now().date().isoformat()
        })
        
    except Exception as e:
        db_status['connected'] = False
        db_status['message'] = f'Connection failed: {str(e)}'
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/plants/<plant_id>', methods=['DELETE'])
def api_remove_plant_by_id(plant_id):
    """Remove a plant from the database by ID (DELETE method)"""
    if not db_status['connected']:
        return jsonify({'success': False, 'message': 'Database not connected'})
    
    try:
        if not plant_id:
            raise Exception("Plant ID is required")
        
        conn = kuzu_manager.connect()
        if not conn:
            raise Exception("Could not connect to database")
        
        try:
            # Remove plant and all its relationships
            remove_query = """
            MATCH (p:Planta {id: $plant_id})
            DETACH DELETE p
            """
            kuzu_manager.execute_query(remove_query, {'plant_id': plant_id}, connection=conn)
            
            return jsonify({
                'success': True,
                'message': f'Plant {plant_id} removed successfully'
            })
        finally:
            kuzu_manager.close(conn)  # Pass the specific connection to close
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/remove_plant', methods=['POST'])
def api_remove_plant():
    """Remove a plant from the database"""
    if not db_status['connected']:
        return jsonify({'success': False, 'message': 'Database not connected'})
    
    try:
        data = request.json
        plant_id = data.get('plant_id')
        
        if not plant_id:
            raise Exception("Plant ID is required")
        
        conn = kuzu_manager.connect()
        if not conn:
            raise Exception("Could not connect to database")
        
        try:
            # Remove plant and all its relationships
            remove_query = """
            MATCH (p:Planta {id: $plant_id})
            DETACH DELETE p
            """
            kuzu_manager.execute_query(remove_query, {'plant_id': plant_id}, connection=conn)
            
            return jsonify({
                'success': True,
                'message': f'Plant {plant_id} removed successfully'
            })
        finally:
            kuzu_manager.close(conn)  # Pass the specific connection to close
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/add_annotation', methods=['POST'])
def api_add_annotation():
    """Add a new annotation to the database"""
    if not db_status['connected']:
        return jsonify({'success': False, 'message': 'Database not connected'})
    
    try:
        data = request.json
        annotation_type = data.get('type', 'observation')
        title = data.get('title', '')
        content = data.get('content', '')
        target = data.get('target', 'garden')
        target_id = data.get('target_id')
        
        if not content.strip():
            raise Exception("Content is required for annotations")
        
        # Combine title and content for the comment field
        comentario = f"{title}: {content}" if title else content
        
        conn = kuzu_manager.connect()
        if not conn:
            raise Exception("Could not connect to database")
        
        try:
            success = kuzu_manager.add_annotation(
                tipo=annotation_type,
                comentario=comentario,
                target_type=target,
                target_id=target_id
            )
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Annotation added successfully!'
                })
            else:
                raise Exception("Failed to add annotation")
        finally:
            kuzu_manager.close(conn)  # Pass the specific connection to close
            raise Exception("Failed to add annotation to database")
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/garden_stats')
def api_garden_stats():
    """Get garden statistics"""
    if not db_status['connected']:
        return jsonify({'success': False, 'message': 'Database not connected'})
    
    try:
        conn = kuzu_manager.connect()
        if not conn:
            raise Exception("Could not connect to database")
        
        try:
            stats = {}
            
            # Get basic statistics
            queries = [
                ("plants", "MATCH (p:Planta) RETURN count(p)"),
                ("gardens", "MATCH (hu:Huerta) RETURN count(hu)"),
                ("vegetable_types", "MATCH (h:Hortaliza) RETURN count(h)"),
                ("annotations", "MATCH (a:Anotation) RETURN count(a)"),
                ("structures", "MATCH (e:Estructura) RETURN count(e)"),
            ]
            
            for name, query in queries:
                try:
                    result = kuzu_manager.execute_query(query, connection=conn)
                    if result and result.has_next():
                        count = result.get_next()[0]
                        stats[name] = count
                    else:
                        stats[name] = 0
                except Exception as e:
                    stats[name] = f"Error: {e}"
            
            # Get structures info
            try:
                estructuras = kuzu_manager.query_all_estructuras()
                stats['structures_list'] = [{
                    'name': e['nombre'],
                    'type': e['tipo'],
                    'vertices': len(e['poligono']) if e['poligono'] else 0
                } for e in estructuras] if estructuras else []
            except:
                stats['structures_list'] = []
            
            return jsonify({'success': True, 'stats': stats})
        finally:
            kuzu_manager.close(conn)  # Pass the specific connection to close
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/reset_db', methods=['POST'])
def api_reset_db():
    """Reset/refresh the database - reinitialize with fresh data"""
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
            raise Exception("Could not connect to KuzuDB")
        
        try:
            # Initialize schema and data
            schema_success = kuzu_manager.initialize_schema()
            if not schema_success:
                raise Exception("Schema initialization failed")
            
            kuzu_manager.load_initial_data()
            
            db_status['connected'] = True
            db_status['message'] = 'Database reset and reinitialized'
            
            return jsonify({'success': True, 'message': 'Database reset successfully!'})
        finally:
            kuzu_manager.close(conn)  # Pass the specific connection to close
        
    except Exception as e:
        db_status['connected'] = False
        db_status['message'] = f'Reset failed: {str(e)}'
        return jsonify({'success': False, 'message': str(e)})


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5001)
