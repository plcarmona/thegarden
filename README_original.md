# thegarden
a garden planificator 🌱

## Parte I: Documento de Especificación de Requisitos de Software (SRS)

  

*Fase de SDLC:* Planificación y Análisis de Requisitos

  

### 1. Introducción

  

#### 1.1. Propósito

  

- [Describir el propósito de este documento SRS, a quién está dirigido y cómo debe ser utilizado.]

    El propósito es dejar registrado el desarrollo del SRS, para poder consultar y hacer mejoras que queden registradas

  

#### 1.2. Alcance del Proyecto

  

- *Objetivos del Software:* [Describir brevemente el producto de software, sus objetivos y los beneficios que aportará al negocio o a los usuarios.]

    Es un software para poder hacer registros diarios de tu huerta, planificar proyectos de esta, y ver fechas, temperaturas proximas, para anticipar y reducir riesgos que pueda sufrir tu huerta. Las huertas prosperan cuando anotas y haces seguimiento de lo que haces en ella, y este software te ayuda a eso. Esto ayuda a no tener en tu cabeza todo el tiempo las fechas de siembra y cosecha, y te ayuda a planificar mejor tu huerta.

- *Dentro del Alcance (In-Scope):* [Listar de manera clara y concisa todas las funcionalidades y características que se incluirán en el proyecto.]

  

    Tiene que implementar un sistema de coordenada para ver la ubicación de la huerta.

    Tiene un calendario de siembra y cosecha donde puedes anotar las fechas de esos eventos para cada hortaliza.

    Tiene un calendario lunar que se puede asociar al calendario de siembra (te da tips cuando conviene sembrar, cosechar segun la fase de la luna).

    Tiene un panel con el clima estimado de los próximos dias que vienen (semana) (para poder anticipar heladas y estar preparada).

    Las hortalizas tienen descripción, tiempos, plagas, necesidades/ciuidados, tamaño/geometria.

    Tiene que implementar una base de datos para registrar todos los eventos, con distintos niveles de especificidad, es decir pueden ser anotaciones por tipo de plantas, por tiempo, por individuo(planta), estacion.

    se debe inicializar plantas activas como instancias de hortalizas.

    Tiene que tener para cada cultivo la posibilidad de subir fotos.

    Se debe consultar por: pos(x,y) > planta activa si hay


  

- *Fuera del Alcance (Out-of-Scope):* [Definir explícitamente qué funcionalidades no se incluirán para evitar la "inflación del alcance" (scope creep).]

    No va a tener un login

    No va a tener multiples paginas y secciones

    No va a ser compleja y robusta

    No va a tener un sistema de pagos

    No va a tener un sistema de usuarios

    No va a tener un sistema de notificaciones

    No va a tener un sistema de reportes

    No va a tener un sistema de recomendaciones personalizadas

    No va a tener un sistema de integraciones con otros servicios

  
  

#### 1.3. Definiciones, Acrónimos y Abreviaturas

  

- [Listar y definir todos los términos, acrónimos y abreviaturas utilizados en el documento para asegurar un entendimiento común.]

  
  

### 2. Planificación y Análisis

  

#### 2.1. Recopilación de Información

  

- *Partes Interesadas (Stakeholders):* [Identificar a todas las partes interesadas clave (clientes, usuarios, equipos internos, etc.).]

- *Métodos de Recopilación:* [Describir los métodos utilizados para obtener los requisitos (entrevistas, talleres, encuestas, etc.).]

  

#### 2.2. Estudios de Viabilidad

  

- *Viabilidad Técnica:* [Evaluar si la tecnología necesaria está disponible y si el equipo tiene la capacidad técnica para desarrollar el proyecto.]

- *Viabilidad Financiera:* [Analizar la relación costo-beneficio del proyecto.]

- *Viabilidad Operativa:* [Determinar si el software se integrará correctamente en los procesos operativos actuales.]

  

#### 2.3. Estimación del Proyecto

  

