-- Schema KuzuDB para The Garden
-- Definición de nodos y relaciones para el sistema de gestión de huerta

-- =============================================
-- TABLAS DE NODOS (NODE TABLES)
-- =============================================

-- Hortaliza: Información de especies/tipos de plantas
CREATE NODE TABLE Hortaliza (
    id INT64 PRIMARY KEY,
    nombre STRING,
    descripcion STRING,
    ciclo_dias INT64,
    siembra_mes_inicio INT64,
    siembra_mes_fin INT64,
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

-- =============================================
-- TABLAS DE RELACIONES (RELATIONSHIP TABLES)
-- =============================================

-- IS_OF_TYPE: Planta -> Hortaliza (una planta es de un tipo de hortaliza)
CREATE REL TABLE IS_OF_TYPE (
    FROM Planta TO Hortaliza,
    fecha_relacion TIMESTAMP
);