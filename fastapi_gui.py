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

class AnnotationCreateRequest(BaseModel):
    tipo: str
    comentario: str
    entity_type: str  # 'planta', 'huerta', or 'hortaliza'
    entity_id: str

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
                   h.id as hortaliza_id, h.nombre as hortaliza_name
        """)
        
        plants = []
        while result.has_next():
            row = result.get_next()
            plants.append({
                'id': row[0],
                'x': row[1],
                'y': row[2],
                'hortaliza_id': row[3],
                'hortaliza_name': row[4]
            })
        
        return plants
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving plants: {str(e)}")

@app.get("/api/hortalizas")
async def get_hortalizas():
    """Get all vegetable types"""
    try:
        hortalizas = toml_loader.get_hortalizas()
        return hortalizas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving hortalizas: {str(e)}")

@app.post("/api/plants")
async def create_plant(plant: PlantCreateRequest):
    """Create a new plant"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Generate plant ID
        plant_id = f"plant_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
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
            'x': plant.coordenadas_x,
            'y': plant.coordenadas_y
        })
        
        # Create relationship with hortaliza
        conn.execute("""
            MATCH (p:Planta {id: $plant_id}), (h:Hortaliza {id: $hortaliza_id})
            CREATE (p)-[:IS_OF_TYPE {fecha_relacion: $fecha}]->(h)
        """, {
            'plant_id': plant_id,
            'hortaliza_id': plant.hortaliza_id,
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
        
        return {"success": True, "plant_id": plant_id, "message": "Plant created successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating plant: {str(e)}")

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
                'tipo': row[1],
                'comentario': row[2],
                'fecha': row[3].isoformat() if row[3] else None
            })
        
        return annotations
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving annotations: {str(e)}")

@app.post("/api/annotations")
async def create_annotation(annotation: AnnotationCreateRequest):
    """Create a new annotation"""
    try:
        conn = kuzu_manager.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Generate annotation ID
        annotation_id = f"annotation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
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
            if kuzu_manager.is_point_in_polygon(coord_request.x, coord_request.y, polygon):
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
        return estructuras
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving structures: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🌱 Starting The Garden FastAPI GUI...")
    print("Access it at: http://localhost:5002")
    print("API docs at: http://localhost:5002/docs")
    uvicorn.run(app, host="0.0.0.0", port=5002)