- *Recursos Necesarios:* [Detallar los recursos humanos, de software y de hardware necesarios.]

- *Costes Estimados:* [Proporcionar una estimación del presupuesto del proyecto.]

- *Plazos Estimados:* [Presentar una estimación del tiempo necesario para completar el proyecto.]

  

#### 2.4. Riesgos Potenciales

  

- [Identificar los posibles riesgos (técnicos, de mercado, de recursos) y proponer un plan de mitigación para cada uno.]

  

#### 2.5. Cronograma del Proyecto

  

- [Adjuntar un cronograma visual (ej. Diagrama de Gantt) con los principales hitos, entregables y plazos.]

  

### 3. Requisitos del Software

  

#### 3.1. Requisitos Funcionales

  

- [Describir detalladamente cada función del software. Usar un formato claro, por ejemplo:]

    - *RF-001: Creación de Cuenta de Usuario*

        - *Descripción:* El sistema debe permitir a un nuevo usuario registrarse proporcionando un nombre de usuario, correo electrónico y contraseña.

        - *Criterios de Aceptación:* El sistema valida que el correo no esté en uso, la contraseña cumpla los requisitos de seguridad y envía un correo de confirmación.

* **RF-001: Cargar mapa de la huerta**
  - *Descripción:* El sistema debe permitir cargar y visualizar un mapa de la huerta usando coordenadas (x,y) en un canvas HTML5.
  - *Criterios de Aceptación:*
    - El sistema muestra un canvas interactivo para visualizar la huerta
    - Se pueden definir polígonos para representar áreas de cultivo
    - Cada polígono tiene coordenadas (x,y) precisas
    - El mapa es escalable y permite zoom básico
  - *Prioridad:* Alta (Fase 1)

* **RF-002: Implementar base de datos**
  - *Descripción:* Crear estructura de base de datos con tablas para eventos, cultivos y anotaciones.
  - *Criterios de Aceptación:*
    - Base de datos KuzuDB configurada correctamente
    - Tablas creadas según el esquema definido
    - Relaciones entre tablas establecidas
  - *Prioridad:* Alta (Fase 1)

* **RF-003: Queries para consultar la base de datos**
  - *Descripción:* Implementar funciones de consulta, especialmente por coordenadas (x,y).
  - *Criterios de Aceptación:*
    - Query por coordenadas (x,y) devuelve planta activa si existe
    - Queries optimizadas para rendimiento
    - Manejo de errores y casos edge
  - *Prioridad:* Alta (Fase 1)

* **RF-004: Sistema de anotaciones**
  - *Descripción:* Funciones para registrar eventos con diferentes niveles de especificidad.
  - *Criterios de Aceptación:*
    - Anotaciones por tipo de planta, tiempo, individuo, estación
    - Timestamps automáticos
    - Asociación correcta con cultivos
  - *Prioridad:* Media (Fase 2)

* **RF-005: Inicialización de cultivos activos**
  - *Descripción:* Crear instancias de hortalizas con posiciones específicas.
  - *Criterios de Aceptación:*
    - Instancias con posición (x,y) válida
    - Verificación de colisiones entre cultivos
    - Estado de cultivo activo/inactivo
  - *Prioridad:* Alta (Fase 1)

* **RF-006: Integración API del clima**
  - *Descripción:* Obtener datos meteorológicos de API externa.
  - *Criterios de Aceptación:*
    - Datos de clima de próximos 7 días
    - Manejo de errores de API
    - Cache de datos para reducir llamadas
  - *Prioridad:* Media (Fase 2)

* **RF-007: Calendario lunar**
  - *Descripción:* Mostrar fases lunares y recomendaciones de siembra.
  - *Criterios de Aceptación:*
    - Fases lunares precisas
    - Tips de siembra según fase lunar
    - Integración con calendario de cultivos
  - *Prioridad:* Baja (Fase 3)

