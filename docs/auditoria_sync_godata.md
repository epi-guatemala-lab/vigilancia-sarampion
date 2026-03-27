# Auditoria End-to-End: Workflow de Sincronizacion GoData

**Fecha:** 2026-03-27
**Alcance:** Flujo completo desde formulario React hasta API GoData Guatemala
**Archivos auditados:**
- `backend/main.py` (endpoints sync, lineas 1478-1627)
- `backend/godata_field_map.py` (mapeo payload, 1432 lineas)
- `backend/godata_queue.py` (cola de sincronizacion, 416 lineas)
- `backend/godata_client.py` (cliente REST, 290 lineas)
- `backend/database.py` (esquema BD, 613 lineas)

---

## 1. Traza del Flujo Completo

### Paso 1: Formulario → Base de Datos
- **POST /api/registro** → `insert_registro()` → INSERT en tabla `registros`
- La tabla `registros` tiene 237 columnas (lista `COLUMNS` en database.py)
- Todas las columnas son `TEXT` (no hay tipos numericos ni DATE)
- `_migrate_columns()` agrega automaticamente columnas nuevas (non-destructive)

**Estado: CORRECTO** — todos los campos del formulario se almacenan.

### Paso 2: Encolado
- **POST /api/godata/queue/enqueue-all** → `godata_enqueue_pending()`
- Query: `INSERT INTO godata_queue SELECT registro_id FROM registros WHERE NOT IN godata_queue`
- UNIQUE INDEX en `registro_id` previene duplicados

**Estado: CORRECTO** — idempotente, se puede llamar multiples veces sin duplicar.

### Paso 3: Aprobacion
- **POST /api/godata/queue/approve** → `godata_approve_records(ids)`
- Solo permite transicion: `pendiente` → `aprobado` y `error` → `aprobado`
- Registra `aprobado_por` y `fecha_aprobacion`

**Estado: CORRECTO** — maquina de estados bien definida.

### Paso 4: Sincronizacion (lineas 1478-1602 de main.py)
Flujo en `godata_sync_single()`:
1. `get_registro_by_id()` → lee registro completo
2. `try_claim_for_sync()` → atomicamente cambia `aprobado` → `sincronizando`
3. `get_godata_credentials()` → obtiene URL/user/pass/outbreak_id
4. `get_next_visual_id()` → genera SR-NNNN secuencial
5. `client.find_case_by_visual_id(visual_id)` → busca duplicado por visualId generado
6. `map_record_to_godata(record)` → construye payload
7. `client.create_case(case_payload)` → POST a GoData
8. `save_visual_id(registro_id, visual_id)` → guarda visualId usado
9. `map_lab_samples_to_godata(record)` → construye payloads lab
10. `client.add_lab_result()` → POST resultados lab (en loop)
11. `mark_synced()` → actualiza queue + registros con godata_case_id

---

## 2. GAPS ENCONTRADOS

### GAP-1: CRITICO — `validate_godata_payload()` NUNCA SE LLAMA ANTES DEL SYNC

La funcion `validate_godata_payload()` existe en godata_field_map.py (linea 1368) pero **no se invoca** en ningun endpoint de sincronizacion:

- `godata_sync_single()` (linea 1478): NO llama validate
- `godata_sync_batch()` (linea 1542): NO llama validate
- Solo se importa `map_record_to_godata` y `map_lab_samples_to_godata` en main.py (linea 56)

**Impacto:** Payloads con campos obligatorios vacios (firstName, dateOfReporting, etc.) se envian a GoData sin validacion. GoData acepta cualquier cosa (zero server-side validation segun el comentario en linea 1372), resultando en casos incompletos que no se pueden filtrar.

**Recomendacion:** Agregar validacion antes del `create_case()`:
```python
warnings = validate_godata_payload(case_payload)
critical = [w for w in warnings if 'vacio' in w and any(f in w for f in ['firstName','dateOfReporting','dateOfOnset'])]
if critical:
    godata_mark_error(registro_id, f"Validacion fallida: {'; '.join(critical)}")
    continue
```

### GAP-2: CRITICO — Duplicado chequea visualId GENERADO, no el contenido del caso

