# Auditoria de Campos de Texto Abierto vs. Selects Cerrados

**Fecha:** 2026-03-26
**Fuentes cruzadas:** Formulario IGSS formSchema.js, GoData Guatemala (API live), ficha MSPAS EPIWEB

---

## Resumen Ejecutivo

Se auditaron los **50 campos tipo `text`/`textarea`** del formulario de vigilancia de sarampion. De estos:

- **12 campos** deben convertirse a `select` (lista cerrada)
- **3 campos** deben convertirse a `searchable-select` (lista grande con busqueda)
- **6 campos** son correctos como `text` pero con observaciones
- **29 campos** son correctos como `text`/`textarea` (datos libres, especificaciones, numericos, etc.)

---

## Tabla Completa: Analisis de cada campo text/textarea

### Leyenda
- **RO** = readOnly (auto-calculado, no requiere cambio)
- **COND** = condicional (solo aparece si se cumple condicion)
- MANTENER = correcto como esta
- CAMBIAR = debe convertirse a select/searchable-select

| # | Tab | Field ID | Label | Flags | GoData tiene opciones? | MSPAS tiene opciones? | Recomendacion |
|---|-----|----------|-------|-------|----------------------|---------------------|---------------|
| 1 | 1 | `codigo_cie10` | Codigo CIE-10 | RO | N/A | N/A | **MANTENER** — auto-asignado desde diagnostico_registrado |
| 2 | 1 | `diagnostico_sospecha_otro` | Especifique diagnostico de sospecha | COND | No (FREE_TEXT) | No | **MANTENER** — texto libre para especificar "otro" |
| 3 | 1 | `unidad_medica_otra` | Especifique la unidad medica | COND | No (FREE_TEXT) | No | **MANTENER** — overflow para unidades no listadas |
| 4 | 1 | `establecimiento_privado_nombre` | (nombre establecimiento privado) | | No (FREE_TEXT) | No | **MANTENER** — miles de posibles establecimientos privados |
| 5 | 1 | `nom_responsable` | Responsable de Notificacion | | GoData: FREE_TEXT | No | **MANTENER** — personal cambia frecuentemente |
| 6 | 1 | `cargo_responsable` | Cargo | | GoData: FREE_TEXT | No | **CAMBIAR a select** — conjunto finito de cargos en epidemiologia |
| 7 | 1 | `correo_responsable` | Correo Electronico | | GoData: FREE_TEXT | No | **MANTENER** — texto libre (email) |
| 8 | 1 | `fuente_notificacion_otra` | Otra fuente de notificacion | COND | No (FREE_TEXT) | No | **MANTENER** — overflow para "Otra" |
| 9 | 1 | `busqueda_activa_otra` | Otra busqueda activa | COND | No | No | **MANTENER** — overflow para "Otra" |
| 10 | 2 | `afiliacion` | Numero de Afiliacion | | N/A | N/A | **MANTENER** — identificador numerico |
| 11 | 2 | `numero_identificacion` | Numero de Identificacion | | N/A | N/A | **MANTENER** — identificador numerico |
| 12 | 2 | `nombres` | Nombres | | N/A | N/A | **MANTENER** — nombre propio |
| 13 | 2 | `apellidos` | Apellidos | | N/A | N/A | **MANTENER** — nombre propio |
| 14 | 2 | `comunidad_linguistica` | Comunidad Linguistica | | **SI — 22 idiomas mayas + "No indica"** | SI (23 comunidades) | **CAMBIAR a select** — lista cerrada oficial MSPAS |
| 15 | 2 | `pais_residencia` | Pais de Residencia | | GoData: SINGLE_ANSWER (Guatemala/Otro) | SI | **CAMBIAR a searchable-select** — lista de paises |
| 16 | 2 | `direccion_exacta` | Direccion | | GoData: FREE_TEXT | No | **MANTENER** — direccion libre |
| 17 | 2 | `nombre_encargado` | Nombre de la madre, padre o encargado | | N/A | N/A | **MANTENER** — nombre propio |
| 18 | 2 | `numero_id_tutor` | Numero de Identificacion del Encargado | | N/A | N/A | **MANTENER** — identificador numerico |
| 19 | 4 | `observaciones_vacuna` | Observaciones de Vacunacion | COND | No | No | **MANTENER** — narrativa clinica |
| 20 | 4 | `antecedentes_medicos_detalle` | Detalle de antecedentes medicos | COND | GoData: FREE_TEXT | No | **MANTENER** — narrativa clinica |
| 21 | 5 | `sitio_inicio_erupcion_otro` | Otro sitio de erupcion | COND | No | No | **MANTENER** — overflow para "Otro" |
| 22 | 5 | `temperatura_celsius` | Temperatura C | | GoData: NUMERIC | No | **MANTENER** — valor numerico (considerar type:'number') |
| 23 | 5 | `hosp_nombre` | Nombre del Hospital | COND | GoData: FREE_TEXT | No | **CAMBIAR a searchable-select** — usar lista unidadesMedicas + "OTRO" |
| 24 | 5 | `no_registro_medico` | No. de Registro Medico | COND | N/A | N/A | **MANTENER** — identificador numerico |
| 25 | 5 | `medico_certifica_defuncion` | Medico que Certifica Defuncion | COND | N/A | No | **MANTENER** — nombre propio |
| 26 | 5 | `motivo_consulta` | Motivo de Consulta / Observaciones Clinicas | | No | No | **MANTENER** — narrativa clinica (textarea) |
| 27 | 5 | `comp_otra_texto` | Otra complicacion | COND | GoData: FREE_TEXT | No | **MANTENER** — overflow para "Otra" |
| 28 | 6 | `viaje_pais` | Pais de Destino del Viaje | COND | GoData: FREE_TEXT | SI (lista paises) | **CAMBIAR a searchable-select** — lista de paises |
| 29 | 6 | `viaje_departamento` | Departamento de Destino | COND | GoData: SINGLE_ANSWER (22 deptos) | SI (22 deptos) | **CAMBIAR a select** — cascada desde viaje_pais=Guatemala |
| 30 | 6 | `viaje_municipio` | Municipio de Destino | COND | GoData: cascading select | SI (cascada) | **CAMBIAR a select** — cascada desde viaje_departamento |
| 31 | 6 | `destino_viaje` | A donde viajo? (legacy) | COND | N/A | N/A | **ELIMINAR** — campo legacy, reemplazado por viaje_pais/depto/muni |
| 32 | 6 | `fuente_contagio_otro` | Otra fuente de contagio | COND | GoData: FREE_TEXT | No | **MANTENER** — overflow para "Otro" |
| 33 | 8 | `motivo_no_recoleccion` | Por que no se recolecto la muestra? | COND | No | SI (opciones MSPAS) | **CAMBIAR a select** — motivos estandarizados |
| 34 | 8 | `muestra_otra_descripcion` | Descripcion Otra Muestra | COND | No | No | **MANTENER** — overflow para "Otra" |
| 35 | 8 | `antigeno_otro` | Otro Antigeno | COND | No | No | **MANTENER** — overflow para "Otro" |
| 36 | 8 | `resultado_igg_numerico` | Resultado IgG Numerico | COND | N/A | N/A | **MANTENER** — valor numerico de laboratorio |
| 37 | 8 | `resultado_igm_numerico` | Resultado IgM Numerico | COND | N/A | N/A | **MANTENER** — valor numerico de laboratorio |
| 38 | 8 | `motivo_no_3_muestras` | Motivo por el que no se tomaron 3 muestras | COND | No | No | **CAMBIAR a select** — motivos estandarizados |
| 39 | 8 | `secuenciacion_resultado` | Resultado de Secuenciacion | | No | No | **CAMBIAR a select** — genotipos conocidos de sarampion/rubeola |
| 40 | 9 | `pais_importacion` | Pais de Importacion | COND | GoData: FREE_TEXT | SI (lista paises) | **CAMBIAR a searchable-select** (misma lista de paises) |
| 41 | 9 | `contacto_otro_caso_detalle` | Detalle del contacto con otro caso | COND | No | No | **MANTENER** — texto libre de detalle |
| 42 | 9 | `caso_analizado_por_otro` | Especifique quien analizo el caso | COND | No | No | **MANTENER** — overflow para "Otros" |
| 43 | 9 | `responsable_clasificacion` | Responsable de Clasificacion | | N/A | No | **MANTENER** — nombre propio |
| 44 | 9 | `causa_muerte_certificado` | Causa de Muerte en Certificado | COND | GoData: FREE_TEXT | No | **MANTENER** — narrativa clinica |
| 45 | 9 | `observaciones` | Observaciones | | No | No | **MANTENER** — narrativa libre (textarea) |
| 46 | 9 | `puesto_desempena` | Puesto que Desempena | COND | GoData: ocupacion FREE_TEXT | No | **CAMBIAR a select** — puestos IGSS son finitos |
| 47 | 9 | `subgerencia_igss_otra` | Especifique Subgerencia | COND | N/A | N/A | **MANTENER** — overflow para organigrama IGSS |
| 48 | 9 | `direccion_igss_otra` | Especifique Direccion | COND | N/A | N/A | **MANTENER** — overflow para organigrama IGSS |
| 49 | 9 | `departamento_igss_otro` | Especifique Departamento | COND | N/A | N/A | **MANTENER** — overflow para organigrama IGSS |
| 50 | 9 | `seccion_igss_otra` | Especifique Seccion | COND | N/A | N/A | **MANTENER** — overflow para organigrama IGSS |

