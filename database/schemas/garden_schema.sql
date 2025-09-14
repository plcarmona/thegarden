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
    fecha_cosecha DATE
);

-- Huerta: Información espacial y configuración de jardín
CREATE NODE TABLE Huerta (
    id STRING PRIMARY KEY,
    nombre STRING,
    ancho DOUBLE,
    alto DOUBLE,
    fecha_creacion TIMESTAMP
);

-- Notas: Registro de notas y observaciones  
CREATE NODE TABLE Anotation (
    id STRING PRIMARY KEY,
    tipo STRING,
    comentario STRING,
    fecha TIMESTAMP
);

-- =============================================
-- TABLAS DE RELACIONES (RELATIONSHIP TABLES)
-- =============================================

-- IS_OF_TYPE: Planta -> Hortaliza (una planta es de un tipo de hortaliza)
CREATE REL TABLE IS_OF_TYPE (
    FROM Planta TO Hortaliza,
    fecha_relacion TIMESTAMP
);

-- PART_OF: Planta -> Huerta (una planta pertenece a una huerta)
CREATE REL TABLE PART_OF (
    FROM Planta TO Huerta,
    fecha_relacion TIMESTAMP
);

-- HAS_ANOTATION: Planta -> Anotation (una planta tiene anotaciones)
CREATE REL TABLE HAS_ANOTATION (
    FROM Planta TO Anotation,
    fecha_relacion TIMESTAMP
);

-- HAS_ANOTATION_HUERTA: Huerta -> Anotation (una huerta tiene anotaciones)
CREATE REL TABLE HAS_ANOTATION_HUERTA (
    FROM Huerta TO Anotation,
    fecha_relacion TIMESTAMP
);

-- HAS_ANOTATION_HORTALIZA: Hortaliza -> Anotation (una hortaliza tiene anotaciones)
CREATE REL TABLE HAS_ANOTATION_HORTALIZA (
    FROM Hortaliza TO Anotation,
    fecha_relacion TIMESTAMP
);

-- =============================================

