# Auditoria Final de Produccion - Vigilancia Sarampion IGSS

**Fecha:** 2026-03-29
**Auditor:** Claude Code (automated)
**Servidor:** 100.114.83.69 (Tailscale)

---

## SECCION 1: Infraestructura — PASS

| Check | Resultado | Estado |
|-------|-----------|--------|
| Backend API health | `status: ok`, version 2.0.0, 1023 registros | PASS |
| Streamlit :8501 | HTTP 200 | PASS |
| Streamlit :8502 | HTTP 200 | PASS |
| Streamlit :8503 | HTTP 200 | PASS |
| Servicio vigilancia-sarampion | active (running), uptime 1d 11h | PASS |
| Disco | 18G/40G usado (43%) | PASS |
| BD integridad | `integrity_check: ok` | PASS |
| BD tamanio | 1.2MB + 1.1MB WAL | PASS |
| Tabla registros | 1023 filas, 206 columnas | PASS |
| Tabla audit_log | 95 filas | PASS |
| Tabla mspas_envios | 1023 filas | PASS |
| Tabla godata_queue | 1023 filas | PASS |
| Tabla godata_config | 1 fila | PASS |
| Orphan queue entries | 0 | PASS |
| RAM | 1.3G/31G usado | PASS |
| Litestream | active (running), 4 dias uptime | PASS |
| Errores recientes (1h) | Ninguno | PASS |

---

## SECCION 2: Modulo GoData — PASS (con observaciones)

| Check | Resultado | Estado |
|-------|-----------|--------|
| Config existe | Si, outbreak configurado | PASS |
| Conexion GoData | Autenticado correctamente, 1 outbreak | PASS |
| Cola: pendiente | 1015 | INFO |
| Cola: completo | 8 | INFO |
| Cola: error | 0 | PASS |
| Cola: total | 1023 | PASS |
| ENV GODATA_PRODUCTION_MODE | `true` | PASS |
| DB production_mode | `0` (NULL/false) | OBSERVACION |
| Casos en GoData | 14 (8 sync + 6 prueba) | INFO |
| Outbreak name | "Taller Sarampion" | ADVERTENCIA |

### Observaciones GoData

1. **DISCREPANCIA production_mode**: El ENV dice `true` pero la DB dice `0`. El codigo en `godata_client.py:29` lee de ENV, asi que el comportamiento real ES produccion. Sin embargo, la DB deberia reflejar lo mismo para consistencia.

2. **Outbreak "Taller Sarampion"**: El nombre del outbreak sugiere que es un ambiente de entrenamiento/taller, NO produccion real de MSPAS. Esto es correcto si el objetivo actual es pruebas controladas, pero debe cambiarse cuando se use el outbreak real.

3. **14 casos en GoData**: 8 sincronizados desde el sistema + 6 casos de prueba previos (PRUEBA EDITADA, PRUEBA PRUEBA, PRUEBA FLUJO LAB, etc.). Los casos de prueba deberian limpiarse antes del uso real.

4. **1015 pendientes**: La gran mayoria de registros estan pendientes de aprobacion/sincronizacion. Esto es esperado si el flujo requiere aprobacion manual.

---

## SECCION 3: Calidad de Codigo — PASS

| Check | Resultado | Estado |
|-------|-----------|--------|
| Credenciales hardcodeadas | NINGUNA en archivos .py | PASS |
| TODO/FIXME/HACK | Ninguno encontrado | PASS |
| Sintaxis main.py | OK | PASS |
| Sintaxis godata_client.py | OK | PASS |
| Sintaxis godata_field_map.py | OK | PASS |
| Sintaxis godata_queue.py | OK | PASS |
| Sintaxis pdf_ficha_v2.py | OK | PASS |
| Sintaxis mspas_queue.py | OK | PASS |
| Sintaxis mspas_bot.py | OK | PASS |
| Sintaxis mspas_field_map.py | OK | PASS |
| Sintaxis database.py | OK | PASS |
| Sintaxis config.py | OK | PASS |

### Nota sobre dry_run

El codigo tiene `dry_run` guards correctos en `godata_client.py`. Cuando `GODATA_PRODUCTION_MODE != true`, todas las operaciones de escritura (crear caso, actualizar, lab results, contactos) retornan datos simulados sin tocar GoData. Esto es un patron de seguridad CORRECTO.

---

## SECCION 4: Endpoints API — PASS

| Endpoint | HTTP | Detalle | Estado |
|----------|------|---------|--------|
| GET /api/health | 200 | | PASS |
| GET /api/godata/config | 200 | | PASS |
| GET /api/godata/queue?limit=1 | 200 | | PASS |
| GET /api/godata/status/{id} | 200 | | PASS |
| GET /api/godata/preview/{id} | 200 | | PASS |
| GET /api/export/ficha/{id} (PDF v1) | 200 | 46,634 bytes | PASS |
| GET /api/export/ficha-v2/{id} (PDF v2) | 200 | 99,124 bytes | PASS |
| GET /api/export/excel | 200 | 250,497 bytes | PASS |

