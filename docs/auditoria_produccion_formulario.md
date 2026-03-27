# Auditoria de Produccion - Formulario Vigilancia Sarampion/Rubeola IGSS

**Fecha:** 2026-03-27
**Auditor:** Simulacion como epidemiologo hospitalario IGSS
**Alcance:** Todos los flujos de usuario, logica condicional, validaciones, y compatibilidad backend
**Archivos auditados:**
- `src/config/formSchema.js` (2133 lineas, 9 tabs, ~130 campos)
- `src/components/FormWizard.jsx` (413 lineas)
- `src/config/conditionalLogic.js` (68 lineas)
- `src/utils/validation.js` (108 lineas)
- `src/utils/formatters.js` (159 lineas)
- `src/components/FormPage.jsx` (160 lineas)
- `src/hooks/useFormState.js` (91 lineas)
- `src/hooks/useConditionalFields.js` (42 lineas)
- `backend/main.py` (~600 lineas)
- `backend/database.py` (COLUMNS list, ~237 columnas)

---

## 1. RESULTADOS POR FLUJO DE USUARIO

### Flow 1: Paciente masculino adulto, sarampion confirmado
| Paso | Resultado | Detalle |
|------|-----------|---------|
| Seleccionar B059, auto-fill CIE-10 | **PASS** | `diagnosticosMap` mapea correctamente, `handleFieldChange` auto-set `codigo_cie10` y agrega 'Sarampion' a `diagnostico_sospecha` |
| Llenar nombres, DPI, masculino, fecha nac | **PASS** | Campos requeridos: `nombres`, `apellidos`, `sexo`, `fecha_nacimiento` |
| Tab 3 (Embarazo) NO debe mostrarse | **PASS** | Todos los campos de Tab 3 tienen `conditional: { dependsOn: 'sexo', showWhen: 'F' }`. `isPageVisible()` oculta la pagina correctamente |
| Tab 4: Vacunado SI, llenar dosis SPR | **PASS** | `dosis_spr` y `fecha_ultima_spr` visibles con `vacunado=SI`, auto-llena campos legacy |
| Tab 5: Signos SI/NO/DESCONOCIDO | **PASS** | 8 signos con 3 opciones cada uno, todos requeridos |
| Tab 5: Hospitalizado SI, campos hospital | **PASS** | `hosp_nombre`, `hosp_fecha`, `no_registro_medico` requeridos y condicionales a `hospitalizado=SI` |
| Tab 6: Viaje SI, campos visibles | **PASS** | `viaje_pais`, `viaje_departamento`, `viaje_municipio` condicionales a `viajo_7_23_previo=SI` |
| Tab 8: Recolecto muestra SI | **PASS** | Muestras individuales (suero/hisopado/orina), antigeno, resultado visibles |
| Tab 9: CONFIRMADO SARAMPION | **PASS** | `criterio_confirmacion` visible, `criterio_descarte` oculto |
| Submit con `cleanHiddenFieldData` | **PASS** | Limpia datos de campos condicionales ocultos antes de envio |

### Flow 2: Paciente femenina embarazada, sospechoso
| Paso | Resultado | Detalle |
|------|-----------|---------|
| Sexo F, Tab 3 visible | **PASS** | Pagina 3 aparece con `esta_embarazada`, `lactando` |
| Embarazada SI, semanas + trimestre | **PASS** | `semanas_embarazo` requerido, trimestre auto-calculado (1-13=1er, 14-26=2do, 27+=3er) |
| SOSPECHOSO, sin criterio confirmacion | **PASS** | `criterio_confirmacion` condicional a CONFIRMADO, no visible con SOSPECHOSO |
| Recolecto=NO | **PASS** | `motivo_no_recoleccion` visible, campos de muestras ocultos |

### Flow 3: Paciente pediatrico (<5 anios)
| Paso | Resultado | Detalle |
|------|-----------|---------|
| Fecha nacimiento reciente, edad auto | **PASS** | Calcula anios/meses/dias correctamente |
| Encargado disponible | **PASS** | `nombre_encargado`, `parentesco_tutor` opcionales |
| Vacunacion verbal/desconocido | **PASS** | `vacunado` tiene opcion 'DESCONOCIDO/VERBAL' |