---

## Campos a Convertir: Listas de Opciones Completas

### 1. `comunidad_linguistica` — Texto a Select

**Fuente:** GoData Guatemala (22 idiomas mayas) + MSPAS oficial

**Condicion:** Solo visible cuando `pueblo_etnia` = "Maya"

**Opciones (23 + 1):**
```javascript
[
  'Achi',
  'Akateka',
  'Awakateka',
  'Chalchiteka',
  'Ch\'orti\'',
  'Chuj',
  'Itza\'',
  'Ixil',
  'Jakalteka',
  'Kaqchikel',
  'K\'iche\'',
  'Mam',
  'Mopan',
  'Poqomam',
  'Poqomchi\'',
  'Q\'anjob\'al',
  'Q\'eqchi\'',
  'Sakapulteka',
  'Sipakapense',
  'Tektiteka',
  'Tz\'utujil',
  'Uspanteka',
  'No indica',
]
```

**Nota:** Estos son los 22 idiomas mayas reconocidos por la Academia de Lenguas Mayas de Guatemala, exactamente como aparecen en GoData Guatemala. Cuando `pueblo_etnia` es Garifuna, Xinca o Ladino, el campo no aplica.

---

### 2. `cargo_responsable` — Texto a Select

**Fuente:** Puestos tipicos en areas de epidemiologia IGSS/MSPAS

