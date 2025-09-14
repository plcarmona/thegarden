#!/usr/bin/env python3
"""
The Garden - GUI Application
Graphical interface for managing garden plants and database
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
from datetime import datetime
from database.kuzu_manager import kuzu_manager
from database.toml_loader import toml_loader


class GardenGUI:
    """Main GUI application for The Garden"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("The Garden - Plant Management 🌱")
        self.root.geometry("800x600")
        
        # Database status
        self.db_connected = False
        self.plants_data = []
        self.hortalizas_data = {}
        
        self.setup_ui()
        self.load_hortalizas()
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🌱 The Garden - Plant Management", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Database status frame
        db_frame = ttk.LabelFrame(main_frame, text="Database Status", padding="10")
        db_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Database status indicator
        self.db_status_label = ttk.Label(db_frame, text="❌ Not connected", 
                                        font=("Arial", 10))
        self.db_status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Database buttons
        self.init_db_btn = ttk.Button(db_frame, text="Initialize Database", 
                                     command=self.initialize_database)
        self.init_db_btn.grid(row=0, column=1, padx=(20, 10))
        
        self.connect_db_btn = ttk.Button(db_frame, text="Connect to Database", 
                                        command=self.connect_database)
        self.connect_db_btn.grid(row=0, column=2, padx=10)
        
        # Main content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left panel - Plant list
        left_frame = ttk.LabelFrame(content_frame, text="Current Plants", padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        # Plants treeview
        self.plants_tree = ttk.Treeview(left_frame, columns=("type", "x", "y", "date"), 
                                       show="tree headings", height=15)
        self.plants_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Treeview headings
        self.plants_tree.heading("#0", text="Plant ID")
        self.plants_tree.heading("type", text="Type")
        self.plants_tree.heading("x", text="X")
        self.plants_tree.heading("y", text="Y")
        self.plants_tree.heading("date", text="Planted")
        
        # Column widths
        self.plants_tree.column("#0", width=100)
        self.plants_tree.column("type", width=100)
        self.plants_tree.column("x", width=60)
        self.plants_tree.column("y", width=60)
        self.plants_tree.column("date", width=80)
        
        # Scrollbar for plants tree
        plants_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, 
                                     command=self.plants_tree.yview)
        plants_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.plants_tree.configure(yscrollcommand=plants_scroll.set)
        
        # Plant actions frame
        plant_actions_frame = ttk.Frame(left_frame)
        plant_actions_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        self.remove_plant_btn = ttk.Button(plant_actions_frame, text="Remove Selected Plant", 
                                          command=self.remove_plant, state="disabled")
        self.remove_plant_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.refresh_plants_btn = ttk.Button(plant_actions_frame, text="Refresh Plants", 
                                           command=self.load_plants)
        self.refresh_plants_btn.pack(side=tk.LEFT)
        
        # Right panel - Add plant
        right_frame = ttk.LabelFrame(content_frame, text="Add New Plant", padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Add plant form
        ttk.Label(right_frame, text="Plant Type:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.plant_type_var = tk.StringVar()
        self.plant_type_combo = ttk.Combobox(right_frame, textvariable=self.plant_type_var, 
                                           state="readonly", width=20)
        self.plant_type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(right_frame, text="X Coordinate:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.x_coord_var = tk.StringVar()
        self.x_coord_entry = ttk.Entry(right_frame, textvariable=self.x_coord_var, width=20)
        self.x_coord_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(right_frame, text="Y Coordinate:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.y_coord_var = tk.StringVar()
        self.y_coord_entry = ttk.Entry(right_frame, textvariable=self.y_coord_var, width=20)
        self.y_coord_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Add plant button
        self.add_plant_btn = ttk.Button(right_frame, text="Add Plant", 
                                       command=self.add_plant, state="disabled")
        self.add_plant_btn.grid(row=3, column=0, columnspan=2, pady=(20, 10))
        
        # Coordinate validation
        ttk.Label(right_frame, text="Coordinate Check:", font=("Arial", 10, "bold")).grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=(20, 5))
        
        self.check_coords_btn = ttk.Button(right_frame, text="Check Usability", 
                                         command=self.check_coordinates, state="disabled")
        self.check_coords_btn.grid(row=5, column=0, columnspan=2, pady=(0, 5))
        
        self.coord_status_label = ttk.Label(right_frame, text="Enter coordinates to check", 
                                           font=("Arial", 9), foreground="gray")
        self.coord_status_label.grid(row=6, column=0, columnspan=2, sticky=tk.W)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Initialize database to get started.")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Bind treeview selection
        self.plants_tree.bind('<<TreeviewSelect>>', self.on_plant_select)
        
        # Configure right panel grid
        right_frame.columnconfigure(1, weight=1)
    
    def load_hortalizas(self):
        """Load available hortalizas from TOML config"""
        try:
            hortalizas_config = toml_loader.get_hortalizas()
            if hortalizas_config:
                self.hortalizas_data = {h['id']: h for h in hortalizas_config}
                plant_names = [f"{h['nombre']} ({h['id']})" for h in hortalizas_config]
                self.plant_type_combo['values'] = plant_names
                self.status_var.set(f"Loaded {len(plant_names)} plant types from configuration")
            else:
                self.status_var.set("Warning: No plant types found in configuration")
        except Exception as e:
            self.status_var.set(f"Error loading plant types: {e}")
            messagebox.showerror("Configuration Error", f"Could not load plant types: {e}")
    
    def initialize_database(self):
        """Initialize the database in a separate thread"""
        def init_db():
            try:
                self.status_var.set("Initializing database...")
                self.init_db_btn.configure(state="disabled")
                
                # Remove old database
                import shutil
                import os
                if os.path.exists("database/garden.kuzu"):
                    if os.path.isfile("database/garden.kuzu"):
                        os.remove("database/garden.kuzu")
                    else:
                        shutil.rmtree("database/garden.kuzu")
                
                # Connect and initialize
                conn = kuzu_manager.connect()
                if not conn:
                    raise Exception("Could not connect to KuzuDB")
                
                # Initialize schema and data
                schema_success = kuzu_manager.initialize_schema()
                if not schema_success:
                    raise Exception("Schema initialization failed")
                
                kuzu_manager.load_initial_data()
                kuzu_manager.close()
                
                # Update UI on main thread
                self.root.after(0, self._on_db_init_success)
                
            except Exception as e:
                error_msg = f"Database initialization failed: {e}"
                self.root.after(0, lambda: self._on_db_init_error(error_msg))
        
        # Run in separate thread to avoid blocking UI
        thread = threading.Thread(target=init_db)
        thread.daemon = True
        thread.start()
    
    def _on_db_init_success(self):
        """Handle successful database initialization"""
        self.status_var.set("Database initialized successfully!")
        self.init_db_btn.configure(state="normal")
        self.connect_database()
        messagebox.showinfo("Success", "Database has been initialized successfully!")
    
    def _on_db_init_error(self, error_msg):
        """Handle database initialization error"""
        self.status_var.set(error_msg)
        self.init_db_btn.configure(state="normal")
        messagebox.showerror("Database Error", error_msg)
    
    def connect_database(self):
        """Connect to the database"""
        try:
            if not kuzu_manager._kuzu_available:
                raise Exception("KuzuDB is not available. Please install it with: pip install kuzu")
            
            conn = kuzu_manager.connect()
            if conn:
                self.db_connected = True
                self.db_status_label.configure(text="✅ Connected", foreground="green")
                self.add_plant_btn.configure(state="normal")
                self.check_coords_btn.configure(state="normal")
                self.status_var.set("Connected to database successfully")
                self.load_plants()
            else:
                raise Exception("Failed to connect to database")
                
        except Exception as e:
            self.db_connected = False
            self.db_status_label.configure(text="❌ Connection failed", foreground="red")
            self.status_var.set(f"Database connection error: {e}")
            messagebox.showerror("Connection Error", f"Could not connect to database: {e}")
    
    def load_plants(self):
        """Load plants from database and populate the tree"""
        if not self.db_connected:
            return
        
        try:
            # Clear existing items
            for item in self.plants_tree.get_children():
                self.plants_tree.delete(item)
            
            conn = kuzu_manager.connect()
            if not conn:
                raise Exception("Could not connect to database")
            
            # Query all plants
            result = kuzu_manager.execute_query("""
                MATCH (p:Planta)-[:IS_OF_TYPE]->(h:Hortaliza)
                RETURN p.id, h.nombre, p.coordenadas_x, p.coordenadas_y, p.fecha_siembra
                ORDER BY p.id
            """)
            
            plants_count = 0
            if result and result.has_next():
                while result.has_next():
                    row = result.get_next()
                    plant_id = row[0]
                    plant_type = row[1]
                    x_coord = row[2]
                    y_coord = row[3]
                    plant_date = row[4] if row[4] else "Unknown"
                    
                    # Format date for display
                    date_display = plant_date
                    if isinstance(plant_date, datetime):
                        date_display = plant_date.strftime("%Y-%m-%d")
                    
                    # Insert into tree
                    self.plants_tree.insert("", "end", text=plant_id,
                                          values=(plant_type, x_coord, y_coord, date_display))
                    plants_count += 1
            
            kuzu_manager.close()
            self.status_var.set(f"Loaded {plants_count} plants from database")
            
        except Exception as e:
            self.status_var.set(f"Error loading plants: {e}")
            messagebox.showerror("Database Error", f"Could not load plants: {e}")
    
    def add_plant(self):
        """Add a new plant to the database"""
        if not self.db_connected:
            messagebox.showerror("Error", "Please connect to database first")
            return
        
        try:
            # Validate inputs
            plant_type_str = self.plant_type_var.get().strip()
            x_str = self.x_coord_var.get().strip()
            y_str = self.y_coord_var.get().strip()
            
            if not plant_type_str:
                messagebox.showerror("Error", "Please select a plant type")
                return
            
            if not x_str or not y_str:
                messagebox.showerror("Error", "Please enter both X and Y coordinates")
                return
            
            try:
                x_coord = float(x_str)
                y_coord = float(y_str)
            except ValueError:
                messagebox.showerror("Error", "Coordinates must be valid numbers")
                return
            
            # Extract plant type ID
            plant_type_id = int(plant_type_str.split("(")[-1].split(")")[0])
            hortaliza_name = self.hortalizas_data[plant_type_id]['nombre']
            
            # Generate unique plant ID
            plant_id = f"{hortaliza_name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Check coordinate usability first
            conn = kuzu_manager.connect()
            if not conn:
                raise Exception("Could not connect to database")
            
            intersecting = kuzu_manager.check_coordinate_in_structure(x_coord, y_coord)
            if intersecting:
                structure_names = [s['nombre'] for s in intersecting]
                response = messagebox.askywarning(
                    "Coordinate Warning",
                    f"The coordinates ({x_coord}, {y_coord}) intersect with structures:\n" +
                    "\n".join(f"• {name}" for name in structure_names) +
                    "\n\nDo you want to continue anyway?",
                    default="no"
                )
                if response != "yes":
                    kuzu_manager.close()
                    return
            
            # Create the plant
            create_plant_query = """
            CREATE (p:Planta {
                id: $id,
                fecha_siembra: $fecha_siembra,
                coordenadas_x: $coordenadas_x,
                coordenadas_y: $coordenadas_y,
                estado: $estado
            })
            """
            
            kuzu_manager.execute_query(create_plant_query, {
                'id': plant_id,
                'fecha_siembra': datetime.now(),
                'coordenadas_x': x_coord,
                'coordenadas_y': y_coord,
                'estado': 'activo'
            })
            
            # Create relationship with hortaliza
            relate_query = """
            MATCH (p:Planta {id: $planta_id}), (h:Hortaliza {id: $hortaliza_id})
            CREATE (p)-[:IS_OF_TYPE {fecha_relacion: $fecha}]->(h)
            """
            
            kuzu_manager.execute_query(relate_query, {
                'planta_id': plant_id,
                'hortaliza_id': plant_type_id,
                'fecha': datetime.now()
            })
            
            kuzu_manager.close()
            
            # Clear form and refresh
            self.plant_type_var.set("")
            self.x_coord_var.set("")
            self.y_coord_var.set("")
            self.coord_status_label.configure(text="Enter coordinates to check", foreground="gray")
            
            self.load_plants()
            self.status_var.set(f"Plant {plant_id} added successfully!")
            messagebox.showinfo("Success", f"Plant {plant_id} has been added to the garden!")
            
        except Exception as e:
            self.status_var.set(f"Error adding plant: {e}")
            messagebox.showerror("Error", f"Could not add plant: {e}")
    
    def remove_plant(self):
        """Remove selected plant from database"""
        if not self.db_connected:
            messagebox.showerror("Error", "Please connect to database first")
            return
        
        selected = self.plants_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a plant to remove")
            return
        
        try:
            plant_item = selected[0]
            plant_id = self.plants_tree.item(plant_item, 'text')
            plant_type = self.plants_tree.item(plant_item, 'values')[0]
            
            # Confirm removal
            response = messagebox.askyesno(
                "Confirm Removal",
                f"Are you sure you want to remove plant '{plant_id}' ({plant_type})?\n\n"
                "This action cannot be undone."
            )
            
            if not response:
                return
            
            conn = kuzu_manager.connect()
            if not conn:
                raise Exception("Could not connect to database")
            
            # Remove plant and all its relationships
            remove_query = """
            MATCH (p:Planta {id: $plant_id})
            DETACH DELETE p
            """
            
            kuzu_manager.execute_query(remove_query, {'plant_id': plant_id})
            kuzu_manager.close()
            
            self.load_plants()
            self.status_var.set(f"Plant {plant_id} removed successfully")
            messagebox.showinfo("Success", f"Plant {plant_id} has been removed from the garden")
            
        except Exception as e:
            self.status_var.set(f"Error removing plant: {e}")
            messagebox.showerror("Error", f"Could not remove plant: {e}")
    
    def check_coordinates(self):
        """Check if coordinates are usable for planting"""
        try:
            x_str = self.x_coord_var.get().strip()
            y_str = self.y_coord_var.get().strip()
            
            if not x_str or not y_str:
                self.coord_status_label.configure(text="Enter both coordinates", foreground="orange")
                return
            
            try:
                x_coord = float(x_str)
                y_coord = float(y_str)
            except ValueError:
                self.coord_status_label.configure(text="Invalid coordinates", foreground="red")
                return
            
            if not self.db_connected:
                self.coord_status_label.configure(text="Database not connected", foreground="red")
                return
            
            conn = kuzu_manager.connect()
            if not conn:
                raise Exception("Could not connect to database")
            
            intersecting = kuzu_manager.check_coordinate_in_structure(x_coord, y_coord)
            kuzu_manager.close()
            
            if intersecting:
                structure_names = [s['nombre'] for s in intersecting]
                status_text = f"❌ Blocked by: {', '.join(structure_names)}"
                self.coord_status_label.configure(text=status_text, foreground="red")
            else:
                self.coord_status_label.configure(text="✅ Coordinates are usable", foreground="green")
                
        except Exception as e:
            self.coord_status_label.configure(text=f"Error checking: {str(e)[:30]}...", foreground="red")
    
    def on_plant_select(self, event):
        """Handle plant selection in tree"""
        selected = self.plants_tree.selection()
        if selected:
            self.remove_plant_btn.configure(state="normal")
        else:
            self.remove_plant_btn.configure(state="disabled")


def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = GardenGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()