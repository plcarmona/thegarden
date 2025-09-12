class GardenMap {
    constructor() {
        this.canvas = document.getElementById('garden-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.currentTool = 'polygon';
        this.currentPolygon = [];
        this.polygons = [];
        this.plants = [];
        this.isDrawing = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadMapData();
        this.loadWeatherData();
        this.loadLunarData();
        this.render();
    }
    
    setupEventListeners() {
        // Canvas events
        this.canvas.addEventListener('click', this.handleCanvasClick.bind(this));
        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        
        // Tool buttons
        document.getElementById('tool-polygon').addEventListener('click', () => this.setTool('polygon'));
        document.getElementById('tool-plant').addEventListener('click', () => this.setTool('plant'));
        document.getElementById('tool-select').addEventListener('click', () => this.setTool('select'));
        
        // Polygon tools
        document.getElementById('finish-polygon').addEventListener('click', this.finishPolygon.bind(this));
        document.getElementById('clear-polygon').addEventListener('click', this.clearCurrentPolygon.bind(this));
        
        // Set initial date to today
        document.getElementById('plant-date').value = new Date().toISOString().split('T')[0];
    }
    
    setTool(tool) {
        this.currentTool = tool;
        
        // Update button states
        document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`tool-${tool}`).classList.add('active');
        
        // Show/hide tool panels
        document.getElementById('polygon-tools').style.display = tool === 'polygon' ? 'block' : 'none';
        document.getElementById('plant-tools').style.display = tool === 'plant' ? 'block' : 'none';
        
        // Clear current polygon if switching tools
        if (tool !== 'polygon') {
            this.clearCurrentPolygon();
        }
        
        this.updateStatus(`Herramienta activa: ${this.getToolName(tool)}`);
    }
    
    getToolName(tool) {
        const names = {
            'polygon': 'Crear Área',
            'plant': 'Plantar',
            'select': 'Seleccionar'
        };
        return names[tool] || tool;
    }
    
    handleCanvasClick(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        switch (this.currentTool) {
            case 'polygon':
                this.addPolygonPoint(x, y);
                break;
            case 'plant':
                this.addPlant(x, y);
                break;
            case 'select':
                this.selectAtCoordinate(x, y);
                break;
        }
    }
    
    handleMouseMove(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = Math.round(event.clientX - rect.left);
        const y = Math.round(event.clientY - rect.top);
        
        document.getElementById('coordinates').textContent = `Coordenadas: (${x}, ${y})`;
    }
    
    addPolygonPoint(x, y) {
        this.currentPolygon.push({x, y});
        this.render();
        this.updateStatus(`Puntos del polígono: ${this.currentPolygon.length}`);
    }
    
    async finishPolygon() {
        if (this.currentPolygon.length < 3) {
            this.updateStatus('Error: Se necesitan al menos 3 puntos para crear un polígono');
            return;
        }
        
        const name = document.getElementById('polygon-name').value || `Área ${this.polygons.length + 1}`;
        const type = document.getElementById('polygon-type').value;
        
        const polygonData = {
            coordinates: this.currentPolygon,
            tipo: type,
            nombre: name
        };
        
        try {
            const response = await fetch('/api/huerta/mapa/poligono', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(polygonData)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.polygons.push({
                    ...polygonData,
                    id: result.id
                });
                this.clearCurrentPolygon();
                this.render();
                this.updateStatus(`Polígono "${name}" creado exitosamente`);
                
                // Clear form
                document.getElementById('polygon-name').value = '';
            } else {
                this.updateStatus(`Error: ${result.detail}`);
            }
        } catch (error) {
            this.updateStatus(`Error de conexión: ${error.message}`);
        }
    }
    
    clearCurrentPolygon() {
        this.currentPolygon = [];
        this.render();
        this.updateStatus('Polígono actual limpiado');
    }
    
    async addPlant(x, y) {
        const plantType = document.getElementById('plant-type').value;
        const plantDate = document.getElementById('plant-date').value;
        
        const plantData = {
            hortaliza_id: parseInt(plantType),
            coordenadas: {x, y},
            fecha_siembra: plantDate
        };
        
        try {
            const response = await fetch('/api/huerta/cultivos/activos', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(plantData)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.plants.push({
                    ...plantData,
                    id: result.id
                });
                this.render();
                this.updateStatus(`Cultivo agregado en (${x}, ${y})`);
            } else {
                this.updateStatus(`Error: ${result.detail}`);
            }
        } catch (error) {
            this.updateStatus(`Error de conexión: ${error.message}`);
        }
    }
    
    async selectAtCoordinate(x, y) {
        try {
            const response = await fetch(`/api/huerta/coordenada/${x}/${y}`);
            const result = await response.json();
            
            if (result.existe_cultivo) {
                const cultivo = result.cultivo;
                this.updateStatus(`Cultivo encontrado: Tipo ${cultivo.hortaliza_id}, plantado el ${cultivo.fecha_siembra}`);
            } else {
                this.updateStatus(`No hay cultivos en (${x}, ${y})`);
            }
        } catch (error) {
            this.updateStatus(`Error de conexión: ${error.message}`);
        }
    }
    
    async loadMapData() {
        try {
            const response = await fetch('/api/huerta/mapa');
            const data = await response.json();
            
            this.polygons = data.poligonos || [];
            this.plants = data.cultivos_activos || [];
            this.render();
            this.updateStatus('Mapa cargado exitosamente');
        } catch (error) {
            this.updateStatus(`Error cargando mapa: ${error.message}`);
        }
    }
    
    async loadWeatherData() {
        try {
            const response = await fetch('/api/clima/pronostico');
            const data = await response.json();
            this.displayWeatherInfo(data);
            
            // Load weather alerts
            const alertsResponse = await fetch('/api/clima/alertas');
            const alerts = await alertsResponse.json();
            this.displayWeatherAlerts(alerts);
        } catch (error) {
            document.getElementById('weather-info').innerHTML = 
                '<p style="color: #dc3545;">Error cargando clima</p>';
        }
    }
    
    async loadLunarData() {
        try {
            const response = await fetch('/api/calendario/lunar');
            const data = await response.json();
            this.displayLunarInfo(data);
        } catch (error) {
            document.getElementById('lunar-info').innerHTML = 
                '<p style="color: #dc3545;">Error cargando información lunar</p>';
        }
    }
    
    displayWeatherInfo(data) {
        const weatherInfo = document.getElementById('weather-info');
        const today = data.dias[0];
        const tomorrow = data.dias[1];
        
        weatherInfo.innerHTML = `
            <div>
                <strong>Hoy:</strong> ${today.icono} ${today.descripcion}<br>
                <span style="font-size: 0.85em;">
                    ${today.temperatura_min}°C - ${today.temperatura_max}°C<br>
                    Humedad: ${today.humedad}%
                </span>
            </div>
            <div style="margin-top: 8px;">
                <strong>Mañana:</strong> ${tomorrow.icono} ${tomorrow.descripcion}<br>
                <span style="font-size: 0.85em;">
                    ${tomorrow.temperatura_min}°C - ${tomorrow.temperatura_max}°C
                </span>
            </div>
        `;
    }
    
    displayWeatherAlerts(alerts) {
        const alertsContainer = document.getElementById('weather-alerts');
        
        if (alerts.length === 0) {
            alertsContainer.innerHTML = '';
            return;
        }
        
        const alertsHtml = alerts.map(alert => `
            <div class="alert alert-${alert.severidad}">
                <strong>${alert.tipo.replace('_', ' ')}:</strong> ${alert.mensaje}
            </div>
        `).join('');
        
        alertsContainer.innerHTML = alertsHtml;
    }
    
    displayLunarInfo(data) {
        const lunarInfo = document.getElementById('lunar-info');
        
        const phaseIcons = {
            'nueva': '🌑',
            'creciente': '🌓',
            'llena': '🌕',
            'menguante': '🌗'
        };
        
        lunarInfo.innerHTML = `
            <div class="lunar-phase">
                <span class="phase-icon">${phaseIcons[data.fase]}</span>
                <span><strong>Fase ${data.fase}</strong></span>
            </div>
            <div style="font-size: 0.85em; margin: 5px 0;">
                Iluminación: ${data.iluminacion_porcentaje}%
            </div>
            <div class="recommendations">
                <strong>Recomendación:</strong><br>
                <span style="font-size: 0.85em;">${data.recomendacion_siembra}</span>
            </div>
        `;
    }
    
    render() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw grid
        this.drawGrid();
        
        // Draw existing polygons
        this.polygons.forEach(polygon => this.drawPolygon(polygon, false));
        
        // Draw current polygon being created
        if (this.currentPolygon.length > 0) {
            this.drawPolygon({coordinates: this.currentPolygon, tipo: 'current'}, true);
        }
        
        // Draw plants
        this.plants.forEach(plant => this.drawPlant(plant));
    }
    
    drawGrid() {
        this.ctx.strokeStyle = '#e9ecef';
        this.ctx.lineWidth = 1;
        
        // Vertical lines
        for (let x = 0; x <= this.canvas.width; x += 50) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y <= this.canvas.height; y += 50) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }
    
    drawPolygon(polygon, isCurrent = false) {
        if (polygon.coordinates.length < 2) return;
        
        this.ctx.beginPath();
        this.ctx.moveTo(polygon.coordinates[0].x, polygon.coordinates[0].y);
        
        for (let i = 1; i < polygon.coordinates.length; i++) {
            this.ctx.lineTo(polygon.coordinates[i].x, polygon.coordinates[i].y);
        }
        
        if (!isCurrent && polygon.coordinates.length > 2) {
            this.ctx.closePath();
        }
        
        // Set colors based on type
        const colors = {
            'cultivo': {fill: 'rgba(76, 175, 80, 0.3)', stroke: '#4CAF50'},
            'sendero': {fill: 'rgba(158, 158, 158, 0.3)', stroke: '#9E9E9E'},
            'estructura': {fill: 'rgba(255, 193, 7, 0.3)', stroke: '#FFC107'},
            'current': {fill: 'rgba(33, 150, 243, 0.3)', stroke: '#2196F3'}
        };
        
        const color = colors[polygon.tipo] || colors['cultivo'];
        
        this.ctx.fillStyle = color.fill;
        this.ctx.strokeStyle = color.stroke;
        this.ctx.lineWidth = 2;
        
        this.ctx.fill();
        this.ctx.stroke();
        
        // Draw points
        polygon.coordinates.forEach((point, index) => {
            this.ctx.beginPath();
            this.ctx.arc(point.x, point.y, 4, 0, 2 * Math.PI);
            this.ctx.fillStyle = color.stroke;
            this.ctx.fill();
        });
    }
    
    drawPlant(plant) {
        const x = plant.coordenadas.x;
        const y = plant.coordenadas.y;
        
        // Plant types colors
        const plantColors = {
            1: '#FF6B6B', // Tomate - rojo
            2: '#4ECDC4', // Lechuga - verde azulado
            3: '#FFA500', // Zanahoria - naranja
            4: '#32CD32'  // Pepino - verde lima
        };
        
        const color = plantColors[plant.hortaliza_id] || '#4CAF50';
        
        // Draw plant circle
        this.ctx.beginPath();
        this.ctx.arc(x, y, 12, 0, 2 * Math.PI);
        this.ctx.fillStyle = color;
        this.ctx.fill();
        this.ctx.strokeStyle = '#fff';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        
        // Draw plant symbol
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText('🌱', x, y);
    }
    
    updateStatus(message) {
        document.getElementById('status').textContent = message;
        console.log('Status:', message);
    }
}

// Initialize the garden map when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new GardenMap();
});