**Opciones:**
```javascript
[
  'Epidemiologo/a',
  'Medico/a de Area',
  'Medico/a Residente',
  'Enfermero/a Profesional',
  'Enfermero/a Auxiliar',
  'Tecnico/a en Salud',
  'Inspector/a de Saneamiento',
  'Director/a de Area',
  'Coordinador/a de Vigilancia',
  'Otro',
]
```

---

### 3. `pais_residencia` — Texto a Searchable Select

**Fuente:** Lista ISO 3166-1 de paises (misma que `viaje_pais` y `pais_importacion`)

**Implementacion:** Crear un archivo `mspasPaises.js` con lista de ~200 paises en espanol, con Guatemala como default/primera opcion.

**Opciones (extracto, los principales para Guatemala):**
```javascript
[
  'GUATEMALA',           // default
  'MEXICO',
  'ESTADOS UNIDOS',
  'EL SALVADOR',
  'HONDURAS',
  'BELICE',
  'NICARAGUA',
  'COSTA RICA',
  'PANAMA',
  'COLOMBIA',
  'VENEZUELA',
  // ... resto de paises del mundo en orden alfabetico
  'OTRO / NO ESPECIFICADO',
]
```

---

### 4. `viaje_pais` — Texto a Searchable Select

**Misma lista que `pais_residencia`** (reutilizar `mspasPaises.js`)

---

### 5. `viaje_departamento` — Texto a Select (cascada)

**Condicion:** Solo visible cuando `viaje_pais` = "GUATEMALA"

**Fuente:** Ya existe `departamentosGuatemala` en el formulario (22 departamentos). Reutilizar.

