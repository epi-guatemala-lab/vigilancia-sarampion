# Auditoria Profunda: Modulo GoData — 2026-03-27

## Archivos Auditados

| Archivo | Lineas | Rol |
|---------|--------|-----|
| `backend/godata_client.py` | 270 | Cliente REST GoData API |
| `backend/godata_field_map.py` | 1287 | Mapeo BD local -> GoData Guatemala payload |
| `backend/godata_queue.py` | 357 | Cola de sincronizacion SQLite |
| `backend/main.py` (lineas 1325-1524) | ~200 | Endpoints FastAPI GoData |
| `visor_formulario_web.py` (lineas 1766-2300) | ~530 | UI Streamlit tab GoData |
| `api_client.py` (lineas 362-521) | ~160 | Cliente HTTP Streamlit -> FastAPI |
| `backend/pdf_ficha_v2.py` | 1040 | Generacion PDF ficha MSPAS 2026 |

---

## 1. BUGS ENCONTRADOS

### CRITICO-01: Backend /api/godata/test ignora credenciales del request body

**Archivo**: `backend/main.py:1351-1359`
**Severidad**: CRITICO

El frontend (`api_client.py:392-417`) envia credenciales en el body del POST (godata_url, username, password, outbreak_id) para permitir probar ANTES de guardar. Pero el backend ignora el body completamente y lee de la BD guardada:

```python
# Backend (main.py:1351-1359)
@app.post("/api/godata/test")
def godata_test_connection(x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    url, user, pwd, outbreak_id = get_godata_credentials()  # <-- lee de BD, ignora body
    if not url:
        raise HTTPException(400, "GoData no esta configurado")
    client = GoDataClient(...)
    return client.test_connection()
```

**Impacto**: No se puede probar la conexion antes de guardar. Si no hay config guardada, siempre devuelve 400. El flujo del UI (probar -> seleccionar outbreak -> guardar) esta completamente roto.

**Fix**: El endpoint debe leer `await request.json()`, usar esas credenciales si vienen, y caer a las guardadas como fallback.

---

### CRITICO-02: Backend /api/godata/test devuelve formato incompatible con frontend

**Archivo**: `backend/godata_client.py:143-154` vs `visor_formulario_web.py:1871-1882`
**Severidad**: CRITICO

El cliente `GoDataClient.test_connection()` devuelve:
```python
{"status": "ok", "authenticated": True, "outbreak_count": 0}
```

Pero el frontend espera:
```python
result.get("success")           # No existe, siempre falsy
result.get("outbreaks", [])     # No existe
result.get("message", ...)      # No existe
result.get("current_user")      # No existe
result.get("current_outbreak")  # No existe
```

**Impacto**: El test de conexion SIEMPRE muestra "Conexion fallida" en el UI aunque funcione. Los outbreaks nunca se descubren. El selector de outbreaks nunca se puebla.

**Fix**: El endpoint `/api/godata/test` debe: (1) autenticarse, (2) listar outbreaks, (3) obtener info del usuario actual, (4) devolver `{"success": True, "outbreaks": [...], "current_user": {...}, "current_outbreak": {...}, "message": "..."}`.

---

### CRITICO-03: 4 endpoints del API client no tienen backend correspondiente

**Archivo**: `api_client.py:419-434`
**Severidad**: CRITICO

Los siguientes metodos del frontend no tienen endpoints en `main.py`:

| Metodo api_client | Ruta esperada | Existe en main.py? |
|---|---|---|
| `godata_get_outbreaks()` | GET /api/godata/outbreaks | NO |
| `godata_get_users()` | GET /api/godata/users | NO |
| `godata_get_templates()` | GET /api/godata/templates | NO |
| `godata_get_reference_data()` | GET /api/godata/reference-data | NO |

**Impacto**: El expander "Exploracion GoData" en el UI (lineas 1961-1984) falla con HTTP 404/405 cuando se presiona "Cargar usuarios" o "Cargar templates". El selector de outbreaks descubiertos depende de `/api/godata/test` que tampoco devuelve outbreaks.