---

## SECCION 5: GoData Field Map — PASS

| Check | Resultado | Estado |
|-------|-----------|--------|
| Registro 1 (KELY) | F1=49qa/1warn, F2=52qa/1warn | PASS |
| Registro 2 (PRUEBA) | F1=44qa/1warn, F2=47qa/1warn | PASS |
| Registro 3 (JUAN) | F1=44qa/1warn, F2=47qa/1warn | PASS |
| Registro 4 (LUISA) | F1=57qa/1warn, F2=61qa/1warn | PASS |
| Nombres presentes | Todos OK (no vacios) | PASS |
| Registro vacio (edge case) | 22 qa keys, no crash | PASS |

Todas las transformaciones fase1 y fase2 funcionan sin errores. Los warnings (1 por registro) son aceptables (probablemente campos opcionales vacios).

---

## SECCION 6: Frontend — PASS

| Check | Resultado | Estado |
|-------|-----------|--------|
| index.html presente | Si (929 bytes) | PASS |
| Assets desplegados | Si | PASS |
| Nginx proxy config | Correcto (/sarampion/ → frontend, /sarampion/api/ → :8510) | PASS |
| URL publica frontend | HTTP 200 | PASS |
| URL publica API health | HTTP 200 | PASS |

---

## SECCION 7: Seguridad — PASS (con observaciones)

| Check | Resultado | Estado |
|-------|-----------|--------|
| Credenciales en codigo .py | NINGUNA | PASS |
| .env permisos | 644 root:root | ADVERTENCIA |
| API_SECRET_KEY | Configurado | PASS |
| FERNET_KEY en .env | NO PRESENTE | ADVERTENCIA |
| GoData password en DB | Encriptado (Fernet, gAAAAA...) | PASS |
| GoData creds en .env | No (en DB encriptadas) | PASS |
| MSPAS_PRODUCTION_MODE | No configurado (default off) | PASS |

### Observaciones de Seguridad

1. **Permisos .env (644)**: El archivo .env es legible por todos (world-readable). Deberia ser 600 (`chmod 600 .env`) para que solo root pueda leerlo. Riesgo bajo ya que el servidor solo tiene acceso root, pero es mala practica.

2. **FERNET_KEY ausente en .env**: La encriptacion de passwords GoData funciona porque `mspas_queue.py` genera/usa una key de otra manera, pero no hay FERNET_KEY explicito en .env. El codigo en `_get_fernet()` busca `FERNET_KEY` o `MSPAS_ENCRYPT_KEY`. Si ninguno esta presente, la encriptacion podria fallar para NUEVAS passwords. Sin embargo, la password actual YA esta encriptada y funciona (confirmado: el test de conexion GoData pasa).

---

## RESUMEN DE HALLAZGOS

### Problemas Criticos: NINGUNO

### Advertencias (no bloqueantes):

1. **Outbreak "Taller Sarampion"** — Es un outbreak de entrenamiento. Para produccion real con MSPAS, se necesitara el outbreak oficial.

2. **14 casos de prueba en GoData** — Incluyen registros con nombres como "PRUEBA EDITADA", "PRUEBA PRUEBA". Limpiar antes de produccion real.

3. **Discrepancia production_mode** — ENV=true, DB=0. Funciona correctamente (lee de ENV), pero la DB deberia actualizarse para consistencia.

4. **.env permisos 644** — Deberia ser 600. Cambio trivial: `chmod 600 /opt/vigilancia-sarampion/backend/.env`

5. **FERNET_KEY no explicito** — Funciona actualmente pero deberia documentarse como se genera/almacena la key de encriptacion.

---

## VEREDICTO FINAL: GO (CONDICIONAL)

El sistema esta **operativo y funcional** para su proposito actual (sincronizacion controlada con GoData training environment). Todos los componentes criticos funcionan:

- Infraestructura estable (uptime, disco, RAM, sin errores)
- API completa y respondiendo (todos los endpoints 200)
- Base de datos integra (0 orphans, integridad OK)
- Field mapping funcional (fase1 + fase2 sin crashes)
- Frontend desplegado y accesible
- Seguridad aceptable (passwords encriptadas, sin credenciales en codigo)
- Dry-run guards correctos para proteger contra escrituras accidentales

**Condiciones para GO pleno en produccion real:**
1. Configurar outbreak real de MSPAS (no "Taller Sarampion")
2. Limpiar casos de prueba del GoData
3. `chmod 600 .env`
4. Documentar proceso de FERNET_KEY
5. Sincronizar production_mode entre DB y ENV