Lineas 1504-1508: La verificacion de duplicados busca por `visual_id` que acabamos de generar (SR-NNNN secuencial). Esto NUNCA encontrara un duplicado porque el `visual_id` es nuevo cada vez.

```python
visual_id = get_next_visual_id()  # Siempre nuevo: SR-0100, SR-0101, etc.
existing = client.find_case_by_visual_id(visual_id)  # Siempre None
```

**Impacto:** Si un registro se re-aprueba y re-sincroniza (error → aprobado → sync), se creara un caso DUPLICADO en GoData con diferente visualId. No hay verificacion por nombre/afiliacion/fecha.

**Recomendacion:** Ademas del visualId, verificar si el registro ya tiene un `godata_case_id` guardado, o buscar por afiliacion/nombre en GoData.

### GAP-3: ALTO — Race condition en `get_next_visual_id()` para batch sync

`get_next_visual_id()` (godata_queue.py linea 157) lee el MAX de la BD, pero en `sync-batch` se llama en un loop secuencial sin guardar el visualId en la BD antes de generar el siguiente. Flujo:

```
Iteracion 1: get_next_visual_id() → SR-0100 → create_case → save_visual_id(SR-0100) ✓
Iteracion 2: get_next_visual_id() → SR-0101 ✓ (lee el SR-0100 guardado)
```

En el caso actual (single-threaded uvicorn) esto funciona. Pero si se ejecutan dos batch syncs en paralelo (dos requests simultaneos), ambos leerian el mismo MAX y generarian el mismo visualId.

**Mitigacion actual:** SQLite WAL + timeout=30 + single worker. Riesgo bajo pero real si se migra a multi-worker.

### GAP-4: ALTO — Lab result failure no impide mark_synced

Lineas 1519-1527: Si `create_case` tiene exito pero uno o mas `add_lab_result` fallan, el registro se marca como `sincronizado` de todas formas. No hay forma de saber que falto laboratorio.

```python
for lab in lab_results:
    try:
        client.add_lab_result(godata_case_id, lab)
        lab_count += 1
    except Exception as e:
        logger.warning(f"GoData lab result error for {registro_id}: {e}")
# Continua a mark_synced() sin importar lab_count vs total
```

**Impacto:** Casos en GoData sin resultados de laboratorio, sin indicacion visible de que fallaron.

**Recomendacion:** Si lab_count < len(lab_results), guardar advertencia en `ultimo_error` o crear un estado `parcial`.

### GAP-5: MEDIO — `form_version` NUNCA se setea

De 1023 registros en produccion, 0 tienen `form_version` seteado. La columna existe en `COLUMNS` (linea 233 de database.py) pero el formulario React no la envia.

**Impacto:** No se puede distinguir registros v1 de v2, lo cual afecta el mapeo de campos (v2 tiene `lab_muestras_json`, v1 usa campos flat).

### GAP-6: MEDIO — Token refresh en _handle_http_error no reintenta

Lineas 127-137 de godata_client.py: Cuando recibe 401, limpia el token (`self._token = ""`) y lanza `PermissionError`. Pero NO reintenta la request.

```python
def _handle_http_error(self, e):
    if status == 401:
        self._token = ""  # Limpia token
        raise PermissionError("Token GoData expirado o inválido")  # Falla
```

En `_request_with_retry`, la excepcion `HTTPError` (que incluye 401) se envia a `_handle_http_error` que lanza, sin reintentar. Solo `ConnectionError` y `Timeout` se reintentan.

**Impacto:** Si el token expira durante un batch largo, todos los registros restantes fallan con error en vez de re-autenticar y reintentar.

**Recomendacion:** Detectar 401, limpiar token, y reintentar UNA vez (la siguiente llamada a `_ensure_token()` obtendra token nuevo).

### GAP-7: BAJO — 1 registro huerfano en godata_queue

La cola tiene 1024 entradas pero solo 1023 registros con registro_id. Hay 1 entrada en `godata_queue` que apunta a un `registro_id` que no existe en `registros`.

**Impacto:** Si se intenta sincronizar, `get_registro_by_id` retorna None y se marca como error. No es critico pero indica un registro que fue eliminado despues de encolarse.

### GAP-8: BAJO — `recover_stuck_syncs()` solo se ejecuta al startup