**Fix**: Crear los 4 endpoints en main.py, cada uno usando `GoDataClient` para proxear la llamada al servidor GoData real.

---

### WARNING-01: `_get` y `_post` no devuelven valor tras `_handle_http_error`

**Archivo**: `backend/godata_client.py:84-104`
**Severidad**: WARNING

```python
def _get(self, url, params=None):
    ...
    except requests.HTTPError as e:
        self._handle_http_error(e)  # raises, pero no tiene `return`
```

Si `_handle_http_error` NO lanza (por un error inesperado interno), la funcion devuelve `None` implicitamente. Esto causaria `TypeError: 'NoneType' is not subscriptable` en callers que hacen `.get()` sobre el resultado.

Mismo problema en `_post` y `_put`.

**Fix**: Cambiar a `raise self._handle_http_error(e)` o asegurar que `_handle_http_error` SIEMPRE lance.

Nota: Actualmente `_handle_http_error` siempre lanza, pero si se agrega un nuevo `except` interno, podria silenciar errores. Es un patrn fragil.

---

### WARNING-02: `acciones_de_respuesta` envia `[{}]` cuando no hay acciones

**Archivo**: `backend/godata_field_map.py:1050`
**Severidad**: WARNING

```python
if has_any_action:
    qa["acciones_de_respuesta"] = _qa_val("SI")
else:
    qa["acciones_de_respuesta"] = [{}]  # <-- valor invalido
```

`_qa_val()` devuelve `[{"value": X}]`. La alternativa envia `[{}]` (dict vacio sin key "value"), que GoData probablemente rechaza o ignora con error silencioso.

**Fix**: Usar `_qa_val("NO")` o no incluir la variable cuando no hay acciones.

---

### WARNING-03: `temperatura_celsius` llama `.replace(",", ".")` sobre string potencialmente vacio

**Archivo**: `backend/godata_field_map.py:912`
**Severidad**: WARNING (bajo riesgo)

```python
temp = _get(d, "temperatura_celsius").replace(",", ".")
```

Si `_get` devuelve `""`, `.replace(",", ".")` devuelve `""`, y luego `_safe_float("")` devuelve `None`. Funciona correctamente pero es inconsistente con el patron de otros campos que verifican antes de operar.

---

### WARNING-04: Batch sync en main.py no usa `try_claim_for_sync` atomicamente antes de `find_case_by_visual_id`

**Archivo**: `backend/main.py:1463-1497`
**Severidad**: WARNING

En el batch sync:
```python
for registro_id in ids:
    if not try_claim_for_sync(registro_id):  # atomico
        continue
    record = get_registro_by_id(registro_id)
    existing = client.find_case_by_visual_id(registro_id)  # HTTP call, puede ser lento
    ...
```

Si dos workers ejecutan batch sync simultaneamente, ambos podrian reclamar registros diferentes (correcto), pero el `find_case_by_visual_id` agrega latencia significativa (una llamada HTTP por registro). No hay timeout global para el batch.

**Fix**: Agregar un timeout total al batch loop y considerar rate limiting.

---

### WARNING-05: Enriquecimiento de cola carga TODOS los registros (hasta 5000)

**Archivo**: `visor_formulario_web.py:2053`
**Severidad**: WARNING (performance)

```python
registros_resp = client.get_registros(limit=5000)
```

Para enriquecer la cola con nombres de pacientes, descarga hasta 5000 registros completos. Si la tabla crece, esto sera lento. Los nombres ya vienen en el JOIN de `godata_queue.get_queue()` (campos `nombres`, `apellidos`).

**Fix**: Usar los campos `nombres`/`apellidos` que ya vienen del LEFT JOIN en `get_queue()` en vez de hacer una segunda llamada.

---

### WARNING-06: `recover_stuck_syncs` usa concatenacion de string para SQL datetime

**Archivo**: `backend/godata_queue.py:329-341`
**Severidad**: WARNING (bajo)