### Flow 4: Caso descartado
| Paso | Resultado | Detalle |
|------|-----------|---------|
| Clasificacion DESCARTADO | **PASS** | `criterio_descarte` visible con 8 opciones |
| Criterio confirmacion oculto | **PASS** | Solo visible con CONFIRMADO SARAMPION/RUBEOLA |
| Condicion final visible | **PASS** | `condicion_final_paciente` no es condicional, siempre visible |

---

## 2. EDGE CASES

### 2.1 Cambio de sexo F a M despues de llenar embarazo
| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Tab 3 se oculta | **PASS** | `isPageVisible` retorna false, tab desaparece del wizard |
| Datos de embarazo persisten en `formData` | **DEFECTO MENOR** | Los valores de `esta_embarazada`, `semanas_embarazo`, etc. quedan en el state. Sin embargo, `cleanHiddenFieldData` los limpia al enviar. No hay fuga de datos. |
| Navegacion: step count se ajusta | **PASS** | `visiblePages` recalcula, `totalSteps` se actualiza |

### 2.2 Cambio de vacunado SI a NO despues de llenar dosis
| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Campos de dosis se ocultan | **PASS** | Condicionales a `vacunado=SI` |
| Datos de dosis persisten en state | **DEFECTO MENOR** | Misma situacion: quedan en state pero se limpian en submit via `cleanHiddenFieldData` |
| Campos legacy (tipo_vacuna, etc.) | **DEFECTO MENOR** | Los campos legacy hidden se llenan por auto-sync pero NO se limpian al cambiar `vacunado` de SI a NO. Solo `cleanHiddenFieldData` los limpia al submit. |

### 2.3 Cambio de hospitalizado SI a NO
| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Campos hospital se ocultan | **PASS** | Condicional correcto |
| Datos de hospital en state | **DEFECTO MENOR** | Mismo patron: se limpian al submit |

### 2.4 Cambio de diagnostico_registrado despues de auto-set
| Aspecto | Estado | Detalle |
|---------|--------|---------|
| CIE-10 se re-asigna | **PASS** | `handleFieldChange` recalcula `codigo_cie10` |
| diagnostico_sospecha se acumula | **DEFECTO** | Si cambias de B05 a B06, se AGREGA 'Rubeola' al array pero NO se quita 'Sarampion'. El array crece monotonamente. Un epidemiologo que cambia de diagnostico mantendria el sospechoso anterior. |
| **Severidad** | **MEDIA** | Puede causar confusion en reportes posteriores |
| **Recomendacion** | | Al cambiar diagnostico, limpiar el array de diagnostico_sospecha antes de agregar el nuevo valor |

### 2.5 Fecha nacimiento que resulta en >120 anios
| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Calculo de edad | **PASS** | Se calcula correctamente pero NO se valida el resultado |
| Validacion max | **DEFECTO** | `edad_anios` tiene `validation: { min: 0, max: 120 }` pero es `readOnly: true`. La validacion `max: 120` se aplica en `validateField` pero como es readOnly, el usuario no puede corregirlo. Si la fecha de nacimiento produce edad >120, la validacion NO bloquea el avance porque `edad_anios` no es `required`. |
| **Severidad** | **BAJA** | El campo no bloquea pero muestra un valor absurdo |
| **Recomendacion** | | Agregar validacion cruzada en `fecha_nacimiento`: rechazar fechas que produzcan edad >120 |

### 2.6 Fechas futuras
| Aspecto | Estado | Detalle |
|---------|--------|---------|
| fecha_notificacion | **PASS** | `noFuture: true` bloquea fechas futuras |
| fecha_nacimiento | **PASS** | `noFuture: true` |
| fecha_inicio_sintomas | **PASS** | `noFuture: true` |
| fecha_probable_parto | **PASS** (en sentido contrario) | Este campo NO tiene `noFuture` y es correcto: una fecha probable de parto es naturalmente futura |
| fecha_egreso | **PASS** | `noFuture: true` |

