#!/usr/bin/env python3
"""
The Garden - FastAPI GUI Application
FastAPI-based graphical interface for managing garden plants and database
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from datetime import datetime
from database.kuzu_manager import kuzu_manager
from database.toml_loader import toml_loader
import time
import random

def is_point_in_polygon(x, y, polygon):
    """Check if a point is inside a polygon using ray casting algorithm"""
    if not polygon or len(polygon) < 3:
        return False
    
    n = len(polygon)
    inside = False
    
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside

app = FastAPI(title="The Garden GUI", description="Garden Plant Management System", version="1.0.0")

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="gui"), name="static")

# Templates
templates = Jinja2Templates(directory="gui")

# Pydantic models for API requests/responses
class PlantCreateRequest(BaseModel):
    hortaliza_id: int
    coordenadas_x: float
    coordenadas_y: float

# Alternative plant request models for different frontend formats
class PlantCreateRequestAlt1(BaseModel):
    vegetable_id: int
    x: float
    y: float
    planting_date: Optional[str] = None

class PlantCreateRequestAlt2(BaseModel):
    plant_type_id: int
    x_coord: float
    y_coord: float
    force_add: Optional[bool] = False

class AnnotationCreateRequest(BaseModel):
    tipo: str
    comentario: str
    entity_type: str  # 'planta', 'huerta', or 'hortaliza'
    entity_id: str

# Alternative annotation request for different frontend format
class AnnotationCreateRequestAlt(BaseModel):
    type: str
    content: str
    target_type: Optional[str] = "garden"
    target_id: Optional[str] = None

class QueryRequest(BaseModel):
    query: str

class CoordinateRequest(BaseModel):
    x: float
    y: float
    radius: Optional[float] = 1.0

class DatabaseStatus(BaseModel):
    connected: bool
    available: bool
    message: str

# Global state
db_status = {
    'connected': False,
    'available': kuzu_manager._kuzu_available,
    'message': 'Not connected'
}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Main page - serve the HTML interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/db_status", response_model=DatabaseStatus)
async def get_db_status():
    """Get current database status"""
    return DatabaseStatus(**db_status)

@app.post("/api/initialize_db")
async def initialize_database():
    """Initialize the database with schema and initial data"""
    try:
        # Remove old database if exists
        import shutil
        if os.path.exists("database/garden.kuzu"):
            if os.path.isfile("database/garden.kuzu"):
                os.remove("database/garden.kuzu")
            elif os.path.isdir("database/garden.kuzu"):
                shutil.rmtree("database/garden.kuzu")
        
        # Initialize database
        kuzu_manager.initialize_database()
        
        # Update status
        db_status['connected'] = True
        db_status['message'] = 'Database initialized successfully'
        
        return {"success": True, "message": "Database initialized successfully"}
        
    except Exception as e:
        db_status['connected'] = False
        db_status['message'] = f'Error initializing database: {str(e)}'
        raise HTTPException(status_code=500, detail=f"Error initializing database: {str(e)}")

@app.get("/api/plants")
async def get_plants():
    """Get all plants from database"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        result = conn.execute("""
            MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
            RETURN p.id as plant_id, p.coordenadas_x as x, p.coordenadas_y as y, 
                   p.fecha_siembra as date, h.id as hortaliza_id, h.nombre as hortaliza_name
        """)
        
        plants = []
        while result.has_next():
            row = result.get_next()
            plants.append({
                'id': row[0],
                'x': row[1],
                'y': row[2],
                'date': row[3].isoformat() if row[3] else None,
                'type': row[5],  # hortaliza_name for templates compatibility
                'hortaliza_id': row[4],
                'hortaliza_name': row[5]
            })
        
        return {"success": True, "plants": plants}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving plants: {str(e)}")

@app.get("/api/hortalizas")
async def get_hortalizas():
    """Get all vegetable types"""
    try:
        hortalizas = toml_loader.get_hortalizas()
        return {"success": True, "hortalizas": hortalizas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving hortalizas: {str(e)}")

@app.post("/api/plants")
async def create_plant(plant: PlantCreateRequestAlt1):
    """Create a new plant (garden-gui.js format)"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Generate unique plant ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = random.randint(1000, 9999)
        plant_id = f"plant_{timestamp}_{random_suffix}"
        
        # Parse planting date if provided
        fecha_siembra = datetime.now().date()
        if plant.planting_date:
            try:
                fecha_siembra = datetime.strptime(plant.planting_date, '%Y-%m-%d').date()
            except ValueError:
                pass  # Use current date if parsing fails
        
        # Create plant
        conn.execute("""
            CREATE (p:Planta {
                id: $id,
                fecha_siembra: $fecha,
                coordenadas_x: $x,
                coordenadas_y: $y
            })
        """, {
            'id': plant_id,
            'fecha': fecha_siembra,
            'x': plant.x,
            'y': plant.y
        })
        
        # Create relationship with hortaliza
        conn.execute("""
            MATCH (p:Planta {id: $plant_id}), (h:Hortaliza {id: $hortaliza_id})
            CREATE (p)-[:IS_OF_TYPE {fecha_relacion: $fecha}]->(h)
        """, {
            'plant_id': plant_id,
            'hortaliza_id': plant.vegetable_id,
            'fecha': datetime.now()
        })
        
        # Create relationship with garden
        conn.execute("""
            MATCH (p:Planta {id: $plant_id}), (hu:Huerta {id: "huerta_principal"})
            CREATE (p)-[:PART_OF {fecha_relacion: $fecha}]->(hu)
        """, {
            'plant_id': plant_id,
            'fecha': datetime.now()
        })
        
        # Get vegetable name for response
        result = conn.execute("""
            MATCH (h:Hortaliza {id: $hortaliza_id})
            RETURN h.nombre as name
        """, {'hortaliza_id': plant.vegetable_id})
        
        vegetable_name = "Unknown"
        if result.has_next():
            vegetable_name = result.get_next()[0]
        
        return {
            "success": True, 
            "id": plant_id,
            "x": plant.x,
            "y": plant.y,
            "vegetable_name": vegetable_name,
            "date": fecha_siembra.isoformat(),
            "message": "Plant created successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating plant: {str(e)}")