```python
conn.execute("""
    UPDATE godata_queue
    SET estado = 'aprobado'
    WHERE estado = 'sincronizando'
      AND updated_at < datetime('now', ? || ' minutes')
""", (f"-{max_age_minutes}",))
```

Funciona correctamente pero el patron `? || ' minutes'` es inusual. SQLite lo acepta, pero es mas claro usar `'-' || ? || ' minutes'` con el valor positivo, o directamente `datetime('now', '-60 minutes')`.

---

### INFO-01: `import json` repetido dentro de metodos

**Archivo**: `backend/godata_client.py:201, 213, 257, 268`
**Severidad**: INFO

`json` se importa localmente dentro de `get_cases`, `find_case_by_visual_id`, `get_locations`, y `get_reference_data`. Deberia importarse al inicio del archivo.

---

### INFO-02: `_strip_accents` importa `unicodedata` cada vez que se llama

**Archivo**: `backend/godata_field_map.py:428`
**Severidad**: INFO (micro-optimization)

```python
def _strip_accents(text):
    import unicodedata  # <-- import dentro de funcion
```

Se llama decenas de veces por registro. Mover a import global.

---

### INFO-03: Lab legacy mapping usa mismo `tested_for` para todos los tests

**Archivo**: `backend/godata_field_map.py:1248`
**Severidad**: INFO

```python
tested_for = "MEASLES" if antigeno == "Sarampion" else "RUBELLA" if antigeno == "Rubeola" else "MEASLES"
```

Si el paciente tiene labs para ambos virus (IgM sarampion + IgM rubeola), el legacy mapper solo puede enviar uno. El mapper JSON (`map_lab_samples_to_godata`) maneja esto correctamente.

---

### INFO-04: PDF generation duplica codigo de page setup

**Archivo**: `backend/pdf_ficha_v2.py:819-826 y 869-875`
**Severidad**: INFO

El bloque de page setup (orientation, paperSize, fitToWidth, fitToHeight, printArea) se repite identicamente en `generar_ficha_v2_pdf` y en el loop de `generar_fichas_v2_bulk`. Deberia extraerse a una funcion helper.

---

## 2. INCONSISTENCIAS FRONTEND-BACKEND

### INC-01: Flujo test_connection completamente desacoplado

| Aspecto | Frontend (api_client) | Backend (main.py) |
|---------|----------------------|-------------------|
| Envia credenciales en body | SI (godata_url, username, password, outbreak_id) | NO (las ignora) |
| Espera `success` en respuesta | SI | NO (devuelve `status`) |
| Espera `outbreaks` en respuesta | SI (para selector) | NO (no lista outbreaks) |
| Espera `current_user` | SI | NO |
| Espera `current_outbreak` | SI | NO |

### INC-02: godata_config save no devuelve `message`

El frontend (`visor:1950`) muestra `result.get("message", "Configuracion guardada")`. El backend devuelve `{"status": "ok"}` sin `message`. Funciona por el default pero es inconsistente.

### INC-03: godata_config no incluye production_mode en save

El frontend muestra production_mode en el caption, pero `save_godata_config()` no acepta ni guarda un parametro `production_mode`. El campo existe en la tabla pero nunca se actualiza desde el UI.

### INC-04: Cola GoData query trae `nombres`/`apellidos` del JOIN pero el UI los ignora

El `get_queue()` de `godata_queue.py:178-179` hace `LEFT JOIN registros r` y trae `r.nombres, r.apellidos`. Pero `visor_formulario_web.py:2053-2065` descarta esos campos y descarga TODOS los registros para construir un `nombre_map` separado.

---

## 3. PROBLEMAS DE SEGURIDAD

### SEC-01: godata_config guarda password con Fernet pero la key puede ser debil (MEDIO)

`save_godata_config` importa `_get_fernet()` de `mspas_queue`. Si la key de Fernet se genera de una fuente debil o se pierde, los passwords quedan irrecuperables. No hay rotacion de keys ni fallback.

