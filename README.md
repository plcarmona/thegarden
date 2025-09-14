# The Garden - Database Tool 🌱

A simplified command-line interface for interacting with a KuzuDB graph database designed for garden management.

## Overview

This project has been simplified to focus on the core database functionality. It provides a CLI tool to:
- Initialize a KuzuDB graph database with garden/plant data
- Execute interactive Cypher queries
- Search plants by coordinates
- Display database information and statistics

## Features

- **Database Management**: Initialize KuzuDB with schema and sample data
- **Interactive Queries**: Execute Cypher queries directly from the command line
- **Coordinate Search**: Find plants near specific coordinates using geometric queries
- **Database Statistics**: View database information and list all plants

## Requirements

- Python 3.9+
- KuzuDB (automatically installed)

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
5. Exit
```

### 1. Initialize Database
Creates a fresh KuzuDB database with:
- Plant and Garden node tables
- Sample plants (Tomato, Lettuce, Carrot)
- A main garden with relationships

### 2. Query Database
Interactive Cypher query interface. Examples:
- `MATCH (p:Plant) RETURN p.name, p.x, p.y`
- `MATCH (p:Plant) RETURN count(p)`
- `MATCH (p:Plant)-[:GROWS_IN]->(g:Garden) RETURN p.name, g.name`

### 3. Search Plants by Coordinates
Search for plants near specific coordinates:
- Enter X and Y coordinates
- Specify search radius
- Get distance-ordered results

### 4. Show Database Info
Display:
- Database location and status
- Plant and garden counts
- List of all plants with coordinates

## Database Schema

The simplified schema includes:

### Node Tables
- **Plant**: id, name, x, y (coordinates)
- **Garden**: id, name, width, height

### Relationship Tables
- **GROWS_IN**: Plant → Garden

## Sample Data

The database comes with sample data:
- **Tomato Plant** at (100.0, 100.0)
- **Lettuce Plant** at (200.0, 150.0)  
- **Carrot Plant** at (150.0, 200.0)
- **My Garden** (800x600 units)

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

Tests include:
- KuzuDB manager creation and connection
- Compatibility mode (graceful handling when KuzuDB unavailable)
- Query safety and error handling
- Schema file validation

## Development

The codebase is structured as:
- `main.py`: CLI interface
- `database/kuzu_manager.py`: KuzuDB connection and query management
- `database/schemas/`: Database schema definitions
- `database/seeds/`: Sample data
- `tests/`: Test suite

## Previous Functionality

This project was originally a full web application with FastAPI, but has been simplified to focus on the database layer as requested. The web interface, REST APIs, weather integration, and calendar features have been removed to create a focused database interaction tool.

## License

This project is for educational and demonstration purposes.