**Opciones:** Las 22 departamentos de Guatemala (ya importados de `mspasMunicipios.js`)

---

### 6. `viaje_municipio` — Texto a Select (cascada)

**Condicion:** Solo visible cuando `viaje_departamento` tiene valor

**Fuente:** Ya existe `getMunicipios(departamento)` en el formulario. Reutilizar cascada existente.

---

### 7. `pais_importacion` — Texto a Searchable Select

**Misma lista que `pais_residencia`** (reutilizar `mspasPaises.js`)

---

### 8. `hosp_nombre` — Texto a Searchable Select

**Fuente:** Lista `unidadesMedicasNombres` ya importada en el formulario + opcion "OTRO"

**Implementacion:**
```javascript
options: [...unidadesMedicasNombres, 'HOSPITAL NACIONAL', 'CENTRO DE SALUD', 'CLINICA PRIVADA', 'OTRO'],
```

Con campo de texto condicional `hosp_nombre_otro` cuando se seleccione "OTRO".

---

### 9. `motivo_no_recoleccion` — Texto a Select

**Fuente:** Motivos estandarizados de la ficha MSPAS

**Opciones:**
```javascript
[
  'Paciente se nego',
  'Paciente no localizado',
  'Muestra inadecuada',
  'Sin insumos',
  'Fuera de periodo optimo',
  'Ya se tomo muestra previa adecuada',
  'Otro',
]
```

---

### 10. `motivo_no_3_muestras` — Texto a Select

**Fuente:** Motivos estandarizados OPS/MSPAS

**Opciones:**
```javascript
[
  'Paciente se nego a toma adicional',
  'Paciente no localizado',
  'Caso descartado antes de completar muestras',
  'Sin insumos para toma de muestra',
  'Muestra previa fue suficiente para diagnostico',
  'Paciente fallecido',
  'Otro',
]
```

---

### 11. `secuenciacion_resultado` — Texto a Select

**Fuente:** Genotipos conocidos de sarampion y rubeola (OMS)

**Opciones:**
```javascript
[
  // Genotipos Sarampion (activos OMS 2024)
  'B3',
  'D4',
  'D8',
  'H1',
  // Genotipos Rubeola (activos OMS)
  '1E',
  '2B',
  // Resultados
  'Pendiente',
  'No se realizo secuenciacion',
  'Muestra inadecuada para secuenciacion',
  'Genotipo no determinado',
]
```

---

### 12. `puesto_desempena` — Texto a Select

**Fuente:** GoData Guatemala tiene 24 ocupaciones. Para IGSS, los puestos de afiliados son mas especificos.

**Opciones (combinacion GoData + IGSS):**
```javascript
[
  'Operativo/a',
  'Administrativo/a',
  'Profesional de Salud',
  'Docente',
  'Estudiante',
  'Obrero/a',
  'Agricultor/a',
  'Comerciante',
  'Seguridad',
  'Limpieza/Mantenimiento',
  'Transporte',
  'Maquila',
  'Construccion',
  'Hoteleria/Restaurante',
  'Call Center/Oficina',
  'Ama de Casa',
  'Jubilado/a',
  'Menor de Edad',
  'Desempleado/a',
  'Otro',
]
```

---

### 13. `destino_viaje` (legacy) — ELIMINAR

Este campo es redundante. Ha sido reemplazado por la combinacion `viaje_pais` + `viaje_departamento` + `viaje_municipio`. Se recomienda:
1. Mantenerlo oculto en el schema (`hidden: true`)
2. No mostrarlo en nuevos formularios
3. Migrar datos existentes a los campos nuevos

---

## Referencia: Ocupaciones en GoData Guatemala (24 opciones)

Obtenidas via API `GET /reference-data?categoryId=LNG_REFERENCE_DATA_CATEGORY_OCCUPATION`:

| Codigo GoData | Traduccion |
|--------------|------------|
| ALBANIL | Albanil |
| BUTCHER | Carnicero |
| CALL_CENTER | Call Center |
| CHILD | Menor de Edad |
| CIVIL_SERVANT | Servidor Publico |
| DEPENDIENTE_DE_TIENDA | Dependiente de Tienda |
| FARMER | Agricultor |
| FORESTRY | Forestal |
| HEALTH_CARE_WORKER | Trabajador de Salud |
| HEALTH_LABORATORY_WORKER | Laboratorista |
| HOTELERIA | Hoteleria |
| HOTELERIA_RESTAURANTE | Hoteleria/Restaurante |
| LIMPIEZA_DOMESTICA | Limpieza Domestica |
| MAQUILA | Maquila |
| MINING | Mineria |
| OFICINA | Oficina |
| OTHER | Otro |
| RELIGIOUS_LEADER | Lider Religioso |
| STUDENT | Estudiante |
| TAXI_DRIVER | Taxista |
| TEACHER | Docente |
| TRADITIONAL_HEALER | Curandero Tradicional |
| UNKNOWN | Desconocido |
| WORKING_WITH_ANIMALS | Trabajo con Animales |

**Nota:** Nuestro formulario ya tiene `ocupacion` como `searchable-select` con 441 opciones MSPAS. Este campo es para clasificacion general del puesto IGSS, distinto de la ocupacion detallada MSPAS.

---

## Campos de Texto Correctamente Abiertos (no cambiar)

Los siguientes campos son correctos como texto libre por su naturaleza:

### Identificadores / Nombres propios
- `afiliacion`, `numero_identificacion`, `nombres`, `apellidos`, `nombre_encargado`, `numero_id_tutor`, `no_registro_medico`

### Narrativa clinica
- `motivo_consulta` (textarea), `antecedentes_medicos_detalle`, `causa_muerte_certificado`, `observaciones` (textarea), `observaciones_vacuna`

### Especificaciones "Otro" (overflow de selects)
- `diagnostico_sospecha_otro`, `unidad_medica_otra`, `fuente_notificacion_otra`, `busqueda_activa_otra`, `sitio_inicio_erupcion_otro`, `comp_otra_texto`, `fuente_contagio_otro`, `muestra_otra_descripcion`, `antigeno_otro`, `caso_analizado_por_otro`, `contacto_otro_caso_detalle`
- `subgerencia_igss_otra`, `direccion_igss_otra`, `departamento_igss_otro`, `seccion_igss_otra`

### Numericos / Automaticos
- `codigo_cie10` (auto-asignado, readonly)
- `resultado_igg_numerico`, `resultado_igm_numerico` (valores de laboratorio)
- `temperatura_celsius` (considerar cambiar a type:'number')

### Datos de contacto
- `nom_responsable`, `correo_responsable`, `responsable_clasificacion`, `medico_certifica_defuncion`, `establecimiento_privado_nombre`

---

## Observaciones Adicionales

### Campo `temperatura_celsius`
Actualmente es `type: 'text'`. Deberia ser `type: 'number'` con `min: 35.0`, `max: 42.0`, `step: 0.1` para evitar entradas no numericas.

### Campo `resultado_igg_numerico` y `resultado_igm_numerico`
Actualmente son `type: 'text'`. Deberian ser `type: 'number'` con `step: 0.01` para valores de titulacion.

### Campos `subgerencia_igss_otra`, `direccion_igss_otra`, etc.
Estos campos de overflow del organigrama IGSS podrian eliminarse si el organigrama en `igssOrganizacion.js` se mantiene actualizado con una opcion "OTRA" que abra un campo libre. Verificar si ya existe esa logica.

---

## Prioridades de Implementacion

### Alta prioridad (mayor impacto en calidad de datos)
1. `comunidad_linguistica` — 22 idiomas mayas es una lista cerrada oficial
2. `viaje_departamento` / `viaje_municipio` — cascada ya existe, solo conectar
3. `hosp_nombre` — reutilizar `unidadesMedicasNombres` existente
4. `secuenciacion_resultado` — genotipos OMS son finitos y criticos

### Media prioridad
5. `pais_residencia` / `viaje_pais` / `pais_importacion` — crear `mspasPaises.js` una vez
6. `motivo_no_recoleccion` / `motivo_no_3_muestras` — estandarizar motivos
7. `puesto_desempena` — reducir variabilidad en datos IGSS

### Baja prioridad
8. `cargo_responsable` — pocos usuarios llenan esto
9. Cambiar `temperatura_celsius` a type:'number'
10. Eliminar campo legacy `destino_viaje`