@app.post("/api/add_plant")
async def add_plant(plant: PlantCreateRequestAlt2):
    """Add a new plant (alternative endpoint for templates/index.html)"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Check if coordinates are blocked by structures (if not force_add)
        if not plant.force_add:
            try:
                estructuras = toml_loader.get_estructuras()
                blocking_structures = []
                for estructura in estructuras:
                    polygon = estructura.get('poligono', [])
                    if is_point_in_polygon(plant.x_coord, plant.y_coord, polygon):
                        blocking_structures.append(estructura['nombre'])
                
                if blocking_structures:
                    return {
                        "success": False,
                        "needs_confirmation": True,
                        "message": f"Coordinates blocked by: {', '.join(blocking_structures)}. Do you want to add anyway?"
                    }
            except Exception as e:
                print(f"Warning: Could not check structure blocking: {e}")
        
        # Generate unique plant ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = random.randint(1000, 9999)
        plant_id = f"plant_{timestamp}_{random_suffix}"
        
        # Create plant
        conn.execute("""
            CREATE (p:Planta {
                id: $id,
                fecha_siembra: $fecha,
                coordenadas_x: $x,
                coordenadas_y: $y
            })
        """, {
            'id': plant_id,
            'fecha': datetime.now().date(),
            'x': plant.x_coord,
            'y': plant.y_coord
        })
        
        # Create relationship with hortaliza
        conn.execute("""
            MATCH (p:Planta {id: $plant_id}), (h:Hortaliza {id: $hortaliza_id})
            CREATE (p)-[:IS_OF_TYPE {fecha_relacion: $fecha}]->(h)
        """, {
            'plant_id': plant_id,
            'hortaliza_id': plant.plant_type_id,
            'fecha': datetime.now()
        })
        
        # Create relationship with garden
        conn.execute("""
            MATCH (p:Planta {id: $plant_id}), (hu:Huerta {id: "huerta_principal"})
            CREATE (p)-[:PART_OF {fecha_relacion: $fecha}]->(hu)
        """, {
            'plant_id': plant_id,
            'fecha': datetime.now()
        })
        
        return {"success": True, "plant_id": plant_id, "message": "Plant added successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding plant: {str(e)}")

@app.delete("/api/plants/{plant_id}")
async def delete_plant(plant_id: str):
    """Delete a plant"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Delete plant and all its relationships
        conn.execute("MATCH (p:Planta {id: $id}) DETACH DELETE p", {'id': plant_id})
        
        return {"success": True, "message": "Plant deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting plant: {str(e)}")

