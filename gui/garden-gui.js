/**
 * Garden GUI - Canvas and Interaction Management
 * Handles visualization and interaction with the garden database
 */

class GardenGUI {
    constructor() {
        this.canvas = document.getElementById('gardenCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.scale = 1;
        this.offsetX = 0;
        this.offsetY = 0;
        this.isDragging = false;
        this.lastMouseX = 0;
        this.lastMouseY = 0;
        this.selectedPlant = null;
        
        // Data storage
        this.plants = [];
        this.annotations = [];
        this.structures = [];
        this.vegetables = [];
        
        // UI state
        this.currentTool = 'select'; // select, add-plant, add-annotation
        
        this.setupCanvas();
        this.setupEventListeners();
        this.loadAvailableVegetables();
        this.render();
    }

    setupCanvas() {
        // Make canvas responsive
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    resizeCanvas() {
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();
        
        // Set canvas size accounting for padding/margins
        this.canvas.width = rect.width - 20;
        this.canvas.height = rect.height - 20;
        
        this.render();
    }

    setupEventListeners() {
        // Mouse events for canvas interaction
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        this.canvas.addEventListener('wheel', (e) => this.handleWheel(e));
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
        
        // Form submissions
        document.getElementById('addPlantForm').addEventListener('submit', (e) => this.handleAddPlant(e));
        document.getElementById('addAnnotationForm').addEventListener('submit', (e) => this.handleAddAnnotation(e));
        
        // Prevent context menu on canvas
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    }

    getCanvasCoordinates(e) {
        const rect = this.canvas.getBoundingClientRect();
        const canvasX = e.clientX - rect.left;
        const canvasY = e.clientY - rect.top;
        
        // Convert to world coordinates
        const worldX = (canvasX - this.offsetX) / this.scale;
        const worldY = (canvasY - this.offsetY) / this.scale;
        
        return { canvasX, canvasY, worldX, worldY };
    }

    handleMouseMove(e) {
        const coords = this.getCanvasCoordinates(e);
        
        // Update coordinates display
        document.getElementById('coordinates').textContent = 
            `Mouse: (${coords.worldX.toFixed(1)}, ${coords.worldY.toFixed(1)})`;
        
        // Handle dragging/panning
        if (this.isDragging) {
            const deltaX = e.clientX - this.lastMouseX;
            const deltaY = e.clientY - this.lastMouseY;
            
            this.offsetX += deltaX;
            this.offsetY += deltaY;
            
            this.lastMouseX = e.clientX;
            this.lastMouseY = e.clientY;
            
            this.render();
        }
        
        // Highlight plants under mouse
        this.updateHover(coords.worldX, coords.worldY);
    }

    handleMouseDown(e) {
        if (e.button === 1 || (e.button === 0 && e.ctrlKey)) { // Middle click or Ctrl+click for panning
            this.isDragging = true;
            this.lastMouseX = e.clientX;
            this.lastMouseY = e.clientY;
            this.canvas.style.cursor = 'grabbing';
            e.preventDefault();
        }
    }

    handleMouseUp(e) {
        if (this.isDragging) {
            this.isDragging = false;
            this.canvas.style.cursor = 'crosshair';
        }
    }

    handleWheel(e) {
        e.preventDefault();
        
        const coords = this.getCanvasCoordinates(e);
        const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
        
        // Zoom towards mouse position
        this.offsetX = coords.canvasX - (coords.canvasX - this.offsetX) * zoomFactor;
        this.offsetY = coords.canvasY - (coords.canvasY - this.offsetY) * zoomFactor;
        this.scale *= zoomFactor;
        
        // Limit zoom
        this.scale = Math.max(0.1, Math.min(5, this.scale));
        
        this.render();
    }

    handleClick(e) {
        if (this.isDragging) return;
        
        const coords = this.getCanvasCoordinates(e);
        
        if (this.currentTool === 'add-plant') {
            // Quick add plant mode
            document.getElementById('plantX').value = coords.worldX.toFixed(1);
            document.getElementById('plantY').value = coords.worldY.toFixed(1);
            showAddPlantModal();
        } else if (this.currentTool === 'add-annotation') {
            // Quick add annotation mode - would need implementation
            document.getElementById('annotationTitle').value = `Annotation at (${coords.worldX.toFixed(1)}, ${coords.worldY.toFixed(1)})`;
            showAddAnnotationModal();
        } else {
            // Select mode - select plants
            this.selectPlantAt(coords.worldX, coords.worldY);
        }
    }

    selectPlantAt(x, y) {
        const threshold = 20 / this.scale; // 20 pixels in world coordinates
        
        for (const plant of this.plants) {
            const distance = Math.sqrt(
                Math.pow(plant.x - x, 2) + Math.pow(plant.y - y, 2)
            );
            
            if (distance <= threshold) {
                this.selectedPlant = plant;
                this.highlightPlantInSidebar(plant.id);
                this.render();
                return;
            }
        }
        
        // No plant found, deselect
        this.selectedPlant = null;
        this.render();
    }

    updateHover(x, y) {
        // This could highlight plants on hover
        // For now, just update cursor
        if (this.currentTool === 'add-plant') {
            this.canvas.style.cursor = 'crosshair';
            return;
        }
        
        const threshold = 20 / this.scale;
        let foundPlant = false;
        
        for (const plant of this.plants) {
            const distance = Math.sqrt(
                Math.pow(plant.x - x, 2) + Math.pow(plant.y - y, 2)
            );
            
            if (distance <= threshold) {
                foundPlant = true;
                break;
            }
        }
        
        this.canvas.style.cursor = foundPlant ? 'pointer' : 'default';
    }

    highlightPlantInSidebar(plantId) {
        // Remove existing highlights
        document.querySelectorAll('.plant-item').forEach(item => {
            item.style.background = '#f8f9fa';
            item.style.borderColor = '#bdc3c7';
        });
        
        // Highlight selected plant
        const plantElement = document.getElementById(`plant-${plantId}`);
        if (plantElement) {
            plantElement.style.background = '#e8f4fd';
            plantElement.style.borderColor = '#3498db';
            plantElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    togglePlantMode() {
        if (this.currentTool === 'add-plant') {
            // Exit plant mode
            this.currentTool = 'select';
            this.updateAddPlantButton(false);
        } else {
            // Enter plant mode
            this.currentTool = 'add-plant';
            this.updateAddPlantButton(true);
        }
        this.updateCursor();
    }

    updateAddPlantButton(isActive) {
        const button = document.querySelector('button[onclick*="togglePlantMode"]');
        if (button) {
            if (isActive) {
                button.textContent = '🎯 Click to Plant (Exit)';
                button.classList.add('active');
                button.style.background = '#e74c3c';
                button.style.color = 'white';
            } else {
                button.textContent = '➕ Add Plant';
                button.classList.remove('active');
                button.style.background = '';
                button.style.color = '';
            }
        }
    }

    updateCursor() {
        if (this.currentTool === 'add-plant') {
            this.canvas.style.cursor = 'crosshair';
        } else {
            this.canvas.style.cursor = 'default';
        }
    }

    // Rendering methods
    render() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Save context and apply transformations
        this.ctx.save();
        this.ctx.translate(this.offsetX, this.offsetY);
        this.ctx.scale(this.scale, this.scale);
        
        // Draw grid
        this.drawGrid();
        
        // Draw structures first (background)
        this.drawStructures();
        
        // Draw plants
        this.drawPlants();
        
        // Note: Annotations are now only shown in sidebar, not on canvas
        
        // Restore context
        this.ctx.restore();
        
        // Draw UI overlays (not affected by transformations)
        this.drawUI();
    }

    drawGrid() {
        const gridSize = 50;
        const startX = Math.floor(-this.offsetX / this.scale / gridSize) * gridSize;
        const startY = Math.floor(-this.offsetY / this.scale / gridSize) * gridSize;
        const endX = startX + (this.canvas.width / this.scale) + gridSize;
        const endY = startY + (this.canvas.height / this.scale) + gridSize;
        
        this.ctx.strokeStyle = '#f0f0f0';
        this.ctx.lineWidth = 0.5;
        
        // Vertical lines
        for (let x = startX; x <= endX; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, startY);
            this.ctx.lineTo(x, endY);
            this.ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = startY; y <= endY; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(startX, y);
            this.ctx.lineTo(endX, y);
            this.ctx.stroke();
        }
    }

    drawStructures() {
        for (const structure of this.structures) {
            if (!structure.polygon || structure.polygon.length < 3) continue;
            
            this.ctx.beginPath();
            this.ctx.moveTo(structure.polygon[0][0], structure.polygon[0][1]);
            
            for (let i = 1; i < structure.polygon.length; i++) {
                this.ctx.lineTo(structure.polygon[i][0], structure.polygon[i][1]);
            }
            
            this.ctx.closePath();
            
            // Fill structure
            this.ctx.fillStyle = 'rgba(231, 76, 60, 0.3)';
            this.ctx.fill();
            
            // Stroke structure
            this.ctx.strokeStyle = '#e74c3c';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            // Add label
            if (structure.polygon.length > 0) {
                const centerX = structure.polygon.reduce((sum, p) => sum + p[0], 0) / structure.polygon.length;
                const centerY = structure.polygon.reduce((sum, p) => sum + p[1], 0) / structure.polygon.length;
                
                this.ctx.fillStyle = '#2c3e50';
                this.ctx.font = `${12 / this.scale}px Arial`;
                this.ctx.textAlign = 'center';
                this.ctx.fillText(structure.name || 'Structure', centerX, centerY);
            }
        }
    }

    drawPlants() {
        for (const plant of this.plants) {
            const isSelected = this.selectedPlant && this.selectedPlant.id === plant.id;
            
            // Draw plant circle
            this.ctx.beginPath();
            this.ctx.arc(plant.x, plant.y, isSelected ? 15 : 10, 0, 2 * Math.PI);
            
            // Plant color based on type or default
            this.ctx.fillStyle = isSelected ? '#2980b9' : '#27ae60';
            this.ctx.fill();
            
            // Plant border
            this.ctx.strokeStyle = isSelected ? '#1f618d' : '#229954';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            // Plant label
            this.ctx.fillStyle = '#2c3e50';
            this.ctx.font = `${10 / this.scale}px Arial`;
            this.ctx.textAlign = 'center';
            this.ctx.fillText(
                plant.vegetable_name || `Plant ${plant.id}`,
                plant.x,
                plant.y - (isSelected ? 20 : 15)
            );
            
            // Show ID
            this.ctx.fillStyle = 'white';
            this.ctx.font = `${8 / this.scale}px Arial`;
            this.ctx.fillText(plant.id, plant.x, plant.y + 3);
        }
    }

    drawAnnotations() {
        for (const annotation of this.annotations) {
            if (!annotation.x || !annotation.y) continue;
            
            // Draw annotation marker
            this.ctx.beginPath();
            this.ctx.arc(annotation.x, annotation.y, 8, 0, 2 * Math.PI);
            this.ctx.fillStyle = '#f39c12';
            this.ctx.fill();
            this.ctx.strokeStyle = '#e67e22';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            // Annotation icon (simple text)
            this.ctx.fillStyle = 'white';
            this.ctx.font = `${10 / this.scale}px Arial`;
            this.ctx.textAlign = 'center';
            this.ctx.fillText('📝', annotation.x, annotation.y + 3);
        }
    }

    drawUI() {
        // Status information
        const status = `Plants: ${this.plants.length} | Scale: ${(this.scale * 100).toFixed(0)}%`;
        document.getElementById('statusBar').textContent = status;
    }

    // Data loading methods
    async loadAvailableVegetables() {
        try {
            const response = await fetch('/api/vegetables');
            this.vegetables = await response.json();
            
            // Populate dropdown
            const select = document.getElementById('plantType');
            select.innerHTML = '<option value="">Select plant type...</option>';
            
            for (const vegetable of this.vegetables) {
                const option = document.createElement('option');
                option.value = vegetable.id;
                option.textContent = vegetable.name;
                select.appendChild(option);
            }
        } catch (error) {
            console.warn('Could not load vegetables:', error);
            this.loadMockVegetables();
        }
    }

    loadMockVegetables() {
        // Fallback mock data
        this.vegetables = [
            { id: 1, name: 'Tomate' },
            { id: 2, name: 'Lechuga' },
            { id: 3, name: 'Zanahoria' },
            { id: 4, name: 'Pimiento' },
            { id: 5, name: 'Espinaca' }
        ];
        
        const select = document.getElementById('plantType');
        select.innerHTML = '<option value="">Select plant type...</option>';
        
        for (const vegetable of this.vegetables) {
            const option = document.createElement('option');
            option.value = vegetable.id;
            option.textContent = vegetable.name;
            select.appendChild(option);
        }
    }

    async loadDatabase() {
        showLoading(true);
        updateStatus('Loading database...');
        
        try {
            // Load all data
            const [plantsResponse, annotationsResponse, structuresResponse] = await Promise.all([
                fetch('/api/plants'),
                fetch('/api/annotations'), 
                fetch('/api/structures')
            ]);
            
            // Handle plants data
            const plantsData = await plantsResponse.json();
            if (plantsData.success) {
                this.plants = plantsData.plants.map(plant => ({
                    id: plant.id,
                    x: plant.x,
                    y: plant.y,
                    vegetable_name: plant.type,
                    planting_date: plant.date
                }));
            } else {
                console.warn('Plants API error:', plantsData.message);
                this.plants = [];
            }
            
            // Handle annotations data
            const annotationsData = await annotationsResponse.json();
            if (annotationsData.success) {
                this.annotations = annotationsData.annotations.map(annotation => ({
                    id: annotation.id,
                    title: annotation.type,
                    content: annotation.content,
                    type: annotation.type,
                    created_date: annotation.date
                }));
            } else {
                console.warn('Annotations API error:', annotationsData.message);
                this.annotations = [];
            }
            
            // Handle structures data
            const structuresData = await structuresResponse.json();
            if (structuresData.success) {
                this.structures = structuresData.structures.map(structure => ({
                    id: structure.id,
                    name: structure.name,
                    type: structure.type,
                    description: structure.description,
                    polygon: structure.polygon
                }));
            } else {
                console.warn('Structures API error:', structuresData.message);
                this.structures = [];
            }
            
            // Update UI
            this.updateSidebar();
            this.render();
            
            showNotification('Database loaded successfully!', 'success');
            updateStatus('Ready');
            
        } catch (error) {
            console.warn('Could not load from API, using mock data:', error);
            this.loadMockData();
        } finally {
            showLoading(false);
        }
    }

    loadMockData() {
        // Mock data for development
        this.plants = [
            { id: 'plant_001', x: 100, y: 150, vegetable_name: 'Tomate', planting_date: '2024-01-15' },
            { id: 'plant_002', x: 200, y: 100, vegetable_name: 'Lechuga', planting_date: '2024-01-20' },
            { id: 'plant_003', x: 150, y: 250, vegetable_name: 'Zanahoria', planting_date: '2024-02-01' }
        ];
        
        this.structures = [
            { 
                id: 'struct_001',
                name: 'Casa de Herramientas',
                polygon: [[50, 50], [150, 50], [150, 120], [50, 120]]
            },
            {
                id: 'struct_002', 
                name: 'Camino Principal',
                polygon: [[0, 200], [400, 200], [400, 220], [0, 220]]
            }
        ];
        
        this.annotations = [
            { 
                id: 'ann_001',
                title: 'Riego diario',
                content: 'Las tomateras necesitan riego diario',
                type: 'observation',
                created_date: '2024-01-16',
                x: 100,
                y: 130
            }
        ];
        
        this.updateSidebar();
        this.render();
        showNotification('Mock data loaded for development', 'success');
        updateStatus('Ready (Mock Mode)');
    }

    updateSidebar() {
        this.updatePlantsSection();
        this.updateAnnotationsSection();
        this.updateStructuresSection();
    }

    updatePlantsSection() {
        const plantsContainer = document.getElementById('plants-list');
        const plantsCount = document.getElementById('plants-count');
        
        plantsCount.textContent = `(${this.plants.length})`;
        
        if (this.plants.length === 0) {
            plantsContainer.innerHTML = '<p>No plants in database</p>';
            return;
        }
        
        plantsContainer.innerHTML = this.plants.map(plant => `
            <div class="plant-item" id="plant-${plant.id}" onclick="gardenGUI.selectPlant('${plant.id}')">
                <div style="font-weight: bold; color: #27ae60;">
                    ${plant.vegetable_name || 'Unknown Plant'}
                </div>
                <div style="font-size: 12px; color: #7f8c8d;">
                    ID: ${plant.id}
                </div>
                <div style="font-size: 12px;">
                    📍 (${plant.x}, ${plant.y})
                    ${plant.planting_date ? `🗓️ ${plant.planting_date}` : ''}
                </div>
                <button class="btn btn-danger" style="padding: 4px 8px; font-size: 12px; margin-top: 5px;" 
                        onclick="event.stopPropagation(); gardenGUI.removePlant('${plant.id}')">
                    🗑️ Remove
                </button>
            </div>
        `).join('');
    }

    updateAnnotationsSection() {
        const annotationsContainer = document.getElementById('annotations-list');
        const annotationsCount = document.getElementById('annotations-count');
        
        annotationsCount.textContent = `(${this.annotations.length})`;
        
        if (this.annotations.length === 0) {
            annotationsContainer.innerHTML = '<p>No annotations in database</p>';
            return;
        }
        
        // Sort by created_date descending (most recent first)
        const sortedAnnotations = [...this.annotations].sort((a, b) => 
            new Date(b.created_date || '2024-01-01') - new Date(a.created_date || '2024-01-01')
        );
        
        annotationsContainer.innerHTML = sortedAnnotations.map(annotation => `
            <div class="annotation-item" onclick="gardenGUI.selectAnnotation('${annotation.id}')">
                <div style="font-weight: bold; color: #f39c12;">
                    ${annotation.title}
                </div>
                <div style="font-size: 12px; color: #7f8c8d;">
                    ${annotation.type} • ${annotation.created_date || 'No date'}
                </div>
                <div style="font-size: 12px; margin-top: 5px;">
                    ${annotation.content.substring(0, 80)}${annotation.content.length > 80 ? '...' : ''}
                </div>
            </div>
        `).join('');
    }

    updateStructuresSection() {
        const structuresContainer = document.getElementById('structures-list');
        const structuresCount = document.getElementById('structures-count');
        
        structuresCount.textContent = `(${this.structures.length})`;
        
        if (this.structures.length === 0) {
            structuresContainer.innerHTML = '<p>No structures in database</p>';
            return;
        }
        
        structuresContainer.innerHTML = this.structures.map(structure => `
            <div class="plant-item">
                <div style="font-weight: bold; color: #e74c3c;">
                    ${structure.name}
                </div>
                <div style="font-size: 12px; color: #7f8c8d;">
                    ${structure.type || 'Structure'} • ${structure.polygon ? structure.polygon.length : 0} vertices
                </div>
                <div style="font-size: 12px; margin-top: 5px;">
                    ${structure.description || 'No description'}
                </div>
            </div>
        `).join('');
    }

    // Plant management methods
    selectPlant(plantId) {
        this.selectedPlant = this.plants.find(p => p.id === plantId);
        this.render();
        
        // Center on plant
        if (this.selectedPlant) {
            const centerX = this.canvas.width / 2;
            const centerY = this.canvas.height / 2;
            this.offsetX = centerX - this.selectedPlant.x * this.scale;
            this.offsetY = centerY - this.selectedPlant.y * this.scale;
            this.render();
        }
    }

    async removePlant(plantId) {
        if (confirm('Are you sure you want to remove this plant?')) {
            try {
                const response = await fetch(`/api/plants/${plantId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    this.plants = this.plants.filter(p => p.id !== plantId);
                    this.selectedPlant = null;
                    this.updateSidebar();
                    this.render();
                    showNotification('Plant removed successfully!', 'success');
                } else {
                    throw new Error('Failed to remove plant');
                }
            } catch (error) {
                console.warn('Could not remove via API, removing locally:', error);
                this.plants = this.plants.filter(p => p.id !== plantId);
                this.selectedPlant = null;
                this.updateSidebar();
                this.render();
                showNotification('Plant removed (local only)', 'success');
            }
        }
    }

    selectAnnotation(annotationId) {
        const annotation = this.annotations.find(a => a.id === annotationId);
        if (annotation && annotation.x && annotation.y) {
            // Center on annotation
            const centerX = this.canvas.width / 2;
            const centerY = this.canvas.height / 2;
            this.offsetX = centerX - annotation.x * this.scale;
            this.offsetY = centerY - annotation.y * this.scale;
            this.render();
        }
    }

    // Form handlers
    async handleAddPlant(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        
        // Get form values with validation
        const plantTypeValue = formData.get('plantType');
        const plantX = formData.get('plantX');
        const plantY = formData.get('plantY');
        const plantDate = formData.get('plantDate');
        
        // Validate required fields
        if (!plantTypeValue || plantTypeValue === '') {
            showNotification('Please select a plant type', 'error');
            return;
        }
        
        // Parse and validate coordinates
        const x = parseFloat(plantX);
        const y = parseFloat(plantY);
        
        if (isNaN(x) || isNaN(y)) {
            showNotification('Invalid coordinates. Please enter valid numbers.', 'error');
            return;
        }
        
        // Parse vegetable ID (should be a number from the dropdown value)
        const vegetableId = parseInt(plantTypeValue);
        
        if (isNaN(vegetableId)) {
            showNotification('Invalid plant type selected', 'error');
            return;
        }
        
        const plantData = {
            vegetable_id: vegetableId,
            x: x,
            y: y,
            planting_date: plantDate || null
        };
        
        try {
            const response = await fetch('/api/plants', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(plantData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Add the new plant to the display
                const newPlant = {
                    id: result.id,
                    x: result.x,
                    y: result.y,
                    vegetable_name: result.vegetable_name,
                    planting_date: result.date
                };
                
                this.plants.push(newPlant);
                this.updateSidebar();
                this.render();
                closeModal('addPlantModal');
                showNotification(result.message || 'Plant added successfully!', 'success');
                e.target.reset();
                
                // Exit plant mode after successful addition
                this.currentTool = 'select';
                this.updateAddPlantButton(false);
                this.updateCursor();
            } else {
                throw new Error(result.message || 'Failed to add plant');
            }
        } catch (error) {
            console.error('Error adding plant via API:', error);
            showNotification(`Failed to add plant: ${error.message}`, 'error');
        }
    }

    async handleAddAnnotation(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const annotationData = {
            type: formData.get('annotationType'),
            title: formData.get('annotationTitle'),
            content: formData.get('annotationContent'),
            target: formData.get('annotationTarget')
        };
        
        // Validate required fields
        if (!annotationData.content || !annotationData.content.trim()) {
            showNotification('Please enter content for the annotation', 'error');
            return;
        }
        
        if (!annotationData.title || !annotationData.title.trim()) {
            showNotification('Please enter a title for the annotation', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/add_annotation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(annotationData)
            });
            
            const result = await response.json();
            if (result.success) {
                // Reload annotations to get fresh data
                const annotationsResponse = await fetch('/api/annotations');
                const annotationsData = await annotationsResponse.json();
                if (annotationsData.success) {
                    this.annotations = annotationsData.annotations.map(annotation => ({
                        id: annotation.id,
                        title: annotation.type,
                        content: annotation.content,
                        type: annotation.type,
                        created_date: annotation.date
                    }));
                }
                
                this.updateSidebar();
                this.render();
                closeModal('addAnnotationModal');
                showNotification('Annotation added successfully!', 'success');
                e.target.reset();
            } else {
                throw new Error(result.message || 'Failed to add annotation');
            }
        } catch (error) {
            console.error('Error adding annotation via API:', error);
            showNotification(`Failed to add annotation: ${error.message}`, 'error');
        }
    }
}

// Global utility functions
function showLoading(show) {
    document.getElementById('loadingIndicator').style.display = show ? 'block' : 'none';
}

function updateStatus(message) {
    document.getElementById('statusBar').textContent = message;
}

function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

function togglePlantMode() {
    gardenGUI.togglePlantMode();
}

function showAddPlantModal() {
    document.getElementById('addPlantModal').style.display = 'block';
}

function showAddAnnotationModal() {
    // Update annotation targets
    const select = document.getElementById('annotationTarget');
    select.innerHTML = '<option value="garden">General Garden</option>';
    
    // Add plants as targets
    for (const plant of gardenGUI.plants) {
        const option = document.createElement('option');
        option.value = `plant_${plant.id}`;
        option.textContent = `Plant: ${plant.vegetable_name || plant.id}`;
        select.appendChild(option);
    }
    
    document.getElementById('addAnnotationModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    section.style.display = section.style.display === 'none' ? 'block' : 'none';
}

async function loadDatabase() {
    await gardenGUI.loadDatabase();
}

async function initializeDatabase() {
    if (confirm('This will reinitialize the database and may remove existing data. Continue?')) {
        showLoading(true);
        updateStatus('Initializing database...');
        
        try {
            const response = await fetch('/api/initialize', { method: 'POST' });
            if (response.ok) {
                await gardenGUI.loadDatabase();
                showNotification('Database initialized successfully!', 'success');
            } else {
                throw new Error('Failed to initialize database');
            }
        } catch (error) {
            console.warn('Could not initialize via API:', error);
            showNotification('Database initialization failed (API unavailable)', 'error');
        } finally {
            showLoading(false);
        }
    }
}

async function resetDatabase() {
    if (confirm('This will reset the database to its initial state, removing all added plants and data. Continue?')) {
        showLoading(true);
        updateStatus('Resetting database...');
        
        try {
            const response = await fetch('/api/reset_db', { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                await gardenGUI.loadDatabase();
                showNotification('Database reset successfully!', 'success');
            } else {
                throw new Error(result.message || 'Failed to reset database');
            }
        } catch (error) {
            console.warn('Could not reset via API:', error);
            showNotification('Database reset failed (API unavailable)', 'error');
        } finally {
            showLoading(false);
        }
    }
}

// Initialize the GUI when page loads
let gardenGUI;
document.addEventListener('DOMContentLoaded', () => {
    gardenGUI = new GardenGUI();
    
    // Load mock data initially for development
    setTimeout(() => {
        gardenGUI.loadMockData();
    }, 500);
});

// Handle modal clicks outside content
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});