### SEC-02: Password GoData se transmite en plaintext entre frontend Streamlit y backend FastAPI (BAJO)

La comunicacion es localhost (127.0.0.1:8510) asi que el riesgo es bajo, pero si algun dia se expone externamente, el password viaja en JSON sin TLS adicional.

### SEC-03: No hay rate limiting en endpoints de sync (BAJO)

Un usuario puede disparar batch sync repetidamente. El `try_claim_for_sync` protege contra duplicados pero no contra sobrecarga del servidor GoData externo.

### SEC-04: Error messages pueden exponer URLs/credenciales internas (MEDIO)

En `godata_client.py:127`:
```python
raise RuntimeError(f"GoData HTTP {status}: {detail}")
```

Si GoData devuelve un error verbose, el mensaje se propaga al UI. Esto podria exponer paths internos del servidor GoData.

---

## 4. FEATURES FALTANTES

### FALT-01: No hay endpoint para outbreak selector (CRITICO para UX)

El UI tiene un selector de outbreaks (`godata_outbreak_select`) pero depende de que `/api/godata/test` devuelva outbreaks, lo cual no hace. No hay `/api/godata/outbreaks` endpoint.

**Necesario**: Endpoint `GET /api/godata/outbreaks` que llame a `GoDataClient.get_outbreaks()`.

### FALT-02: No hay endpoint para usuarios GoData

El UI tiene boton "Cargar usuarios GoData" pero no hay `GET /api/godata/users`.

**Necesario**: Endpoint que llame a `GoDataClient` con un endpoint de users de GoData. Nota: GoData API no tiene `/users` directo para usuarios normales; podria necesitar `/api/users` si el usuario tiene permisos admin.

### FALT-03: No hay endpoint para templates GoData

El UI tiene boton "Cargar templates GoData" pero no hay `GET /api/godata/templates`.

**Necesario**: Endpoint que proxee a GoData. GoData tiene `/api/outbreaks/{id}/case-questionnaires` o similar.

### FALT-04: No hay endpoint para reference data

`api_client.godata_get_reference_data()` no tiene backend.

### FALT-05: No hay toggle de production_mode desde el UI

El campo `production_mode` existe en la tabla `godata_config` pero no se puede cambiar desde el UI. Actualmente solo se lee de `os.environ["GODATA_PRODUCTION_MODE"]` en el `GoDataClient.__init__`.

### FALT-06: No hay retry automatico para errores transitorios

Si un caso falla por timeout, queda en estado `error` permanentemente. No hay retry automatico. Solo se puede reintentar manualmente aprobando de nuevo.

**Recomendado**: Cron job que re-apruebe errores con < 5 intentos y error transitorio (ConnectionError, Timeout) cada X minutos.

### FALT-07: No hay sincronizacion de contactos

`GoDataClient` tiene `create_contact()` y `create_relationship()` pero ningun endpoint ni UI los usa. Los contactos del caso nunca se sincronizan con GoData.

### FALT-08: No hay actualizacion de casos existentes

Si un caso ya fue sincronizado y luego se modifica localmente, no hay mecanismo para actualizar el caso en GoData. `GoDataClient.update_case()` existe pero no se usa en ningun endpoint.

### FALT-09: No hay descarga de datos desde GoData

No hay funcionalidad para descargar casos de GoData a la BD local. Solo hay upload (push), no pull.

### FALT-10: No hay bulk PDF en el visor GoData

El tab de fichas PDF masivas (lineas 2258+) parece incompleto — se corta al final del fragmento visible. Necesita verificacion de que el flujo masivo completo funciona.

---

## 5. PROBLEMAS DE PERFORMANCE

### PERF-01: Enriquecimiento de cola carga 5000 registros

Ya documentado en WARNING-05. Impacto: latencia de 1-3 segundos extra en cada carga de la cola.

### PERF-02: Batch sync hace N+1 HTTP calls al servidor GoData

Para N registros aprobados, hace:
- N llamadas a `find_case_by_visual_id` (busqueda de duplicado)
- N llamadas a `create_case` (creacion)
- M llamadas a `add_lab_result` (labs, donde M >= N)