@app.get("/api/annotations")
async def get_annotations():
    """Get all annotations"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        result = conn.execute("""
            MATCH (a:Anotation)
            RETURN a.id as id, a.tipo as tipo, a.comentario as comentario, a.fecha as fecha
            ORDER BY a.fecha DESC
        """)
        
        annotations = []
        while result.has_next():
            row = result.get_next()
            annotations.append({
                'id': row[0],
                'type': row[1],  # For garden-gui.js compatibility
                'content': row[2],  # For garden-gui.js compatibility
                'date': row[3].isoformat() if row[3] else None,
                # Also keep original format for compatibility
                'tipo': row[1],
                'comentario': row[2],
                'fecha': row[3].isoformat() if row[3] else None
            })
        
        return {"success": True, "annotations": annotations}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving annotations: {str(e)}")

@app.post("/api/annotations")
async def create_annotation(annotation: AnnotationCreateRequest):
    """Create a new annotation"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Generate unique annotation ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = random.randint(1000, 9999)
        annotation_id = f"annotation_{timestamp}_{random_suffix}"
        
        # Create annotation
        conn.execute("""
            CREATE (a:Anotation {
                id: $id,
                tipo: $tipo,
                comentario: $comentario,
                fecha: $fecha
            })
        """, {
            'id': annotation_id,
            'tipo': annotation.tipo,
            'comentario': annotation.comentario,
            'fecha': datetime.now()
        })
        
        # Create relationship based on entity type
        if annotation.entity_type == 'planta':
            conn.execute("""
                MATCH (a:Anotation {id: $annotation_id}), (p:Planta {id: $entity_id})
                CREATE (p)-[:HAS_ANOTATION {fecha_relacion: $fecha}]->(a)
            """, {
                'annotation_id': annotation_id,
                'entity_id': annotation.entity_id,
                'fecha': datetime.now()
            })
        elif annotation.entity_type == 'huerta':
            conn.execute("""
                MATCH (a:Anotation {id: $annotation_id}), (h:Huerta {id: $entity_id})
                CREATE (h)-[:HAS_ANOTATION_HUERTA {fecha_relacion: $fecha}]->(a)
            """, {
                'annotation_id': annotation_id,
                'entity_id': annotation.entity_id,
                'fecha': datetime.now()
            })
        
        return {"success": True, "annotation_id": annotation_id, "message": "Annotation created successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating annotation: {str(e)}")