* **RF-008: Calendario de siembra y cosecha**
  - *Descripción:* Visualizar fechas importantes para cada cultivo.
  - *Criterios de Aceptación:*
    - Calendario visual intuitivo
    - Fechas automáticas basadas en tipo de cultivo
    - Recordatorios y alertas
  - *Prioridad:* Media (Fase 2)

* **RF-009: Sugerencias de siembra**
  - *Descripción:* Recomendaciones automáticas según fecha actual y condiciones.
  - *Criterios de Aceptación:*
    - Sugerencias basadas en temporada
    - Consideración del clima local
    - Disponibilidad de espacio en huerta
  - *Prioridad:* Baja (Fase 3)


#### 3.2. Requisitos No Funcionales

- **Rendimiento:**
  - El mapa de la huerta debe cargar en menos de 3 segundos
  - Las consultas a la base de datos deben responder en menos de 500ms
  - El canvas debe mantener 30 FPS durante interacciones

- **Usabilidad:**
  - Interfaz intuitiva para usuarios sin experiencia técnica en jardinería
  - Navegación por teclado y mouse en el mapa
  - Responsive design para tablets y escritorio

- **Confiabilidad:**
  - Sistema debe funcionar offline para funcionalidades básicas
  - Backup automático de datos de la huerta
  - Tolerancia a fallos en APIs externas

- **Compatibilidad:**
  - Navegadores modernos (Chrome 90+, Firefox 88+, Safari 14+)
  - Soporte para dispositivos táctiles
  - Resoluciones desde 1024x768

#### 3.3. Fases de Desarrollo

**Fase 1 - MVP (Funcionalidad Básica)**
- RF-001: Mapa de huerta con canvas
- RF-002: Base de datos básica
- RF-003: Consultas por coordenadas
- RF-005: Cultivos activos básicos

**Fase 2 - Funcionalidades Avanzadas**
- RF-004: Sistema de anotaciones completo
- RF-006: Integración API del clima
- RF-008: Calendario de siembra/cosecha

**Fase 3 - Características Premium**
- RF-007: Calendario lunar
- RF-009: Sugerencias inteligentes
- Optimizaciones de rendimiento

  

## Parte II: Documento de Diseño de Software (SDD)

  

*Fase de SDLC:* Diseño

  

### 4. Diseño de Alto Nivel (High-Level Design - HLD)

  

#### 4.1. Arquitectura General del Sistema

  

- *Descripción de la Arquitectura:* [Describir el patrón arquitectónico seleccionado (ej. Microservicios, Monolítica, Cliente-Servidor) y justificar la elección.]

    Microservicios

- *Diagrama de Arquitectura:* [Insertar un diagrama visual que muestre los componentes principales del sistema y cómo se conectan entre sí.]

  

#### 4.2. Identificación de Componentes Principales

  

- [Listar y describir cada componente principal o módulo definido en la arquitectura. Por ejemplo: Módulo de Autenticación, Módulo de Pagos, API Gateway, Base de Datos de Usuarios, etc.]

Componentes:
- Huerta (mapa, coordenadas, polígonos)
- Hortalizas (base de datos con info de cada cultivo)
- Anotaciones (eventos, fotos, notas)
- Calendario (clima, lunar, siembra/cosecha)
- API Externa (clima)  

#### 4.3. Selección de Plataformas Tecnológicas

- **Lenguaje de Programación:** Python 3.9+
  - Justificación: Ecosistema rico para análisis de datos y APIs

- **Framework Backend:** FastAPI
  - Justificación: Alto rendimiento, documentación automática, typing nativo

- **Frontend:** HTML5 + JavaScript (Vanilla) + Canvas API
  - Justificación: Simplicidad, control total sobre rendering, sin dependencias pesadas

- **Base de Datos:** KuzuDB
  - Justificación: Optimizada para consultas con relaciones complejas, ideal para coordenadas

- **Gestión de Dependencias:** Poetry
  - Justificación: Manejo moderno de dependencias Python