Para 100 registros con 3 labs cada uno, son ~400 HTTP calls secuenciales.

**Recomendado**: Usar el bulk import endpoint de GoData si existe, o paralelizar con `concurrent.futures`.

### PERF-03: LibreOffice cold start para PDFs

Cada PDF individual arranca un proceso `libreoffice --headless`. Para bulk, esto significa N procesos secuenciales.

**Recomendado**: Mantener un proceso libreoffice listener o usar `--norestore` flag.

---

## 6. ANALISIS DEL FIELD MAP (godata_field_map.py)

### Variables Correctamente Mapeadas

El mapeo cubre exhaustivamente las secciones del formulario GoData Guatemala:

- Seccion 0: Diagnostico de sospecha
- Seccion 1: Unidad notificadora (con DMS cascadeado por departamento)
- Seccion 2: Informacion del paciente
- Seccion 3: Antecedentes medicos y vacunacion
- Seccion 4: Datos clinicos (sintomas como multi-answer)
- Seccion 5: Factores de riesgo
- Seccion 6: Acciones de respuesta (con codigos "1"/"2")
- Seccion 7: Clasificacion (codigos numericos Guatemala)
- Lab: 4 tests por muestra (sarampion_igm, sarampion_igg, rubeola_igm, rubeola_igg)

### Variables Potencialmente Faltantes

| Variable GoData Guatemala | Estado en field_map |
|---------------------------|-------------------|
| `numero_contactos_` | NO MAPEADA — numero de contactos identificados |
| `fecha_de_defuncion` (QA) | NO MAPEADA — solo se pone en `dateOfOutcome` base, no en QA |
| `causa_de_muerte_certificado_` | NO MAPEADA |
| `observaciones_` | NO MAPEADA — campo de observaciones generales |
| `genotipo_` o `secuenciacion_` | NO MAPEADA — resultado de secuenciacion genomica |

### Inconsistencia DMS: Departamentos faltantes

`_DMS_VARIABLE_MAP` tiene 26 entradas pero Guatemala tiene 29 DAS (Direcciones de Area de Salud):
- Faltan: "IXCAN" y "IXIL" estan como DAS separadas en el mapa, lo cual es correcto para MSPAS
- "PETEN" no esta mapeado directamente (solo PETEN NORTE, PETEN SUR OCCIDENTE, PETEN SUR ORIENTE)

El `_MUNICIPIO_VARIABLE_MAP` SI tiene "PETEN" generico, pero `_DMS_VARIABLE_MAP` no. Si el registro tiene `departamento_residencia = "PETEN"` sin especificar sub-region, el DMS no se mapea.

### Inconsistencia Guatemala DMS Map

`_GUATEMALA_DMS_MAP` solo tiene 9 municipios de los ~17 municipios de Guatemala. Los municipios sin mapeo (SAN JUAN SACATEPEQUEZ, SAN PEDRO SACATEPEQUEZ, SAN RAYMUNDO, PALENCIA, SAN JOSE DEL GOLFO, SAN JOSE PINULA, SAN PEDRO AYAMPUC, SANTA CATARINA PINULA, etc.) caen al default `dms4` que es Guatemala Central, incorrecto para municipios de Guatemala Nor Oriente/Nor Occidente/Sur.

Contraste con `_GUATEMALA_MUNICIPIO_TO_DAS` que tiene ~20 municipios correctamente mapeados. La solucion es sincronizar ambos maps.

### Accent Handling: Correcto

El patron es correcto:
- `_godata_text()` = MAYUSCULAS sin acentos (texto libre: nombres, direcciones)
- `_godata_option()` = MAYUSCULAS con acentos (opciones: SARAMPION, RUBEOLA, BUSQUEDA ACTIVA)

---

## 7. ANALISIS DEL PDF (pdf_ficha_v2.py)

