-- Datos iniciales para KuzuDB - The Garden
-- Migración de datos existentes del sistema en memoria a KuzuDB

-- =============================================
-- HORTALIZAS BASE (migrado desde models.py)
-- =============================================

CREATE (h:Hortaliza {
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

CREATE (h:Hortaliza {
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

CREATE (h:Hortaliza {
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

-- =============================================
-- HUERTA POR DEFECTO
-- =============================================

CREATE (hu:Huerta {
    id: "huerta_default", 
    nombre: "Mi Huerta Principal", 
    ancho: 800.0, 
    alto: 600.0,
    fecha_creacion: timestamp('2024-01-01T10:00:00')
});

-- =============================================
-- PLANTAS DE EJEMPLO
-- =============================================

CREATE (p:Planta {
    id: "tomate_001", 
    fecha_siembra: date('2024-01-15'),
    coordenadas_x: 150.0,
    coordenadas_y: 100.0,
    fecha_cosecha: NULL,
    estado: "activo"
});

CREATE (p:Planta {
    id: "lechuga_001", 
    fecha_siembra: date('2024-01-20'),
    coordenadas_x: 200.0,
    coordenadas_y: 150.0,
    fecha_cosecha: NULL,
    estado: "activo"
});

CREATE (p:Planta {
    id: "zanahoria_001", 
    fecha_siembra: date('2024-01-10'),
    coordenadas_x: 300.0,
    coordenadas_y: 120.0,
    fecha_cosecha: NULL,
    estado: "activo"
});

-- =============================================
-- RELACIONES INICIALES
-- =============================================

-- Relacionar plantas con tipos de hortalizas
MATCH (p:Planta {id: "tomate_001"}), (h:Hortaliza {id: 1})
CREATE (p)-[:IS_OF_TYPE {fecha_relacion: timestamp('2024-01-15T09:30:00')}]->(h);

MATCH (p:Planta {id: "lechuga_001"}), (h:Hortaliza {id: 2})
CREATE (p)-[:IS_OF_TYPE {fecha_relacion: timestamp('2024-01-20T10:00:00')}]->(h);

-- =============================================
-- ANOTACIONES DE EJEMPLO
-- =============================================

CREATE (:Anotation {
    id: "anotacion_001",
    tipo: "siembra",
    comentario: "Siembra realizada en día soleado, suelo bien preparado",
    fecha: timestamp('2024-01-15T09:30:00')
});

CREATE (:Anotation {
    id: "anotacion_002",
    tipo: "riego",
    comentario: "Riego matutino, sistema de goteo funcionando correctamente",
    fecha: timestamp('2024-01-18T07:00:00')
});

CREATE (:Anotation {
    id: "anotacion_003",
    tipo: "nota",
    comentario: "Las temperaturas nocturnas están bajando, considerar protección",
    fecha: timestamp('2024-01-20T18:00:00')
});

-- =============================================
-- RELACIONES INICIALES
-- =============================================

-- Relacionar plantas con tipos de hortalizas
MATCH (p:Planta {id: "tomate_001"}), (h:Hortaliza {id: 1})
CREATE (p)-[:IS_OF_TYPE {fecha_relacion: timestamp('2024-01-15T09:30:00')}]->(h);

MATCH (p:Planta {id: "lechuga_001"}), (h:Hortaliza {id: 2})
CREATE (p)-[:IS_OF_TYPE {fecha_relacion: timestamp('2024-01-20T10:00:00')}]->(h);

MATCH (p:Planta {id: "zanahoria_001"}), (h:Hortaliza {id: 3})
CREATE (p)-[:IS_OF_TYPE {fecha_relacion: timestamp('2024-01-10T08:00:00')}]->(h);

-- Relacionar plantas con huerta
MATCH (p:Planta {id: "tomate_001"}), (hu:Huerta {id: "huerta_default"})
CREATE (p)-[:PART_OF {fecha_relacion: timestamp('2024-01-15T09:30:00')}]->(hu);

MATCH (p:Planta {id: "lechuga_001"}), (hu:Huerta {id: "huerta_default"})
CREATE (p)-[:PART_OF {fecha_relacion: timestamp('2024-01-20T10:00:00')}]->(hu);

MATCH (p:Planta {id: "zanahoria_001"}), (hu:Huerta {id: "huerta_default"})
CREATE (p)-[:PART_OF {fecha_relacion: timestamp('2024-01-10T08:00:00')}]->(hu);

-- Relacionar anotaciones
MATCH (a:Anotation {id: "anotacion_001"}), (p:Planta {id: "tomate_001"})
CREATE (p)-[:HAS_ANOTATION {fecha_relacion: timestamp('2024-01-15T09:30:00')}]->(a);

MATCH (a:Anotation {id: "anotacion_002"}), (h:Hortaliza {id: 1})
CREATE (h)-[:HAS_ANOTATION_HORTALIZA {fecha_relacion: timestamp('2024-01-18T07:00:00')}]->(a);

MATCH (a:Anotation {id: "anotacion_003"}), (hu:Huerta {id: "huerta_default"})
CREATE (hu)-[:HAS_ANOTATION_HUERTA {fecha_relacion: timestamp('2024-01-20T18:00:00')}]->(a);