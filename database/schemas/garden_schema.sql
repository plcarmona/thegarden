-- Schema KuzuDB para The Garden
-- Definición de nodos y relaciones para el sistema de gestión de huerta

-- =============================================
-- TABLAS DE NODOS (NODE TABLES)
-- =============================================

-- Hortaliza: Información de especies/tipos de plantas
CREATE NODE TABLE Hortaliza (
    id INTEGER PRIMARY KEY,
    nombre STRING,
    descripcion STRING,
    ciclo_dias INTEGER,
    siembra_mes_inicio INTEGER,
    siembra_mes_fin INTEGER,
    plagas_comunes STRING[],
    cuidados STRING[],
    tamano_promedio DOUBLE,
    distancia_min DOUBLE
);

-- Planta: Instancias individuales de cultivos
CREATE NODE TABLE Planta (
    id STRING PRIMARY KEY,
    fecha_siembra DATE,
    coordenadas_x DOUBLE,
    coordenadas_y DOUBLE,
    estado STRING,
    fecha_cosecha DATE,
    notas STRING
);

-- Huerta: Información espacial y configuración de jardín
CREATE NODE TABLE Huerta (
    id STRING PRIMARY KEY,
    nombre STRING,
    ancho DOUBLE,
    alto DOUBLE,
    configuracion_activa BOOLEAN,
    fecha_creacion TIMESTAMP,
    descripcion STRING
);

-- Anotaciones: Sistema de comentarios y notas con diferentes niveles de especificidad
CREATE NODE TABLE Anotaciones (
    id STRING PRIMARY KEY,
    tipo STRING,
    nivel_especificidad STRING,
    fecha TIMESTAMP,
    notas STRING,
    fotos STRING[],
    temporada STRING,
    metadata STRING
);

-- =============================================
-- TABLAS DE RELACIONES (RELATIONSHIP TABLES)
-- =============================================

-- IS_OF_TYPE: Planta -> Hortaliza (una planta es de un tipo de hortaliza)
CREATE REL TABLE IS_OF_TYPE (
    FROM Planta TO Hortaliza,
    fecha_relacion TIMESTAMP
);

-- LOCATED_IN: Planta -> Huerta (una planta está ubicada en una huerta)
CREATE REL TABLE LOCATED_IN (
    FROM Planta TO Huerta,
    fecha_plantacion TIMESTAMP,
    area_ocupada DOUBLE
);

-- CONTAINS: Huerta -> Planta (una huerta contiene plantas - inversa de LOCATED_IN)
CREATE REL TABLE CONTAINS (
    FROM Huerta TO Planta
);

-- ANNOTATES: Anotaciones -> Hortaliza (anotación se refiere a tipo de hortaliza)
CREATE REL TABLE ANNOTATES (
    FROM Anotaciones TO Hortaliza,
    relevancia DOUBLE,
    fecha_anotacion TIMESTAMP
);

-- ANNOTATES_PLANTA: Anotaciones -> Planta (anotación se refiere a planta específica)
CREATE REL TABLE ANNOTATES_PLANTA (
    FROM Anotaciones TO Planta,
    relevancia DOUBLE,
    fecha_anotacion TIMESTAMP
);

-- ANNOTATES_HUERTA: Anotaciones -> Huerta (anotación se refiere a huerta completa)
CREATE REL TABLE ANNOTATES_HUERTA (
    FROM Anotaciones TO Huerta,
    relevancia DOUBLE,
    fecha_anotacion TIMESTAMP
);

-- TEMPORAL_CONTEXT: Anotaciones -> Anotaciones (agrupa anotaciones por contexto temporal)
CREATE REL TABLE TEMPORAL_CONTEXT (
    FROM Anotaciones TO Anotaciones,
    tipo_contexto STRING
);