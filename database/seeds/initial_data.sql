-- Datos iniciales para KuzuDB - The Garden
-- Migración de datos existentes del sistema en memoria a KuzuDB

-- =============================================
-- HORTALIZAS BASE (migrado desde models.py)
-- =============================================

CREATE (:Hortaliza {
    id: 1, 
    nombre: "Tomate", 
    descripcion: "Solanum lycopersicum - Hortaliza de fruto muy popular",
    ciclo_dias: 120, 
    siembra_mes_inicio: 9, 
    siembra_mes_fin: 11,
    plagas_comunes: ["Trips", "Mosca blanca", "Pulgones", "Tizón tardío"],
    cuidados: ["Riego regular", "Tutoreo", "Poda de brotes laterales", "Fertilización rica en potasio"],
    tamano_promedio: 1.5, 
    distancia_min: 0.6
});

CREATE (:Hortaliza {
    id: 2, 
    nombre: "Lechuga", 
    descripcion: "Lactuca sativa - Hortaliza de hoja de crecimiento rápido",
    ciclo_dias: 60, 
    siembra_mes_inicio: 3, 
    siembra_mes_fin: 9,
    plagas_comunes: ["Caracoles", "Babosas", "Pulgones", "Mildiu"],
    cuidados: ["Riego frecuente", "Sombra parcial en verano", "Cosecha escalonada"],
    tamano_promedio: 0.3, 
    distancia_min: 0.2
});

CREATE (:Hortaliza {
    id: 3, 
    nombre: "Zanahoria", 
    descripcion: "Daucus carota - Hortaliza de raíz rica en betacaroteno",
    ciclo_dias: 90, 
    siembra_mes_inicio: 8, 
    siembra_mes_fin: 2,
    plagas_comunes: ["Mosca de la zanahoria", "Nematodos", "Gusano alambre"],
    cuidados: ["Suelo suelto y profundo", "Raleo de plántulas", "Riego moderado"],
    tamano_promedio: 0.1, 
    distancia_min: 0.1
});

CREATE (:Hortaliza {
    id: 4, 
    nombre: "Pepino", 
    descripcion: "Cucumis sativus - Hortaliza rastrera de fruto refrescante",
    ciclo_dias: 75, 
    siembra_mes_inicio: 10, 
    siembra_mes_fin: 12,
    plagas_comunes: ["Oídio", "Trips", "Arañuela", "Mosca blanca"],
    cuidados: ["Tutoreo o espalderas", "Riego abundante", "Fertilización regular", "Cosecha frecuente"],
    tamano_promedio: 2.0, 
    distancia_min: 0.8
});

-- Agregar más hortalizas comunes
CREATE (:Hortaliza {
    id: 5, 
    nombre: "Albahaca", 
    descripcion: "Ocimum basilicum - Hierba aromática mediterránea",
    ciclo_dias: 75, 
    siembra_mes_inicio: 9, 
    siembra_mes_fin: 2,
    plagas_comunes: ["Pulgones", "Caracoles", "Fusarium"],
    cuidados: ["Riego regular", "Pellizcar flores", "Cosecha frecuente", "Proteger de heladas"],
    tamano_promedio: 0.25, 
    distancia_min: 0.15
});

CREATE (:Hortaliza {
    id: 6, 
    nombre: "Pimiento", 
    descripcion: "Capsicum annuum - Hortaliza de fruto dulce o picante",
    ciclo_dias: 100, 
    siembra_mes_inicio: 8, 
    siembra_mes_fin: 11,
    plagas_comunes: ["Trips", "Pulgones", "Mosca blanca", "Antracnosis"],
    cuidados: ["Tutoreo", "Riego constante", "Fertilización balanceada", "Protección del viento"],
    tamano_promedio: 1.0, 
    distancia_min: 0.4
});

-- =============================================
-- HUERTA POR DEFECTO
-- =============================================

CREATE (:Huerta {
    id: "huerta_default", 
    nombre: "Mi Huerta Principal", 
    ancho: 800.0, 
    alto: 600.0,
    configuracion_activa: true,
    fecha_creacion: timestamp('2024-01-01T10:00:00'),
    descripcion: "Huerta principal del jardín con área de cultivos mixtos"
});

-- Crear huerta de ejemplo adicional
CREATE (:Huerta {
    id: "huerta_experimental", 
    nombre: "Área Experimental", 
    ancho: 400.0, 
    alto: 300.0,
    configuracion_activa: false,
    fecha_creacion: timestamp('2024-01-15T10:00:00'),
    descripcion: "Área experimental para pruebas de nuevas variedades"
});

-- =============================================
-- PLANTAS DE EJEMPLO
-- =============================================