@app.post("/api/query")
async def execute_query(query_request: QueryRequest):
    """Execute a custom Cypher query"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Basic query validation
        query = query_request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Empty query")
        
        # Prevent destructive queries in GUI
        dangerous_keywords = ['DROP', 'DELETE', 'REMOVE', 'SET', 'CREATE', 'MERGE']
        query_upper = query.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise HTTPException(status_code=400, detail=f"Query contains dangerous keyword: {keyword}")
        
        result = conn.execute(query)
        
        # Convert result to list
        rows = []
        while result.has_next():
            rows.append(result.get_next())
        
        return {"success": True, "rows": rows, "count": len(rows)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")

@app.post("/api/search_plants")
async def search_plants_by_coordinates(coord_request: CoordinateRequest):
    """Search plants by coordinates within a radius"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Use point distance calculation
        result = conn.execute("""
            MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
            WITH p, h, 
                 sqrt((p.coordenadas_x - $x) * (p.coordenadas_x - $x) + 
                      (p.coordenadas_y - $y) * (p.coordenadas_y - $y)) as distance
            WHERE distance <= $radius
            RETURN p.id as plant_id, p.coordenadas_x as x, p.coordenadas_y as y,
                   h.nombre as hortaliza_name, distance
            ORDER BY distance
        """, {
            'x': coord_request.x,
            'y': coord_request.y,
            'radius': coord_request.radius
        })
        
        plants = []
        while result.has_next():
            row = result.get_next()
            plants.append({
                'id': row[0],
                'x': row[1],
                'y': row[2],
                'hortaliza_name': row[3],
                'distance': row[4]
            })
        
        return {"plants": plants, "count": len(plants)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching plants: {str(e)}")

@app.post("/api/check_usability")
async def check_coordinate_usability(coord_request: CoordinateRequest):
    """Check if coordinates are usable (not blocked by structures)"""
    try:
        # Get structures from TOML
        estructuras = toml_loader.get_estructuras()
        
        blocking_structures = []
        for estructura in estructuras:
            polygon = estructura.get('poligono', [])
            if is_point_in_polygon(coord_request.x, coord_request.y, polygon):
                blocking_structures.append(estructura['nombre'])
        
        is_usable = len(blocking_structures) == 0
        
        return {
            'usable': is_usable,
            'blocking_structures': blocking_structures,
            'message': 'Coordinates are usable' if is_usable else f"Blocked by: {', '.join(blocking_structures)}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking usability: {str(e)}")

@app.get("/api/structures")
async def get_structures():
    """Get all garden structures"""
    try:
        estructuras = toml_loader.get_estructuras()
        return {"success": True, "structures": estructuras}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving structures: {str(e)}")

@app.post("/api/connect_db")
async def connect_database():
    """Connect to the database (alias for initialize_db)"""
    try:
        if kuzu_manager.connect():
            db_status['connected'] = True
            db_status['message'] = 'Database connected successfully'
            return {"success": True, "message": "Database connected successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to connect to database")
    except Exception as e:
        db_status['connected'] = False
        db_status['message'] = f'Error connecting to database: {str(e)}'
        raise HTTPException(status_code=500, detail=f"Error connecting to database: {str(e)}")

@app.get("/api/check_coordinates")
async def check_coordinates(x: float, y: float):
    """Check if coordinates are usable (alias for check_usability)"""
    try:
        coord_request = CoordinateRequest(x=x, y=y)
        result = await check_coordinate_usability(coord_request)
        
        return {
            "success": True,
            "usable": result["usable"],
            "message": result["message"],
            "blocking_structures": result.get("blocking_structures", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking coordinates: {str(e)}")

@app.post("/api/remove_plant")
async def remove_plant(request: dict):
    """Remove a plant (wrapper for DELETE endpoint)"""
    try:
        plant_id = request.get("plant_id")
        if not plant_id:
            raise HTTPException(status_code=400, detail="plant_id is required")
        
        result = await delete_plant(plant_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing plant: {str(e)}")

@app.get("/api/garden_stats")
async def get_garden_stats():
    """Get garden statistics"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Get plant count
        plant_result = conn.execute("MATCH (p:Planta) RETURN count(p) as plant_count")
        plant_count = 0
        if plant_result.has_next():
            plant_count = plant_result.get_next()[0]
        
        # Get vegetable types count
        vegetable_result = conn.execute("MATCH (h:Hortaliza) RETURN count(h) as vegetable_count")
        vegetable_count = 0
        if vegetable_result.has_next():
            vegetable_count = vegetable_result.get_next()[0]
        
        # Get annotation count
        annotation_result = conn.execute("MATCH (a:Anotation) RETURN count(a) as annotation_count")
        annotation_count = 0
        if annotation_result.has_next():
            annotation_count = annotation_result.get_next()[0]
        
        return {
            "success": True,
            "stats": {
                "plants": plant_count,
                "vegetable_types": vegetable_count,
                "annotations": annotation_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving garden stats: {str(e)}")

# Add missing endpoints for garden-gui.js
@app.post("/api/add_annotation")
async def add_annotation(annotation: AnnotationCreateRequestAlt):
    """Add a new annotation (alternative endpoint for garden-gui.js)"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Generate unique annotation ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = random.randint(1000, 9999)
        annotation_id = f"annotation_{timestamp}_{random_suffix}"
        
        # Create annotation
        conn.execute("""
            CREATE (a:Anotation {
                id: $id,
                tipo: $tipo,
                comentario: $comentario,
                fecha: $fecha
            })
        """, {
            'id': annotation_id,
            'tipo': annotation.type,
            'comentario': annotation.content,
            'fecha': datetime.now()
        })
        
        # Create relationship based on target type
        if annotation.target_type == 'plant' and annotation.target_id:
            conn.execute("""
                MATCH (a:Anotation {id: $annotation_id}), (p:Planta {id: $target_id})
                CREATE (p)-[:HAS_ANOTATION {fecha_relacion: $fecha}]->(a)
            """, {
                'annotation_id': annotation_id,
                'target_id': annotation.target_id,
                'fecha': datetime.now()
            })
        elif annotation.target_type == 'garden':
            # Default to relating with the default garden
            conn.execute("""
                MATCH (a:Anotation {id: $annotation_id}), (hu:Huerta {id: "huerta_principal"})
                CREATE (hu)-[:HAS_ANOTATION_HUERTA {fecha_relacion: $fecha}]->(a)
            """, {
                'annotation_id': annotation_id,
                'fecha': datetime.now()
            })
        
        return {"success": True, "annotation_id": annotation_id, "message": "Annotation added successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding annotation: {str(e)}")

@app.post("/api/reset_db")
async def reset_database():
    """Reset the database (reinitialize)"""
    try:
        # Remove old database if exists
        import shutil
        if os.path.exists("database/garden.kuzu"):
            if os.path.isfile("database/garden.kuzu"):
                os.remove("database/garden.kuzu")
            elif os.path.isdir("database/garden.kuzu"):
                shutil.rmtree("database/garden.kuzu")
        
        # Initialize database
        kuzu_manager.initialize_database()
        
        # Update status
        db_status['connected'] = True
        db_status['message'] = 'Database reset successfully'
        
        return {"success": True, "message": "Database reset successfully"}
        
    except Exception as e:
        db_status['connected'] = False
        db_status['message'] = f'Error resetting database: {str(e)}'
        raise HTTPException(status_code=500, detail=f"Error resetting database: {str(e)}")

@app.post("/api/initialize")
async def initialize_database_alt():
    """Initialize the database (alias for initialize_db)"""
    return await initialize_database()

if __name__ == "__main__":
    import uvicorn
    print("🌱 Starting The Garden FastAPI GUI...")
    print("Access it at: http://localhost:5002")
    print("API docs at: http://localhost:5002/docs")
    uvicorn.run(app, host="0.0.0.0", port=5002)