### Fortalezas
- Manejo correcto de MergedCells (skip con warning)
- Parser de fechas robusto (4 formatos)
- Fallback de lab data (JSON -> legacy fields)
- Test CLI con datos completos y vacios

### Debilidades

| Problema | Linea | Impacto |
|----------|-------|---------|
| Row 38 fecha hospitalizacion: dia+mes pero no ano | 426-430 | Ano de hospitalizacion se pierde |
| Row 40 comp_otra_texto: se marca checkbox pero no se escribe texto | 450-452 | "Otra" marcada sin especificar cual |
| Worksheet name hardcoded "Ficha Epidemiologica" | 812 | Si el template cambia el nombre de la hoja, falla |
| No se manejan caracteres especiales en rutas de registro_id | 806 | IDs con caracteres especiales podrian fallar |
| `_write_date` en Row 9 se llama 2 veces identicamente | 199, 206 | Redundante pero inofensivo |

---

## 8. ANALISIS DE LA COLA (godata_queue.py)

### Fortalezas
- Claim atomico con `try_claim_for_sync`
- Recovery de registros stuck con timeout
- Estado dual (godata_queue + registros principal)
- Encriptacion de password con Fernet

### Debilidades
- No hay max_retries enforcement en la cola (el SELECT filtra `intentos < 5` pero nada impide re-aprobar)
- No hay mecanismo de dead letter queue (registros con 5+ intentos quedan en "error" para siempre)
- No hay UNIQUE constraint en `godata_queue(registro_id)` — podria haber duplicados si `enqueue_pending_records` falla a medio camino

---

## 9. RECOMENDACIONES PRIORIZADAS

### Prioridad 1 (Bloquean funcionalidad core)

1. **Fix `/api/godata/test`** para aceptar credenciales del body y devolver el formato esperado por el UI (success, outbreaks, current_user, current_outbreak, message)

2. **Crear endpoints faltantes**: `/api/godata/outbreaks`, `/api/godata/users`, `/api/godata/templates`, `/api/godata/reference-data`

3. **Fix `acciones_de_respuesta = [{}]`** -> `_qa_val("NO")`

### Prioridad 2 (Mejoran robustez y UX)

4. **Agregar production_mode toggle** en el UI de configuracion y en `save_godata_config()`

5. **Usar nombres del JOIN existente** en la cola en vez de cargar 5000 registros

6. **Agregar UNIQUE constraint** a `godata_queue(registro_id)`

7. **Mover imports `json` y `unicodedata`** al nivel global

8. **Fix PDF row 38**: agregar celda para ano de hospitalizacion

9. **Sincronizar `_GUATEMALA_DMS_MAP`** con `_GUATEMALA_MUNICIPIO_TO_DAS`

### Prioridad 3 (Features nuevos)

10. **Retry automatico** para errores transitorios (cron cada 10 min)

11. **Update de casos existentes** via `GoDataClient.update_case()`

12. **Mapear variables faltantes**: numero_contactos, fecha_defuncion QA, causa_muerte, observaciones, genotipo

13. **Paralelizar batch sync** con ThreadPoolExecutor

14. **Agregar dead letter queue** para registros con 5+ intentos fallidos

15. **Sanitizar error messages** antes de enviarlos al frontend

---

## Resumen Ejecutivo

| Categoria | Criticos | Warnings | Info |
|-----------|----------|----------|------|
| Bugs | 3 | 6 | 4 |
| Inconsistencias F/B | 4 | - | - |
| Seguridad | - | 2 | 2 |
| Features faltantes | 10 | - | - |
| Performance | - | 3 | - |

**Estado general**: El modulo GoData tiene una arquitectura solida (field map exhaustivo, cola con estados, dry-run mode, PDF generation) pero el integration layer entre frontend y backend esta **incompleto**. Los 3 bugs criticos hacen que las funciones de configuracion, test de conexion, y exploracion de GoData no funcionen en el UI actual. El field map y la generacion de payload son correctos y completos para casos basicos. Los features faltantes mas importantes son los 4 endpoints sin backend y el fix del test de conexion.
