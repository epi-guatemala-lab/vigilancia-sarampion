# Auditoria: Campos de Nombre — Alineacion con GoData Guatemala

**Fecha:** 2026-03-26
**Objetivo:** Determinar si los campos de nombre deben dividirse y como alinear con el modelo de datos de GoData Guatemala.

---

## 1. Como almacena GoData Guatemala los nombres (5 casos reales)

GoData utiliza **3 campos** para nombres:

| visualId | firstName | middleName | lastName |
|----------|-----------|------------|----------|
| SR-0001 | MARIA | SONIA | CAPETILLO LERA |
| SR-0002 | BENJAMIN | ESTUARDO | CONTRERAS ESTRADA |
| SR-0003 | KATERIN | FLORINDA | RAMOS |
| SR-0004 | Gregorio | *(vacio)* | velasquez |
| SR-0005 | CARMEN | LUCIA | VALLADARES SORIA |

**Patron observado:**
- `firstName` = Primer nombre
- `middleName` = Segundo nombre (puede quedar vacio si solo tiene uno)
- `lastName` = Ambos apellidos juntos (ej: "CAPETILLO LERA", "CONTRERAS ESTRADA")

---

## 2. Como almacena nuestra ficha los nombres (estado actual)

### Base de datos (ficha vigilancia-sarampion)
- **2 campos:** `nombres` (texto libre) y `apellidos` (texto libre)
- `nombre_apellido` se computa automaticamente: `nombres + " " + apellidos`

### Frontend (formSchema.js)
- Campo `nombres` — label "Nombres", placeholder "Nombres del paciente"
- Campo `apellidos` — label "Apellidos", placeholder "Apellidos del paciente"
- Ambos `colSpan: 'half'` (lado a lado)

### Ejemplo de datos almacenados
No hay fichas con datos reales aun en la BD de fichas. Los datos del portal principal (`sarampion_casos`) almacenan el nombre completo en un solo campo `nombre_paciente` (ej: "CHRISTOPHER GABRIEL RODRIGUEZ DE LA CRUZ").

---

## 3. Como esperan nombres los sistemas destino

| Sistema | Campos | Formato |
|---------|--------|---------|
| **GoData Guatemala** | `firstName`, `middleName`, `lastName` | 3 campos separados |
| **MSPAS EPIWEB** | `nombres`, `apellidos` | 2 campos (igual que nosotros) |
| **PDF Ficha** | `Nombres`, `Apellidos` | 2 campos (igual que nosotros) |

---

## 4. Evaluacion de opciones

### Opcion A: Mantener 2 campos (actual) + split automatico para GoData

**Flujo:**
- Usuario ingresa: `nombres="CARLOS EDUARDO"`, `apellidos="MARTINEZ GARCIA"`
- Para GoData: split en primer espacio → `firstName="CARLOS"`, `middleName="EDUARDO"`, `lastName="MARTINEZ GARCIA"`
- Para MSPAS: enviar tal cual (ya es el formato correcto)
- Para PDF: enviar tal cual

**Ventajas:**
- Cero cambios en frontend, backend DB, PDF, MSPAS bot
- Solo se necesita logica de split en `godata_field_map.py` (1 archivo)
- Consistente con EPIWEB que es el sistema primario de reporte
- Minima disrupcion al flujo de trabajo actual

**Desventajas:**
- Split automatico puede fallar con nombres compuestos (ej: "MARIA DE LOS ANGELES" — que parte es primer nombre y cual segundo?)
- No captura la intencion del usuario sobre como dividir sus nombres

**Riesgo:** BAJO. En la practica guatemalteca, la gran mayoria de personas tienen 2 nombres y 2 apellidos. El split en primer espacio funciona correctamente para 4/5 de los casos reales en GoData.

### Opcion B: Dividir en 4 campos

**Flujo:**
- Usuario ingresa: `primer_nombre`, `segundo_nombre`, `primer_apellido`, `segundo_apellido`
- Para GoData: mapeo directo 1:1
- Para MSPAS: concatenar `primer_nombre + " " + segundo_nombre` y `primer_apellido + " " + segundo_apellido`
- Para PDF: concatenar igual