Linea 201 de main.py: `recover_stuck_syncs()` se llama en `@app.on_event("startup")` solamente. Si un registro queda stuck en `sincronizando` (crash mid-sync, timeout, etc.), permanece asi hasta el proximo reinicio del servicio.

**Recomendacion:** Llamar `recover_stuck_syncs()` al inicio de `godata_sync_batch()` tambien, similar a como se hace en MSPAS (linea 1199).

---

## 3. Evaluacion de Manejo de Errores

| Escenario | Manejo | Estado |
|-----------|--------|--------|
| GoData retorna error HTTP | `mark_error()` + raise HTTPException | CORRECTO |
| GoData no configurado | `mark_error()` + raise HTTPException | CORRECTO |
| Conexion cae mid-request | Retry 2x con backoff exponencial | CORRECTO |
| Token expira mid-batch | Error sin re-auth automatica | **GAP-6** |
| Registro no encontrado en BD | `mark_error()` + continue (batch) | CORRECTO |
| Registro ya sincronizando | `try_claim_for_sync()` retorna False | CORRECTO |
| Lab result falla | Warning + continua + marca synced | **GAP-4** |
| Registro stuck en sincronizando | Solo recovery al startup | **GAP-8** |
| Batch: un registro falla | Continua con el resto | CORRECTO |
| DRY RUN mode | `create_case` retorna DRYRUN-id, no llama GoData | CORRECTO |

---

## 4. Escenarios de Recuperacion

| Escenario | Recuperacion |
|-----------|-------------|
| Crash del servidor mid-sync | `recover_stuck_syncs()` al startup (60 min threshold) |
| Error en GoData API | Estado → `error`, reintentable via approve → re-sync |
| Registro duplicado en GoData | Estado → `duplicado`, no reintentable |
| Falla total de red | Retry 2x, luego error permanente |
| BD corrupta | Litestream backup continuo |

---

## 5. Calidad del Payload (Test Real)

Resultado del test con registro `IGSS-SAR-2026-7184231-MZLB`:

| Campo | Valor | Estado |
|-------|-------|--------|
| firstName | LUISA | OK |
| lastName | RAMIREZ CASTILLO DE LOPEZ | OK |
| gender | FEMALE (ref code) | OK |
| classification | CONFIRMED (ref code) | OK |
| outcomeId | RECOVERED (ref code) | OK |
| riskLevel | HIGH (ref code) | OK |
| dateOfReporting | 2026-03-25T00:00:00.000Z | OK |
| dateOfOnset | 2026-03-20T00:00:00.000Z | OK |
| visualId | IGSS-SAR-2026-7184231-MZLB (se sobreescribe con SR-NNNN) | OK |
| addresses | 1 (Guatemala/Quetzaltenango) | OK |
| documents | 1 (IGSS afiliacion) | OK |
| questionnaireAnswers | 48 campos | OK |
| lab_results | 3 resultados | OK |
| **Validation warnings** | **0** | **OK** |

El mapeo de payload es robusto: 48 campos QA, cascaded variables por departamento, codigos numericos Guatemala, sintomas multi-answer, y laboratorio JSON parsed correctamente.

---

## 6. Resumen de Recomendaciones por Prioridad

### CRITICAS (deben arreglarse antes de produccion)

1. **Llamar `validate_godata_payload()` antes de `create_case()`** — actualmente la funcion existe pero nunca se invoca en el flujo de sync.

2. **Arreglar verificacion de duplicados** — buscar por `godata_case_id` existente en el registro antes de crear caso nuevo, no por el visualId recien generado.

### ALTAS

3. **Token refresh automatico en 401** — en `_request_with_retry`, detectar PermissionError, limpiar token, y reintentar una vez.

4. **Registrar fallo parcial de lab results** — si lab_count < total, guardar advertencia en ultimo_error o marcar como `parcial`.

### MEDIAS

5. **Setear `form_version` desde el formulario React** — para distinguir v1/v2 en el mapeo.

6. **Llamar `recover_stuck_syncs()` al inicio de batch** — no solo al startup del servicio.

### BAJAS

7. **Limpiar registro huerfano** — 1 entrada en godata_queue sin registro correspondiente.

8. **Documentar que `get_next_visual_id()` no es thread-safe** — safe en single-worker actual, problema si se escala.
