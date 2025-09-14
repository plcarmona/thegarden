# The Garden - GUI Interface 🌱

This document describes the GUI implementation for The Garden plant management system.

## GUI Options

The Garden provides two GUI interfaces:

### 1. **Web GUI** (Recommended)
- Works everywhere (desktop, laptop, server, mobile)
- Modern responsive web interface
- No display requirements
- Access via web browser at `http://localhost:5001`

### 2. **Desktop GUI** (Tkinter)
- Native desktop application
- Requires desktop environment with display
- Traditional desktop application feel
- Falls back gracefully in headless environments

Both interfaces provide identical functionality - choose based on your environment and preferences.

## GUI Features

### ✅ Core Requirements Met:
- **Load Database**: Initialize and connect to KuzuDB database with schema and sample data
- **Add Plants**: Add new plants to the garden with coordinate validation
- **Remove Plants**: Remove existing plants from the garden

### 🌟 Additional Features:
- **Plant Type Selection**: Choose from 5 pre-configured plant types (Tomate, Lechuga, Zanahoria, Pimiento, Espinaca)
- **Coordinate Validation**: Check if planting coordinates conflict with garden structures
- **Garden Statistics**: View real-time statistics about plants, structures, and garden data
- **Responsive Design**: Modern web interface that works on desktop and mobile
- **Real-time Updates**: Dynamic loading and updating of plant data
- **Error Handling**: User-friendly error messages and confirmations

## Files Created

### Web GUI Implementation:
- **`web_gui.py`**: Flask web server with REST API endpoints (✅ Fixed template configuration)
- **`templates/index.html`**: Complete web interface with HTML, CSS, and JavaScript  
- **`gui/index.html`**: Alternative GUI interface template

### Desktop GUI Implementation:
- **`gui.py`**: Desktop GUI using tkinter with improved error handling
- **`launcher.py`**: Interactive launcher for choosing between interfaces

### Test and Demo Scripts:
- **`test_gui.py`**: Tests GUI functionality and dependencies
- **`demo_gui.py`**: Demonstrates all GUI features programmatically

## How to Use

### 1. Install Dependencies
```bash
cd /path/to/thegarden
pip install -r requirements.txt
```

### 2. Choose Interface

**Option A: Use the Launcher (Recommended)**
```bash
python launcher.py
```
Then select from the menu:
1. Web GUI (works everywhere)
2. Desktop GUI (tkinter - requires desktop environment)
3. Command Line Interface

**Option B: Run Interfaces Directly**

**Web GUI** (Recommended - works everywhere):
```bash
python web_gui.py
```

**Desktop GUI** (tkinter - requires desktop environment):
```bash
python gui.py
```

### 3. Open Browser
Navigate to: `http://localhost:5001`

### 4. Use the Interface

#### Initialize Database:
1. Click "Initialize Database" to create fresh KuzuDB instance
2. Wait for success message and status to show "✅ Connected"

#### View Current Plants:
- Plants automatically load when database connects
- Table shows Plant ID, Type, Coordinates, and Planting Date
- Click "Refresh Plants" to reload data

#### Add New Plant:
1. Select plant type from dropdown (loaded from TOML config)
2. Enter X and Y coordinates
3. Optional: Click "Check Coordinates" to validate usability
4. Click "Add Plant" to create new plant in database
5. System validates coordinates against garden structures
6. Confirmation required if coordinates conflict with structures

#### Remove Plant:
1. Click on a plant row in the table to select it
2. Click "Remove Selected" button
3. Confirm removal in popup dialog

#### View Statistics:
- Garden statistics automatically load and show:
  - Total number of plants
  - Number of plant types available
  - Number of garden structures
  - Other database statistics

## Architecture

### Backend (Flask + REST API):
- **`/`**: Main GUI interface
- **`/api/db_status`**: Database connection status  
- **`/api/initialize_db`**: Initialize database
- **`/api/connect_db`**: Connect to existing database
- **`/api/plants`**: Get/manage plants
- **`/api/hortalizas`**: Get available plant types
- **`/api/add_plant`**: Add new plant
- **`/api/remove_plant`**: Remove plant
- **`/api/check_coordinates`**: Validate coordinates
- **`/api/garden_stats`**: Get garden statistics

### Frontend (HTML + CSS + JavaScript):
- Modern responsive design using CSS Grid and Flexbox
- Real-time AJAX communication with backend
- Interactive plant selection and management
- Visual feedback for coordinate validation
- Confirmation dialogs for destructive actions

### Integration:
- Uses existing `database/kuzu_manager.py` backend
- Loads plant types from `config/hortalizas.toml`
- Maintains compatibility with original CLI interface

## Testing

### Run Functionality Test:
```bash
python test_gui.py
```

### Run Demo:
```bash
python demo_gui.py
```

### Test Original CLI:
```bash
python main.py
```

## Key Benefits

1. **User-Friendly**: No command-line knowledge required
2. **Visual**: Clear interface with real-time feedback
3. **Safe**: Coordinate validation prevents conflicts
4. **Complete**: All requested functionality implemented
5. **Extensible**: Web-based architecture allows future enhancements
6. **Compatible**: Original CLI functionality preserved

## Technical Details

- **Backend**: Flask 3.0+ with Python 3.9+
- **Database**: KuzuDB graph database
- **Configuration**: TOML-based plant and structure definitions  
- **Frontend**: Vanilla HTML/CSS/JavaScript (no external dependencies)
- **Architecture**: REST API with responsive web interface

The GUI successfully provides all requested functionality:
✅ Load database  
✅ Add plants to garden  
✅ Remove plants from garden

Plus additional features that enhance the user experience and provide a complete garden management solution.