-- Algunos cultivos activos de ejemplo
CREATE (:Planta {
    id: "tomate_001", 
    fecha_siembra: date('2024-01-15'),
    coordenadas_x: 150.0,
    coordenadas_y: 100.0,
    estado: "activo",
    fecha_cosecha: NULL,
    notas: "Primera siembra de tomate de la temporada"
});

CREATE (:Planta {
    id: "lechuga_001", 
    fecha_siembra: date('2024-01-20'),
    coordenadas_x: 200.0,
    coordenadas_y: 150.0,
    estado: "activo",
    fecha_cosecha: NULL,
    notas: "Lechuga para ensaladas de verano"
});

CREATE (:Planta {
    id: "pepino_001", 
    fecha_siembra: date('2024-01-10'),
    coordenadas_x: 300.0,
    coordenadas_y: 200.0,
    estado: "activo",
    fecha_cosecha: NULL,
    notas: "Pepino con tutor, necesita soporte"
});

-- =============================================
-- ANOTACIONES DE EJEMPLO
-- =============================================

CREATE (:Anotaciones {
    id: "anotacion_001",
    tipo: "siembra",
    nivel_especificidad: "individuo", 
    fecha: timestamp('2024-01-15T09:30:00'),
    notas: "Siembra realizada en día soleado, suelo bien preparado",
    fotos: [],
    temporada: "verano",
    metadata: "{\"temperatura\": 22, \"humedad\": 65}"
});

CREATE (:Anotaciones {
    id: "anotacion_002",
    tipo: "riego",
    nivel_especificidad: "tipo_planta",
    fecha: timestamp('2024-01-18T07:00:00'),
    notas: "Riego matutino, sistema de goteo funcionando correctamente",
    fotos: [],
    temporada: "verano", 
    metadata: "{\"duracion_minutos\": 30, \"litros_aprox\": 15}"
});

CREATE (:Anotaciones {
    id: "anotacion_003",
    tipo: "nota",
    nivel_especificidad: "estacion",
    fecha: timestamp('2024-01-20T18:00:00'), 
    notas: "Las temperaturas nocturnas están bajando, considerar protección",
    fotos: [],
    temporada: "verano",
    metadata: "{\"temperatura_minima\": 12}"
});

-- =============================================
-- RELACIONES INICIALES
-- =============================================

-- Relacionar plantas con tipos de hortalizas
MATCH (p:Planta {id: "tomate_001"}), (h:Hortaliza {id: 1})
CREATE (p)-[:IS_OF_TYPE {fecha_relacion: timestamp('2024-01-15T09:30:00')}]->(h);

MATCH (p:Planta {id: "lechuga_001"}), (h:Hortaliza {id: 2})
CREATE (p)-[:IS_OF_TYPE {fecha_relacion: timestamp('2024-01-20T10:00:00')}]->(h);

MATCH (p:Planta {id: "pepino_001"}), (h:Hortaliza {id: 4})
CREATE (p)-[:IS_OF_TYPE {fecha_relacion: timestamp('2024-01-10T08:00:00')}]->(h);

-- Relacionar plantas con huerta
MATCH (p:Planta {id: "tomate_001"}), (hu:Huerta {id: "huerta_default"})
CREATE (p)-[:LOCATED_IN {fecha_plantacion: date('2024-01-15'), area_ocupada: 1.5}]->(hu),
       (hu)-[:CONTAINS]->(p);

MATCH (p:Planta {id: "lechuga_001"}), (hu:Huerta {id: "huerta_default"})
CREATE (p)-[:LOCATED_IN {fecha_plantacion: date('2024-01-20'), area_ocupada: 0.3}]->(hu),
       (hu)-[:CONTAINS]->(p);

MATCH (p:Planta {id: "pepino_001"}), (hu:Huerta {id: "huerta_default"})
CREATE (p)-[:LOCATED_IN {fecha_plantacion: date('2024-01-10'), area_ocupada: 2.0}]->(hu),
       (hu)-[:CONTAINS]->(p);

-- Relacionar anotaciones
MATCH (a:Anotaciones {id: "anotacion_001"}), (p:Planta {id: "tomate_001"})
CREATE (a)-[:ANNOTATES_PLANTA {relevancia: 1.0, fecha_anotacion: timestamp('2024-01-15T09:30:00')}]->(p);

MATCH (a:Anotaciones {id: "anotacion_002"}), (h:Hortaliza {id: 1})
CREATE (a)-[:ANNOTATES {relevancia: 0.8, fecha_anotacion: timestamp('2024-01-18T07:00:00')}]->(h);

MATCH (a:Anotaciones {id: "anotacion_003"}), (hu:Huerta {id: "huerta_default"})
CREATE (a)-[:ANNOTATES_HUERTA {relevancia: 0.9, fecha_anotacion: timestamp('2024-01-20T18:00:00')}]->(hu);