### 2.7 Nombres con caracteres especiales
| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Acentos (Maria) | **PASS** | No hay filtro de caracteres en frontend. Backend `sanitize_value` solo remueve control chars (x00-x08, etc.) |
| Apostrofes (O'Brien) | **PASS** | SQLite parametrizado, no hay inyeccion SQL |
| Guiones (Lopez-Garcia) | **PASS** | Sin restriccion |
| maxLength 100 | **PASS** | Suficiente para nombres guatemaltecos |

---

## 3. LOGICA DE CAMPOS Y VALIDACIONES

### 3.1 Campos requeridos por tab

**Tab 1 - Datos Generales:**
| Campo | Requerido | Correcto? | Nota |
|-------|-----------|-----------|------|
| diagnostico_registrado | SI | OK | |
| unidad_medica | SI | OK | |
| fecha_notificacion | SI | OK | |
| semana_epidemiologica | SI | **PROBLEMA** | Es `readOnly` y se auto-calcula. Si el usuario no pone fecha_notificacion primero, queda vacio y bloquea. Pero como fecha_notificacion es requerida y esta antes, esto no deberia pasar en flujo normal. |
| nom_responsable | SI | OK | |
| cargo_responsable | SI | OK | |
| correo_responsable | NO | **MEJORAR** | Tipo `text` en lugar de `email`. No tiene validacion de formato email. Si se quiere validar email, deberia ser `type: 'email'`. |

**Tab 2 - Datos del Paciente:**
| Campo | Requerido | Correcto? | Nota |
|-------|-----------|-----------|------|
| afiliacion | SI | OK | |
| nombres | SI | OK | |
| apellidos | SI | OK | |
| sexo | SI | OK | |
| fecha_nacimiento | SI | OK | |
| pueblo_etnia | SI | OK | |
| ocupacion | SI | OK | |
| escolaridad | SI | OK | |
| departamento_residencia | SI | OK | |
| municipio_residencia | SI | OK | |
| nombre_encargado | NO | **MEJORAR** | Para menores de edad deberia ser requerido. No hay validacion cruzada. |
| telefono_paciente | NO | OK | Telefono es dificil de obtener en algunos contextos |

**Tab 3 - Embarazo:**
| Campo | Requerido | Correcto? | Nota |
|-------|-----------|-----------|------|
| esta_embarazada | SI (si F) | OK | |
| semanas_embarazo | SI (si embarazada=SI) | OK | |
| trimestre_embarazo | NO | OK | Auto-calculado |

**Tab 4 - Vacunacion:**
| Campo | Requerido | Correcto? | Nota |
|-------|-----------|-----------|------|
| vacunado | SI | OK | |
| fuente_info_vacuna | SI (si vacunado=SI) | OK | |
| dosis_spr | NO | **MEJORAR** | Si vacunado=SI, al menos uno de SPR/SR/SPRV deberia tener dosis. No hay validacion cruzada. |

**Tab 5 - Datos Clinicos:**
| Campo | Requerido | Correcto? | Nota |
|-------|-----------|-----------|------|
| fecha_inicio_sintomas | SI | OK | Critico para vigilancia |
| fecha_captacion | SI | OK | |
| fecha_inicio_erupcion | SI | OK | |
| sitio_inicio_erupcion | SI | OK | |
| fecha_inicio_fiebre | SI | **REVISAR** | Es requerido siempre, pero si el paciente NO tiene fiebre (signo_fiebre=NO), no tiene sentido requerir fecha de inicio de fiebre. |
| 8 signos | SI | OK | |
| asintomatico | SI | OK | |
| hospitalizado | SI | OK | |
| hosp_nombre | SI (si hosp) | OK | |
| hosp_fecha | SI (si hosp) | OK | |
| no_registro_medico | SI (si hosp) | **PROBLEMA** | En urgencias/emergencia, el numero de registro a veces no esta disponible inmediatamente. Deberia ser recomendado pero no bloqueante. |

**Tab 6 - Factores de Riesgo:**
| Campo | Requerido | Correcto? | Nota |
|-------|-----------|-----------|------|
| contacto_sospechoso_7_23 | SI | OK | |
| caso_sospechoso_comunidad_3m | SI | OK | |
| viajo_7_23_previo | SI | OK | |

**Tab 7 - Acciones de Respuesta:**
| Campo | Requerido | Correcto? | Nota |
|-------|-----------|-----------|------|
| Ningun campo | - | OK | Todo es opcional, correcto para acciones que pueden no haberse realizado aun |

**Tab 8 - Laboratorio:**
| Campo | Requerido | Correcto? | Nota |
|-------|-----------|-----------|------|
| recolecto_muestra | SI | OK | |
| muestra_suero | SI (si recolecto=SI) | OK | |
| muestra_suero_fecha | SI (si suero=SI) | OK | |
| muestra_hisopado | SI (si recolecto=SI) | OK | |
| muestra_hisopado_fecha | SI (si hisop=SI) | OK | |
| muestra_orina | SI (si recolecto=SI) | OK | |
| muestra_orina_fecha | SI (si orina=SI) | OK | |
| antigeno_prueba | SI (si recolecto=SI) | OK | |
| resultado_prueba | SI (si recolecto=SI) | OK | |

**Tab 9 - Clasificacion y Datos IGSS:**
| Campo | Requerido | Correcto? | Nota |
|-------|-----------|-----------|------|
| clasificacion_caso | SI | OK | |
| es_empleado_igss | SI | OK | |
| criterio_confirmacion | NO | **MEJORAR** | Deberia ser requerido cuando clasificacion es CONFIRMADO. Actualmente es opcional. |
| criterio_descarte | NO | **MEJORAR** | Deberia ser requerido cuando clasificacion es DESCARTADO. Actualmente es opcional. |

### 3.2 Completitud de opciones

| Campo | Opciones | Completo? | Nota |
|-------|----------|-----------|------|
| clasificacion_caso | 6 opciones | **PASS** | SOSPECHOSO, CONFIRMADO SARAMPION, CONFIRMADO RUBEOLA, DESCARTADO, PENDIENTE, NO CUMPLE DEFINICION DE CASO |
| signos (8 campos) | SI/NO/DESCONOCIDO | **PASS** | Correcto para vigilancia epidemiologica |
| complicaciones | 6 tipos + otra | **PASS** | Neumonia, Encefalitis, Diarrea, Trombocitopenia, Otitis, Ceguera + texto libre |
| fuente_posible_contagio | 9 opciones | **PASS** | Hogar, Servicio Salud, Educativa, Publico, Evento, Transporte, Comunidad, Desconocido, Otro |
| condicion_final_paciente | 4 opciones | **PASS** | Recuperado, Con Secuelas, Fallecido, Desconocido |
| criterio_descarte | 8 opciones | **PASS** | Incluye Laboratorial, Reaccion Vacunal, Dengue, Parvovirus, Herpes 6, etc. |
| secuenciacion_resultado | 9 opciones | **PASS** | B3, D4, D8, H1, 1E, 2B, Pendiente, No aplica, Otro |
| viaje_pais | 25 paises | **DEFECTO MENOR** | Falta REPUBLICA DOMINICANA (destino frecuente desde Guatemala). Falta HAITI. |

### 3.3 Auto-calculos

| Calculo | Funciona? | Nota |
|---------|-----------|------|
| edad desde fecha_nacimiento | **PASS** | Calculo correcto con anios/meses/dias |
| trimestre desde semanas_embarazo | **PASS** | 1-13=1, 14-26=2, 27+=3 |
| semana_epidemiologica desde fecha_notificacion | **PASS** | Usa sistema MMWR/CDC (domingo-sabado) |
| diagnostico_sospecha desde diagnostico_registrado | **PASS** con DEFECTO | Acumulativo, no reemplaza (ver 2.4) |
| asintomatico desde signos | **PASS** | Si TODOS los signos=NO, asintomatico=SI. Si alguno=SI, asintomatico=NO |
| complicaciones texto desde checkboxes | **PASS** | Concatena labels con comas |
| condicion_egreso desde condicion_final_paciente | **PASS** | Recuperado/Con Secuelas->MEJORADO, Fallecido->MUERTO |
| nombre_apellido desde nombres+apellidos | **PASS** | Concatena con espacio |
| destino_viaje desde viaje_pais+depto+muni | **PASS** | Formato: "municipio, departamento, pais" |

### 3.4 cleanHiddenFieldData

| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Limpia campos condicionales ocultos | **PASS** | Itera sobre `allFields`, verifica `isFieldVisible`, elimina datos de campos ocultos |
| Campos hidden (UI-only) | **NO AFECTA** | Los campos `hidden: true` nunca se renderizan pero `cleanHiddenFieldData` los procesa por `field.conditional`, no por `field.hidden`. Campos hidden sin conditional no son limpiados (correcto: son campos de sistema). |
| Campos con conditional + hidden | **PASS** | Ejemplo: `busqueda_activa_otra` es hidden+conditional. Se limpia si `busqueda_activa` no es 'Otras'. |

---

## 4. COMPATIBILIDAD BACKEND

### 4.1 VALID_CLASIFICACIONES (backend) vs clasificacion_caso (frontend)

**Frontend ofrece:**
```
SOSPECHOSO, CONFIRMADO SARAMPION, CONFIRMADO RUBEOLA,
DESCARTADO, PENDIENTE, NO CUMPLE DEFINICION DE CASO
```

**Backend acepta:**
```
SOSPECHOSO, CONFIRMADO, CONFIRMADO SARAMPION, CONFIRMADO SARAMPION (sin tilde),
CONFIRMADO RUBEOLA, CONFIRMADO RUBEOLA (sin tilde), DESCARTADO, PENDIENTE,
NO CUMPLE DEFINICION, NO CUMPLE DEFINICION (sin tilde), SUSPENDIDO,
CLINICO, CLINICO (sin tilde), FALSO, ERROR DIAGNOSTICO, ERROR DIAGNOSTICO (sin tilde)
```

| Valor frontend | En backend? | Estado |
|----------------|-------------|--------|
| SOSPECHOSO | SI | **PASS** |
| CONFIRMADO SARAMPION | SI (con y sin tilde) | **PASS** |
| CONFIRMADO RUBEOLA | SI (con y sin tilde) | **PASS** |
| DESCARTADO | SI | **PASS** |
| PENDIENTE | SI | **PASS** |
| NO CUMPLE DEFINICION DE CASO | **NO** | **DEFECTO** |

**DEFECTO CRITICO:** El frontend envia `"NO CUMPLE DEFINICION DE CASO"` pero el backend solo acepta `"NO CUMPLE DEFINICION"` y `"NO CUMPLE DEFINICION"`. La validacion del backend rechazara este valor con error 400.

**Severidad: ALTA** - Un caso clasificado como "NO CUMPLE DEFINICION DE CASO" sera rechazado por el backend.

**Recomendacion:** Alinear - agregar `"NO CUMPLE DEFINICION DE CASO"` y `"NO CUMPLE DEFINICIÓN DE CASO"` a `VALID_CLASIFICACIONES` en `backend/main.py`, o acortar la opcion del frontend.

### 4.2 VALID_SI_NO

**Backend:** `{"SI", "NO", "N/A", "N/S", "DESCONOCIDO", ""}`
**Frontend:** Los campos radio usan `SI`, `NO`, `DESCONOCIDO`, `N/A`, `N/S`
**Estado:** **PASS** - Todos los valores del frontend estan en el set del backend.

**Excepcion:** `vacunado` tiene opcion `'DESCONOCIDO/VERBAL'` que NO es validado por VALID_SI_NO. Pero el backend solo valida campos especificos (clasificacion, sexo, semana, edad), no campos SI/NO generico. **No hay problema actual.**

### 4.3 MAX_FIELD_LENGTH

Backend trunca a 500 caracteres. Frontend tiene:
- `observaciones`: maxLength 1000
- `antecedentes_medicos_detalle`: maxLength 500
- `motivo_no_3_muestras`: maxLength 500
- `motivo_consulta`: maxLength 500

**DEFECTO:** `observaciones` permite 1000 caracteres en frontend pero backend trunca a 500. El usuario podria escribir un texto largo que se trunca silenciosamente.

**Severidad: MEDIA** - Perdida de datos silenciosa en campo de observaciones.

**Recomendacion:** Subir `MAX_FIELD_LENGTH` a 1000 en backend, o bajar maxLength de `observaciones` a 500 en frontend.

### 4.4 Campos en frontend vs COLUMNS en backend

Campos del formulario frontend que NO estan en backend COLUMNS:

| Campo frontend | En COLUMNS? | Impacto |
|----------------|-------------|---------|
| edad_dias | **NO** | Dato se pierde silenciosamente al guardar |

**Detalle:** `edad_dias` se calcula en el frontend pero no existe en la lista `COLUMNS` del backend. El endpoint `POST /api/registro` solo extrae valores de columnas en `COLUMNS`, por lo que `edad_dias` se descarta.

**Severidad: BAJA** - Se puede recalcular desde `fecha_nacimiento`, pero es inconsistente con `edad_anios` y `edad_meses` que SI estan en COLUMNS.

**Recomendacion:** Agregar `"edad_dias"` a COLUMNS en `backend/database.py`.

### 4.5 Campos en backend COLUMNS que NO estan en frontend

| Campo backend | En frontend? | Nota |
|---------------|-------------|------|
| diagnostico_otro | NO | Campo legacy, no necesario |
| centro_externo | NO | Campo legacy |
| complicaciones_otra | NO | Reemplazado por `comp_otra_texto` |
| fecha_laboratorios | NO | Campo legacy |
| tipo_muestra | NO | Campo legacy |
| area_salud_mspas | NO | Campo MSPAS, no aplica a IGSS |
| distrito_salud_mspas | NO | Campo MSPAS |
| servicio_salud_mspas | NO | Campo MSPAS |
| godata_case_id | NO | Generado por backend |
| godata_sync_status | NO | Generado por backend |
| godata_last_sync | NO | Generado por backend |
| godata_outbreak_id | NO | Generado por backend |
| form_version | NO | Generado por backend |
| ip_origen | NO | Generado por backend |
| created_at | NO | Generado por backend |

**Estado: PASS** - Todos los campos extra del backend son legacy o generados por el servidor. No hay campos necesarios faltantes en el frontend (excepto `edad_dias` mencionado arriba).

---

## 5. PROBLEMAS ENCONTRADOS (RESUMEN)

### CRITICOS (bloquean uso en produccion)

| # | Problema | Ubicacion | Fix |
|---|---------|-----------|-----|
| C1 | `"NO CUMPLE DEFINICION DE CASO"` rechazado por backend | `backend/main.py` L98 | Agregar variante completa a `VALID_CLASIFICACIONES` |

### ALTOS (afectan datos, requieren fix antes de lanzamiento)

| # | Problema | Ubicacion | Fix |
|---|---------|-----------|-----|
| A1 | `observaciones` permite 1000 chars, backend trunca a 500 | `formSchema.js` / `main.py` | Alinear limites |
| A2 | `edad_dias` no se guarda en backend | `database.py` COLUMNS | Agregar `"edad_dias"` a COLUMNS |
| A3 | `fecha_inicio_fiebre` requerido incluso si `signo_fiebre=NO` | `formSchema.js` L958 | Hacer condicional o no requerido |

### MEDIOS (mejoras de logica)

| # | Problema | Ubicacion | Fix |
|---|---------|-----------|-----|
| M1 | `diagnostico_sospecha` acumula valores al cambiar diagnostico | `FormWizard.jsx` L62-72 | Limpiar array antes de agregar nuevo |
| M2 | `criterio_confirmacion` deberia ser requerido para CONFIRMADOS | `formSchema.js` L1852 | Agregar `required: true` (o validacion cruzada) |
| M3 | `criterio_descarte` deberia ser requerido para DESCARTADOS | `formSchema.js` L1862 | Agregar `required: true` (o validacion cruzada) |
| M4 | `correo_responsable` tipo `text` sin validacion email | `formSchema.js` L237 | Cambiar a `type: 'email'` |
| M5 | `no_registro_medico` requerido puede bloquear en emergencia | `formSchema.js` L1098 | Considerar hacer opcional |

### BAJOS (mejoras deseables, no bloquean)

| # | Problema | Ubicacion | Fix |
|---|---------|-----------|-----|
| B1 | No hay validacion de edad maxima en `fecha_nacimiento` | `formSchema.js` L378 | Agregar validacion custom |
| B2 | `viaje_pais` falta Republica Dominicana, Haiti | `formSchema.js` L1298 | Agregar paises |
| B3 | `nombre_encargado` no requerido para menores | `formSchema.js` L549 | Requiere validacion cruzada con edad |
| B4 | Si `vacunado=SI`, ninguna dosis de SPR/SR/SPRV es requerida | `formSchema.js` L722-786 | Validacion cruzada: al menos uno debe tener valor |
| B5 | Datos de campos condicionales persisten en state al ocultar | `useFormState.js` | Solo se limpian al submit, no al ocultar. Funcional pero no ideal. |
| B6 | Semana epidemiologica MMWR/CDC vs MSPAS | `formatters.js` L11 | Verificar que el calculo coincida exactamente con calendario oficial MSPAS (domingo-sabado). El algoritmo usa Jan 4 como referencia, que es correcto para MMWR. |

---

## 6. VALIDACIONES FALTANTES

| Validacion | Tipo | Descripcion |
|------------|------|-------------|
| Fecha cruzada: sintomas antes de notificacion | Cross-field | `fecha_inicio_sintomas` debe ser <= `fecha_notificacion` |
| Fecha cruzada: erupcion despues de sintomas | Cross-field | `fecha_inicio_erupcion` >= `fecha_inicio_sintomas` (usualmente) |
| Fecha cruzada: hospitalizacion despues de sintomas | Cross-field | `hosp_fecha` >= `fecha_inicio_sintomas` |
| Fecha cruzada: egreso despues de hospitalizacion | Cross-field | `fecha_egreso` >= `hosp_fecha` |
| Fecha cruzada: defuncion despues de hospitalizacion | Cross-field | `fecha_defuncion` >= `hosp_fecha` |
| Edad vs embarazo | Cross-field | Si edad < 10 anios, embarazada no deberia ser SI |
| Recoleccion muestra vs resultado | Cross-field | Si `resultado_prueba` es 'Positivo', clasificacion NO deberia ser DESCARTADO (warning) |
| Asintomatico vs fiebre | Cross-field | Si `signo_fiebre=SI`, `asintomatico` NO puede ser SI (el auto-calculo maneja esto, pero manual override es posible) |
| DPI formato | Format | Si `tipo_identificacion=DPI`, el `numero_identificacion` debe tener 13 digitos |

Nota: Ninguna de estas es estrictamente necesaria para produccion, pero mejorarian la calidad de datos significativamente. El formulario MSPAS original no tiene la mayoria de estas validaciones cruzadas.

---

## 7. EVALUACION DE PRODUCCION

### GO / NO-GO

## VEREDICTO: **GO CONDICIONAL**

El formulario esta listo para produccion **despues de corregir el defecto critico C1** (alineacion de clasificacion con backend). Los demas defectos son mejoras que pueden implementarse en iteraciones posteriores sin bloquear el uso.

### Condiciones para GO:

1. **OBLIGATORIO antes de produccion:**
   - [ ] Fix C1: Agregar `"NO CUMPLE DEFINICION DE CASO"` y `"NO CUMPLE DEFINICIÓN DE CASO"` a `VALID_CLASIFICACIONES` en `backend/main.py`

2. **Recomendado antes de produccion (alta prioridad):**
   - [ ] Fix A1: Alinear maxLength de `observaciones` (frontend 1000 vs backend 500)
   - [ ] Fix A2: Agregar `edad_dias` a COLUMNS en backend
   - [ ] Fix A3: Hacer `fecha_inicio_fiebre` no requerido o condicional a `signo_fiebre=SI`

3. **Recomendado para siguiente iteracion:**
   - [ ] Fix M1-M5: Mejoras de logica condicional y validacion
   - [ ] Validaciones cruzadas de fechas
   - [ ] Validacion DPI 13 digitos

### Fortalezas del formulario:
- Arquitectura solida con separacion de concerns (schema, logica condicional, validacion, state)
- `cleanHiddenFieldData` previene envio de datos stale de campos ocultos
- Offline support con localStorage y cola de envio
- Duplicado check por afiliacion + fecha (frontend + backend)
- Sanitizacion de datos en backend (control chars, length)
- Rate limiting por IP
- Campos legacy hidden para compatibilidad retroactiva
- Auto-calculos correctos (edad, trimestre, semana epi, complicaciones)
- Tab 3 se oculta correctamente para pacientes masculinos
- Cascading selects para departamento/municipio/poblado y organigrama IGSS

### Debilidades arquitectonicas:
- Sin validaciones cruzadas entre campos (cross-field validation)
- Sin validacion de coherencia temporal entre fechas
- El frontend confia en que el backend aceptara los valores que el frontend permite (ver C1)
- No hay mecanismo de "guardar borrador" parcial (solo submit completo o localStorage)
