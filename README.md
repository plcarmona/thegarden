# The Garden - Database Tool 🌱

A command-line interface for interacting with a KuzuDB graph database designed for garden management, with TOML-based configuration.

## Overview

This project provides a CLI tool to:
- Initialize a KuzuDB graph database with garden/plant data loaded from TOML configuration
- Execute interactive Cypher queries
- Search plants by coordinates
- Manage garden structures and unusable areas
- Display database information and statistics

## Features

- **TOML Configuration**: Load vegetable (hortalizas) data from `config/hortalizas.toml` instead of hardcoded values
- **Garden Structures**: Define and manage unusable areas in the garden using polygon shapes
- **Database Management**: Initialize KuzuDB with schema and TOML-based data
- **Interactive Queries**: Execute Cypher queries directly from the command line
- **Coordinate Search**: Find plants near specific coordinates using geometric queries
- **Usability Checking**: Determine if coordinates are suitable for planting (not blocked by structures)
- **Database Statistics**: View database information and list all plants and structures

## Requirements

- Python 3.9+
- KuzuDB (automatically installed)
- TOML parsing library (automatically installed)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/plcarmona/thegarden.git
cd thegarden
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main application:
```bash
python main.py
```

This will present you with a menu:
```
🌱 The Garden - Database Tool
========================================

🌿 Choose an option:
1. Initialize database
2. Query database
3. Search plants by coordinates
4. Show database info
5. Show garden structures
6. Check coordinate usability
7. Reload TOML configuration
8. Exit
```

### 1. Initialize Database
Creates a fresh KuzuDB database with:
- Plant and Garden node tables
- Structure (unusable area) polygons
- Vegetables loaded from `config/hortalizas.toml`
- Sample plants with relationships

### 2. Query Database
Interactive Cypher query interface. Examples:
- `MATCH (p:Planta) RETURN p.id, p.coordenadas_x, p.coordenadas_y`
- `MATCH (h:Hortaliza) RETURN h.nombre, h.descripcion`
- `MATCH (e:Estructura) RETURN e.nombre, e.tipo`

### 3. Search Plants by Coordinates
Search for plants near specific coordinates:
- Enter X and Y coordinates
- Specify search radius
- Get distance-ordered results

### 4. Show Database Info
Display:
- Database location and status
- Plant, garden, vegetable, and structure counts
- List of all plants with coordinates
- List of all structures

### 5. Show Garden Structures
Display all defined structures (unusable areas):
- Structure name, type, and description
- Polygon vertex information
- Creation timestamps

### 6. Check Coordinate Usability
Check if specific coordinates are suitable for planting:
- Enter X and Y coordinates
- System checks if point intersects with any structure polygons
- Returns usability status and conflicting structures

### 7. Reload TOML Configuration
Reload the TOML configuration file:
- Refreshes vegetable and structure definitions
- Option to reinitialize database with new data

## TOML Configuration

The system uses `config/hortalizas.toml` to define:

### Vegetables (Hortalizas)
```toml
[[hortalizas]]
id = 1
nombre = "Tomate"
descripcion = "Solanum lycopersicum - Hortaliza de fruto muy popular"
ciclo_dias = 120
siembra_mes_inicio = 9
siembra_mes_fin = 11
plagas_comunes = ["Trips", "Mosca blanca", "Pulgones"]
cuidados = ["Riego regular", "Tutoreo", "Poda de brotes laterales"]
tamano_promedio = 1.5
distancia_min = 0.6
```

### Garden Structures (Unusable Areas)
```toml
[[estructuras.estructura]]
id = "structure_001"
nombre = "Casa de Herramientas"
tipo = "edificio"
descripcion = "Pequeña caseta para almacenar herramientas"
# Polygon coordinates (clockwise from top-left)
poligono = [
    [50.0, 50.0],   # top-left
    [150.0, 50.0],  # top-right
    [150.0, 120.0], # bottom-right
    [50.0, 120.0]   # bottom-left
]
```

## Database Schema

The schema includes:

### Node Tables
- **Hortaliza**: Vegetable types (loaded from TOML)
- **Planta**: Individual plant instances
- **Huerta**: Garden information
- **Anotation**: Notes and observations
- **Estructura**: Garden structures/unusable areas (loaded from TOML)

### Relationship Tables
- **IS_OF_TYPE**: Plant → Vegetable type
- **PART_OF**: Plant → Garden
- **HAS_ANOTATION**: Plant → Annotation
- **HAS_ANOTATION_HUERTA**: Garden → Annotation
- **HAS_ANOTATION_HORTALIZA**: Vegetable → Annotation
- **BLOCKS_AREA**: Structure → Garden

## Sample Data

The system comes with sample data loaded from TOML:
- **5 vegetable types**: Tomate, Lechuga, Zanahoria, Pimiento, Espinaca
- **3 sample structures**: Casa de Herramientas, Camino Principal, Área Rocosa
- **Sample plants** with coordinates and relationships

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

Tests include:
- KuzuDB manager functionality
- TOML configuration loading and validation
- Point-in-polygon calculations for structures
- Database query safety and error handling

## Configuration Management

- Modify `config/hortalizas.toml` to add/edit vegetables and structures
- Use option 7 in the CLI to reload configuration without restarting
- Structure polygons use point-in-polygon detection for usability checking

## Development

The codebase is structured as:
- `main.py`: CLI interface with new structure management options
- `database/kuzu_manager.py`: KuzuDB connection and TOML-based data loading
- `database/toml_loader.py`: TOML configuration parsing and validation
- `config/hortalizas.toml`: Vegetable and structure definitions
- `database/schemas/`: Database schema definitions (updated for structures)
- `database/seeds/`: Basic data (gardens, plants, annotations)
- `tests/`: Test suite including TOML and structure tests

## License

This project is for educational and demonstration purposes.