**Ventajas:**
- Mapeo perfecto a GoData
- Maxima granularidad de datos

**Desventajas:**
- Cambios en: frontend (formSchema.js), backend (database.py, schema), godata_field_map.py, mspas_field_map.py, mspas_bot.py, pdf_ficha_v2.py
- Mas campos para el usuario (4 en vez de 2) — mas friccion
- Necesita migracion de datos si hay fichas existentes
- No se alinea con EPIWEB (que usa 2 campos)
- El segundo nombre es opcional y muchos pacientes no lo tienen

### Opcion C: 3 campos (nombres + primer_apellido + segundo_apellido)

**Ventajas:**
- Los apellidos se mapean mejor a GoData lastName
- Nombres se mantiene como campo libre

**Desventajas:**
- Mismos problemas de Opcion B pero sin resolver el split de nombres para GoData
- Inconsistente con EPIWEB
- Cambios moderados en multiples archivos

---

## 5. Recomendacion: OPCION A (mantener 2 campos + split automatico)

### Justificacion

1. **EPIWEB es el sistema primario.** La ficha MSPAS usa exactamente 2 campos (`nombres`, `apellidos`). Alinearse con EPIWEB es la prioridad porque es obligatorio; GoData es complementario.

2. **GoData acepta nombres concatenados en lastName.** Los 5 casos reales confirman que `lastName` puede contener 2 apellidos juntos ("CAPETILLO LERA"). No hay separacion de apellidos en GoData.

3. **El split automatico funciona bien.** De los 5 casos existentes en GoData, 4 de 5 tienen el patron [primer_nombre] + [segundo_nombre] que se resuelve con split en primer espacio. El caso SR-0004 (solo "Gregorio" + "velasquez") demuestra que middleName vacio es valido.

4. **Minimo impacto.** Solo requiere modificar `godata_field_map.py` lineas 576-577:

```python
# Actual:
"firstName": _godata_text(_get(d, "nombres")),
"lastName": _godata_text(_get(d, "apellidos")),

# Propuesto:
nombres = _godata_text(_get(d, "nombres"))
parts = nombres.split(" ", 1) if nombres else [""]
"firstName": parts[0],
"middleName": parts[1] if len(parts) > 1 else "",
"lastName": _godata_text(_get(d, "apellidos")),
```

5. **Calidad de datos aceptable.** Para los pocos casos donde el split falle (nombres compuestos como "MARIA DE LOS ANGELES"), el resultado en GoData seria `firstName="MARIA"`, `middleName="DE LOS ANGELES"` — que es aceptable y corregible manualmente en GoData si necesario.

6. **Flujo de trabajo IGSS.** Los medicos del IGSS estan acostumbrados a escribir nombres y apellidos en 2 campos. Forzar 4 campos agrega friccion innecesaria.

### Implementacion requerida

| Archivo | Cambio | Esfuerzo |
|---------|--------|----------|
| `godata_field_map.py` L576-577 | Split `nombres` en `firstName` + `middleName` | 5 min |
| Tests | Verificar mapeo con nombres de 1, 2 y 3+ palabras | 10 min |

**Total estimado: 15 minutos.**

No se requieren cambios en: frontend, database.py, mspas_field_map.py, mspas_bot.py, pdf_ficha_v2.py.

---

## 6. Casos borde a manejar

| Input nombres | firstName | middleName | Correcto? |
|---------------|-----------|------------|-----------|
| "CARLOS" | CARLOS | "" | Si |
| "CARLOS EDUARDO" | CARLOS | EDUARDO | Si |
| "MARIA DE LOS ANGELES" | MARIA | DE LOS ANGELES | Aceptable |
| "" (vacio) | "" | "" | Si (GoData permite vacio) |
| "JUAN CARLOS JOSE" | JUAN | CARLOS JOSE | Aceptable (GoData middleName es texto libre) |