- **Servidor Web:** Uvicorn
  - Justificación: Servidor ASGI de alto rendimiento para FastAPI
  

### 5. Diseño de Bajo Nivel (Low-Level Design - LLD)

  

#### 5.1. Detalle Interno de Módulos

  

- [Para cada componente definido en el HLD, detallar su funcionamiento interno.]

    - *Módulo: [Nombre del Módulo]*

        - *Clases/Objetos Principales:* [Listar las clases y sus responsabilidades.]

        - *Algoritmos Clave:* [Describir cualquier algoritmo complejo que se vaya a implementar.]

        - *Diagramas:* [Insertar diagramas de secuencia o de clases para visualizar la lógica.]

Huerta:
- Clase: Huerta
  - Responsabilidades: Cargar mapa, manejar coordenadas y polígonos.
  - Métodos: cargarMapa(), agregarPoligono(), obtenerPlantaEnCoordenada(x,y)
Hortalizas:
- Clase: Hortaliza
  - Responsabilidades: Gestionar información de cultivos.
  - Métodos: obtenerInfoCultivo(nombre), listarCultivos()
Anotaciones:
- Clase: Anotacion
  - Responsabilidades: Registrar eventos, fotos y notas.
  - Métodos: agregarAnotacion(tipo, fecha, notas, fotos), obtenerAnotacionesPorCultivo(cultivo)
Calendario:
- Clase: Calendario
  - Responsabilidades: Mostrar clima, calendario lunar y de siembra/cosecha.
  - Métodos: obtenerClimaProximo(), mostrarCalendarioLunar(), mostrarCalendarioSiembraCosecha()
API Externa:
- Clase: ApiClima
  - Responsabilidades: Interactuar con la API externa para obtener datos climáticos.
  - Métodos: fetchClima(ciudad), parsearDatosClima(response)
  
  

#### 5.2. Estructura de la Base de Datos

  

- *Esquema de la Base de Datos:* [Insertar un diagrama Entidad-Relación (ERD).]

- *Definición de Tablas/Colecciones:* [Detallar cada tabla, sus columnas, tipos de datos, claves primarias, claves foráneas e índices.]

Tablas:
- Huertas
  - id (PK)
  - nombre
  - instancias de hortalizas (FK)
  - estructuras (polígonos, coordenadas)
- Hortalizas
  - id (PK)
  - nombre
  - descripción
  - tiempos (siembra, cosecha)
  - plagas
  - necesidades/cuidados
  - tamaño/geometría
- Anotaciones
  - id (PK)
  - Niveles de especificidad (tipo de planta, tiempo, individuo, estación)
  - tipo (evento, foto, nota)
  - fecha
  - notas
  - fotos (URL o path)
  - cultivo asociado (FK)
- Calendario
  - id (PK)
  - clima (datos obtenidos de API externa)
  - calendario lunar
  - calendario de siembra/cosecha

#### 5.3. Diseño de API REST

**Endpoints principales:**

```
GET /api/huerta/mapa
- Descripción: Obtiene la configuración del mapa de la huerta
- Respuesta: { "polygons": [...], "dimensions": {...} }

POST /api/huerta/mapa/poligono
- Descripción: Añade un nuevo polígono al mapa
- Body: { "coordinates": [[x,y], ...], "tipo": "cultivo" }

GET /api/huerta/coordenada/{x}/{y}
- Descripción: Consulta qué hay en una coordenada específica
- Respuesta: { "cultivo": {...}, "anotaciones": [...] }

POST /api/cultivos/activos
- Descripción: Inicializa un nuevo cultivo activo
- Body: { "hortaliza_id": 1, "coordenadas": [x,y], "fecha_siembra": "..." }

GET /api/cultivos/tipos
- Descripción: Lista todos los tipos de hortalizas disponibles
- Respuesta: [{ "id": 1, "nombre": "tomate", "ciclo_dias": 120, ... }]
```
