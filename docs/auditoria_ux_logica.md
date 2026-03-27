# Auditoria UX y Logica — Formulario Vigilancia Sarampion/Rubeola IGSS

**Fecha:** 2026-03-26
**Alcance:** Revision completa de `src/config/formSchema.js` (2128 lineas, 9 tabs, ~120 campos)
**Contexto:** Formulario llenado por medicos/enfermeras/epidemiologos en hospitales IGSS para notificar casos sospechosos de sarampion/rubeola.

---

## 1. CAMPOS REDUNDANTES

### 1.1 `diagnostico_sospecha` vs `diagnostico_registrado` (ALTA PRIORIDAD)

**Problema:** El usuario selecciona `diagnostico_registrado` = "B05 - Sarampion" y luego debe marcar manualmente `diagnostico_sospecha` = "Sarampion". Esto es redundante: si el CIE-10 es B05x, la sospecha de sarampion es obvia. Si es B06x, la sospecha de rubeola es obvia.

**Recomendacion:**
- Auto-marcar `diagnostico_sospecha` segun `diagnostico_registrado`:
  - B05x -> pre-check "Sarampion"
  - B06x -> pre-check "Rubeola"
- Permitir que el usuario ANADA sospechas adicionales (ej: B05 + sospecha de Dengue como diferencial)
- Cambiar el label a "Sospechas adicionales (opcional)" y quitar `required: true`

**Impacto:** Elimina 1 click obligatorio redundante en el 100% de los casos.

### 1.2 `codigo_cie10` (BAJA PRIORIDAD)

**Problema:** Campo readOnly que se auto-llena desde `diagnostico_registrado`. El usuario ve "B05" al lado de "B05 - Sarampion complicado por encefalitis". Es informacion visual duplicada.

**Recomendacion:** Mantener como esta (campo oculto para backend), pero considerar si realmente necesita espacio visual. Podria ser `hidden: true` y solo guardarse internamente.

### 1.3 `condicion_egreso` (Tab 5) vs `condicion_final_paciente` (Tab 9)

**Problema:** Dos campos preguntan esencialmente lo mismo en momentos diferentes:
- Tab 5: `condicion_egreso` con opciones MEJORADO/GRAVE/MUERTO (al egreso hospitalario)
- Tab 9: `condicion_final_paciente` con opciones Recuperado/Con Secuelas/Fallecido/Desconocido

Si `condicion_egreso` = MUERTO, `condicion_final_paciente` deberia auto-llenarse como "Fallecido".

**Recomendacion:**
- Auto-derivar `condicion_final_paciente` = "Fallecido" si `condicion_egreso` = "MUERTO"
- Pre-llenar "Recuperado" si `condicion_egreso` = "MEJORADO"
- Permitir override manual en Tab 9

### 1.4 `fecha_defuncion` (Tab 5) vs `causa_muerte_certificado` (Tab 9)

**Problema:** Datos de defuncion repartidos en 2 tabs diferentes. El usuario llena fecha y medico en Tab 5, luego causa en Tab 9. Deberian estar juntos.

**Recomendacion:** Mover `causa_muerte_certificado` a Tab 5, dentro del bloque condicional `condicion_egreso = MUERTO`, junto a `fecha_defuncion` y `medico_certifica_defuncion`.

### 1.5 `contacto_sospechoso_7_23` (Tab 6) vs `contacto_otro_caso` (Tab 9)

**Problema:** Preguntas similares sobre contacto:
- Tab 6: "Tuvo contacto con otro sospechoso de 7-23 dias antes del inicio de la erupcion" (SI/NO/DESCONOCIDO)
- Tab 9: "Tuvo contacto con otro caso confirmado?" (SI/NO)

Son conceptualmente distintas (sospechoso vs confirmado, ventana temporal), pero el usuario percibe redundancia.

**Recomendacion:** Mantener ambas pero agregar helpText a cada una para aclarar la diferencia:
- Tab 6: "Contacto con caso SOSPECHOSO durante el periodo de incubacion (7-23 dias antes de erupcion)"
- Tab 9: "Contacto con caso CONFIRMADO por laboratorio o nexo epidemiologico"

---

## 2. CAMPOS QUE PODRIAN SER AUTO-DERIVADOS

### 2.1 `semana_epidemiologica` -- YA IMPLEMENTADO (OK)
Auto-calculada desde `fecha_notificacion`. Correcto.

### 2.2 `edad_anios`, `edad_meses`, `edad_dias` -- YA IMPLEMENTADO (OK)
Auto-calculados desde `fecha_nacimiento`. Correcto.

### 2.3 `trimestre_embarazo` -- YA IMPLEMENTADO (OK)
Auto-calculado desde `semanas_embarazo`. Correcto.

### 2.4 `clasificacion_caso` -- PODRIA SER SEMI-AUTO (MEDIA PRIORIDAD)

**Oportunidad:** Si `resultado_igm_cualitativo` = "REACTIVO" o `resultado_pcr_hisopado` = "POSITIVO", sugerir automaticamente "CONFIRMADO SARAMPION" (si CIE=B05x) o "CONFIRMADO RUBEOLA" (si CIE=B06x). Si todos los resultados son negativos, sugerir "DESCARTADO".

**Recomendacion:** No auto-llenar (la clasificacion es decision clinica), pero mostrar una sugerencia visual: "Basado en resultados de laboratorio, este caso podria clasificarse como: CONFIRMADO SARAMPION".

### 2.5 `fuente_notificacion` -- PODRIA TENER DEFAULT IGSS (BAJA PRIORIDAD)

**Oportunidad:** En el 95%+ de los casos IGSS, la fuente es "Servicio de Salud". Podria pre-seleccionarse.

**Recomendacion:** `defaultValue: 'Servicio de Salud'` para ahorrar 1 click.

### 2.6 `es_seguro_social` y `establecimiento_privado` -- YA IMPLEMENTADO (OK)
Campos hidden, hardcodeados como SI y NO respectivamente. Correcto.

### 2.7 `pais_residencia` -- PARCIALMENTE IMPLEMENTADO
Tiene `defaultValue: 'GUATEMALA'` pero es texto libre. El 99% de pacientes IGSS son guatemaltecos.

**Recomendacion:** Mantener el default. Considerar cambiarlo a select con "GUATEMALA" + texto libre para "Otro".

### 2.8 `dias_entre_erupcion_y_muestra` -- NO EXISTE, DEBERIA

**Oportunidad:** Un indicador critico en vigilancia de sarampion es cuantos dias pasaron entre el inicio de la erupcion y la toma de muestra. Se puede calcular desde `fecha_inicio_erupcion` y `muestra_suero_fecha`.

**Recomendacion:** Agregar campo readOnly auto-calculado que muestre este indicador. OPS/MSPAS lo usan para evaluar oportunidad de la muestra (ideal: 0-3 dias).

### 2.9 `dias_entre_notificacion_y_investigacion` -- NO EXISTE, DEBERIA

**Oportunidad:** Otro indicador clave: dias entre `fecha_notificacion` y `fecha_captacion`. Mide la oportunidad de la investigacion.

---

## 3. CAMPOS TEXTO QUE DEBERIAN SER SELECT/DROPDOWN

### 3.1 `comunidad_linguistica` (ALTA PRIORIDAD)

**Problema actual:** Campo `type: 'text'` libre.

**Valores conocidos (GoData Guatemala 2026):**
Achi', Akateka, Awakateka, Ch'orti', Chalchiteka, Chuj, Garifuna, Itza, Ixil, Jakalteka, Kaqchikel, K'iche', Mam, Mopan, Poqomam, Poqomchi, Q'anjob'al, Q'eqchi', Sakapulteka, Sipakapense, Tektiteka, Tz'utujil, Uspanteka, Espanol, Otro

**Recomendacion:** Cambiar a `type: 'select', searchable: true` con estas 25 opciones. Agregar condicional: solo mostrar si `pueblo_etnia` = "Maya" o "Garifuna" o "Xinca".

### 3.2 `cargo_responsable` (MEDIA PRIORIDAD)

**Problema actual:** Campo texto libre para el cargo del notificador.

**Valores frecuentes en IGSS:**
Medico Epidemiologo, Medico Residente, Medico de Consulta, Enfermera Profesional, Enfermera Auxiliar, Jefe de Epidemiologia, Coordinador de Vigilancia, Otro

**Recomendacion:** Cambiar a `type: 'select'` con opcion "Otro" + campo condicional texto.

### 3.3 `hosp_nombre` (MEDIA PRIORIDAD)

**Problema actual:** Campo texto libre para nombre del hospital de hospitalizacion.

**Recomendacion:** Reutilizar el select de `unidadesMedicasNombres` (ya importado) + agregar hospitales MSPAS frecuentes + opcion "Otro". Esto da consistencia en los datos y evita variantes ("Hosp. Roosevelt" vs "HOSPITAL ROOSEVELT" vs "Roosevelt").

### 3.4 `viaje_pais` (BAJA PRIORIDAD)

**Problema actual:** Texto libre.

**Recomendacion:** Select con lista de paises de Centroamerica y paises con circulacion activa de sarampion (USA, Brasil, India, Nigeria, etc.) + "Otro" con texto libre. O al menos un searchable select con ISO country list.

### 3.5 `viaje_departamento` (MEDIA PRIORIDAD)

**Problema actual:** Texto libre, pero el formulario YA tiene `departamentosGuatemala` importado.

**Recomendacion:** Reutilizar el select de departamentos existente. Agregar condicional: solo mostrar como select si `viaje_pais` = "GUATEMALA"; si es otro pais, mostrar como texto libre.

### 3.6 `motivo_no_recoleccion` (BAJA PRIORIDAD)

**Problema actual:** Texto libre.

**Valores comunes:** Paciente se nego, Muestra hemolizada, No habia insumos, Paciente se retiro antes, Alta antes de toma, Otro

**Recomendacion:** Cambiar a select + "Otro" con texto.

### 3.7 `puesto_desempena` (Tab 9, Datos IGSS) (BAJA PRIORIDAD)

**Problema actual:** Texto libre para puesto del empleado IGSS.

**Recomendacion:** Podria ser select con puestos frecuentes en IGSS (Medico, Enfermera, Administrativo, Tecnico, Camillero, Limpieza, etc.) + "Otro".

### 3.8 `secuenciacion_resultado` (BAJA PRIORIDAD)

**Problema actual:** Texto libre para genotipo.

**Valores conocidos de sarampion:** A, B1, B2, B3, C1, C2, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, G1, G2, G3, H1, H2 (genotipos OMS). Para rubeola: 1a, 1B, 1C, 1D, 1E, 1F, 1G, 1H, 1I, 1J, 2A, 2B, 2C.

**Recomendacion:** Select con genotipos conocidos + "Pendiente" + "Otro". Facilitaria analisis posterior.

---

## 4. NOMBRES — SPLIT O NO SPLIT

### Estado actual
- `nombres` (campo unico) y `apellidos` (campo unico)

### Analisis

| Criterio | 2 campos (actual) | 4 campos (split) |
|----------|-------------------|-------------------|
| Velocidad de llenado | Mas rapido | Mas lento (4 tabs/clicks) |
| Compatibilidad EPIWEB | Directo (2 campos) | Requiere concatenacion |
| Compatibilidad GoData | Requiere split | Directo (firstName, middleName, lastName) |
| Datos existentes | 414 registros con formato combinado | Requeriria migracion |
| Nombres guatemaltecos | "Maria Jose" + "Lopez Garcia" es comun | Ambiguedad: "Jose" es segundo nombre o? |
| DPI | El DPI tiene primer nombre + segundo nombre + apellido + apellido | Matchea bien con 4 campos |

### Recomendacion: MANTENER 2 CAMPOS

Razones:
1. EPIWEB usa 2 campos (la compatibilidad con MSPAS es prioritaria)
2. 414 registros existentes necesitarian migracion
3. El split automatico de nombres guatemaltecos es fragil ("Maria de los Angeles" seria primer_nombre o primer+segundo?)
4. El beneficio para GoData es menor (se puede hacer split automatico en el backend al exportar)

**Si se quisiera mejorar:** Agregar hints en el placeholder: `placeholder: 'Primer y segundo nombre'` y `placeholder: 'Primer y segundo apellido'`.

---

## 5. REQUIRED vs OPTIONAL — ANALISIS POR PERSPECTIVA HOSPITALARIA

### Campos que deberian ser REQUIRED pero NO lo son

| Campo | Estado actual | Justificacion para requerir |
|-------|-------------|---------------------------|
| `tipo_identificacion` | optional | Si tiene `numero_identificacion`, deberia saber el tipo |
| `telefono_paciente` | optional | **Mantener optional** — algunos pacientes no tienen |

### Campos que son REQUIRED pero NO deberian serlo

| Campo | Estado actual | Justificacion para hacer optional |
|-------|-------------|----------------------------------|
| `afiliacion` | required | No todos los pacientes tienen numero de afiliacion (menores, beneficiarios sin carnet, emergencias) |
| `ocupacion` | required | En emergencias no siempre se obtiene. Podria tener "No disponible" como opcion |
| `escolaridad` | required | Dato secundario, no siempre disponible en emergencia |
| `pueblo_etnia` | required | Dato sensible, paciente puede negarse a responder. Agregar "Prefiere no responder" |
| `diagnostico_sospecha` | required | Redundante con `diagnostico_registrado` (ver seccion 1.1) |
| `signo_manchas_koplik` | required | Las manchas de Koplik son dificiles de identificar y transitorias. Muchos medicos no las buscan. Deberia ser optional |
| `signo_artralgia` | required | Mas relevante para rubeola. Si el CIE es B05x, no siempre se evalua |
| `asintomatico` | required | Si ya se marcaron sintomas, este campo es derivable (todos NO -> asintomatico=SI) |
| `fecha_captacion` | required | A veces es igual a `fecha_notificacion` y es un campo extra innecesario |
| `es_empleado_igss` | required | Correcto que sea required en contexto IGSS |

### Campos que son optional y DEBERIAN serlo (correcto)

- `numero_identificacion` -- No todos cargan DPI
- `nombre_encargado` -- Solo relevante para menores
- Todo el Tab 3 (Embarazo) -- Condicional a sexo=F
- Todo el Tab 8 (Laboratorio resultados) -- Pueden llegar despues
- `observaciones` -- Siempre optional

### Recomendacion especifica: `afiliacion`

En IGSS, el numero de afiliacion es el identificador principal. PERO en emergencias, pacientes pueden llegar sin carnet. Opciones:
1. Mantener required pero agregar opcion "PENDIENTE" o "SIN AFILIACION"
2. Cambiar a optional con validacion warning (no error)

---

## 6. LOGICA CONDICIONAL — ANALISIS

### 6.1 Condicionales correctos (OK)

- Tab 3 completo: `sexo = F` -- Correcto
- `semanas_embarazo`: `esta_embarazada = SI` -- Correcto
- `fecha_defuncion`: `condicion_egreso = MUERTO` -- Correcto
- Campos vacunacion: `vacunado = SI` -- Correcto
- Campos viaje: `viajo_7_23_previo = SI` -- Correcto
- Campos BAI: `bai_realizada = SI` -- Correcto
- Muestras lab: `recolecto_muestra = SI` -- Correcto

### 6.2 Condicionales faltantes (PROBLEMAS)

#### a) `nombre_encargado` deberia ser condicional a edad < 18

**Problema:** El campo de encargado aparece siempre, pero solo es relevante para menores de edad. Para adultos, es ruido visual.

**Recomendacion:** Hacer toda la seccion "Encargado" (`nombre_encargado`, `parentesco_tutor`, `tipo_id_tutor`, `numero_id_tutor`, `telefono_encargado`) condicional:
- Mostrar siempre si `edad_anios` < 18
- Mostrar como seccion colapsada/opcional si `edad_anios` >= 18
- Alternativamente: agregar radio "Paciente es menor de edad o con discapacidad?" que controle la visibilidad

#### b) `comunidad_linguistica` deberia ser condicional a `pueblo_etnia`

**Problema:** Aparece siempre, pero solo es relevante si `pueblo_etnia` = "Maya" o "Garifuna" o "Xinca".

**Recomendacion:** `conditional: { dependsOn: 'pueblo_etnia', showWhen: ['Maya', 'Garifuna', 'Xinca'] }`

#### c) `lactando` deberia considerar edad del paciente

**Problema:** Aparece para toda mujer (sexo=F), pero una nina de 5 anos no puede estar lactando.

**Recomendacion:** Agregar logica adicional: mostrar solo si `sexo = F` AND `edad_anios >= 12` (o edad reproductiva). Similar para `esta_embarazada`.

#### d) `familiar_viajo_exterior` tiene condicional incorrecto

**Problema actual:** Condicional a `viajo_7_23_previo = SI`. Esto es logicamente incorrecto. La pregunta sobre si un FAMILIAR viajo es relevante SIEMPRE, no solo cuando el PACIENTE viajo. De hecho, es MAS relevante cuando el paciente NO viajo (porque el familiar podria ser la fuente de contagio).

**Recomendacion:** Quitar el condicional de `viajo_7_23_previo` y mostrar siempre en Tab 6. O mejor: hacer condicional inverso (mostrar cuando `viajo_7_23_previo = NO`).

#### e) `muestra_suero`, `muestra_hisopado`, `muestra_orina` son required dentro del condicional

**Problema:** Si `recolecto_muestra = SI`, los tres tipos de muestra son `required: true`. Pero es perfectamente valido tomar solo suero sin hisopado. El campo `motivo_no_3_muestras` existe precisamente para esto.

**Recomendacion:** Cambiar `muestra_hisopado` y `muestra_orina` a `required: false`. Solo `muestra_suero` deberia ser required (es la muestra minima obligatoria segun protocolo OPS).

#### f) `antigeno_prueba` y `resultado_prueba` son required si `recolecto_muestra = SI`

**Problema:** Al momento de llenar el formulario, la muestra puede haberse tomado pero los resultados aun no estan disponibles. Forzar resultado es incorrecto.

**Recomendacion:** Cambiar ambos a `required: false`. Agregar opcion "PENDIENTE" a `resultado_prueba`.

### 6.3 Condicionales con bugs potenciales

#### g) `contacto_enfermo_catarro` es `hidden: true` PERO no tiene conditional guard

**Problema:** Campo oculto sin condicional. Si algun mecanismo lo des-oculta, aparece sin contexto.

**Status:** Bajo riesgo (hidden funciona). Pero deberia limpiarse: o eliminarlo o documentar por que esta oculto.

---

## 7. TAB FLOW — ORDEN OPTIMO PARA WORKFLOW HOSPITALARIO

### Orden actual

| Tab | Contenido | Campos visibles |
|-----|-----------|-----------------|
| 1 | Datos Generales (unidad, diagnostico, responsable, investigacion) | ~14 |
| 2 | Datos del Paciente (ID, nombre, edad, residencia, encargado) | ~20 |
| 3 | Embarazo (condicional F) | ~6 |
| 4 | Antecedentes y Vacunacion | ~15 |
| 5 | Datos Clinicos (sintomas, hospitalizacion, complicaciones) | ~25 |
| 6 | Factores de Riesgo (contactos, viaje) | ~12 |
| 7 | Acciones de Respuesta (BAI, vitamina A) | ~4 visibles |
| 8 | Laboratorio | ~25 |
| 9 | Clasificacion y Datos IGSS | ~20 |

### Flujo real del medico en hospital

1. **Paciente llega** -> El medico ve al paciente y obtiene: nombre, edad, motivo de consulta
2. **Examen clinico** -> Sintomas, signos vitales, erupcion
3. **Diagnostico** -> CIE-10, sospecha
4. **Ordenes** -> Toma de muestras, hospitalizacion
5. **Notificacion** -> Llena formulario epidemiologico (este formulario)
6. **Seguimiento** -> Resultados de lab, clasificacion final

### Orden recomendado

| Tab | Contenido recomendado | Justificacion |
|-----|-----------------------|---------------|
| 1 | **Datos del Paciente** (ID, nombre, edad, residencia) | Lo primero que el medico tiene a mano: carnet del paciente |
| 2 | **Datos Clinicos** (sintomas, erupcion, fiebre) | Lo segundo: lo que acaba de examinar |
| 3 | **Diagnostico y Notificacion** (CIE-10, sospecha, unidad, responsable, fecha) | Tercero: formaliza la notificacion |
| 4 | **Embarazo** (condicional) | Si aplica, ya tiene los datos clinicos |
| 5 | **Antecedentes y Vacunacion** | Requiere preguntar al paciente/familia o buscar carne |
| 6 | **Factores de Riesgo** (contactos, viaje) | Requiere investigacion/entrevista |
| 7 | **Laboratorio** | Se llena parcialmente ahora, se completa cuando llegan resultados |
| 8 | **Clasificacion Final** (incluye Acciones de Respuesta) | Se llena al final, cuando hay datos completos |

### Beneficio
El usuario puede llenar los primeros 3-4 tabs inmediatamente con informacion que tiene a la mano, y dejar los ultimos tabs para completar despues. Esto es mas natural que el flujo actual donde Tab 1 mezcla datos administrativos con diagnostico.

---

## 8. ISSUES ESPECIFICOS

### 8.a `diagnostico_sospecha` auto-poblado (REITERADO, ALTA PRIORIDAD)

Ver seccion 1.1. Implementacion sugerida:

```javascript
// En el componente del formulario, cuando cambia diagnostico_registrado:
const cieCode = diagnosticosMap[selectedDiag]
if (cieCode?.startsWith('B05')) {
  // Pre-check "Sarampion" en diagnostico_sospecha
  setFieldValue('diagnostico_sospecha', ['Sarampion', ...currentSospecha])
}
if (cieCode?.startsWith('B06')) {
  setFieldValue('diagnostico_sospecha', ['Rubeola', ...currentSospecha])
}
```

### 8.b Campos de investigacion ocultos -- CORRECTO

`fecha_visita_domiciliaria`, `busqueda_activa`, `fecha_inicio_investigacion` estan `hidden: true`. Correcto, son campos MSPAS que IGSS no usa directamente.

### 8.c `comunidad_linguistica` como select -- DETALLE DE IMPLEMENTACION

```javascript
{
  id: 'comunidad_linguistica',
  label: 'Comunidad Linguistica',
  type: 'select',
  page: 2,
  required: false,
  searchable: true,
  options: [
    "Achi'", "Akateka", "Awakateka", "Ch'orti'", "Chalchiteka",
    "Chuj", "Garifuna", "Itza'", "Ixil", "Jakalteka", "Kaqchikel",
    "K'iche'", "Mam", "Mopan", "Poqomam", "Poqomchi'", "Q'anjob'al",
    "Q'eqchi'", "Sakapulteka", "Sipakapense", "Tektiteka", "Tz'utujil",
    "Uspanteka", "Xinka", "Espanol", "Otro"
  ],
  conditional: { dependsOn: 'pueblo_etnia', showWhen: ['Maya', 'Garifuna', 'Xinca'] },
  colSpan: 'half',
}
```

### 8.d `parentesco_tutor` -- YA IMPLEMENTADO COMO SELECT (OK)

El campo ya tiene `options: ['Madre', 'Padre', 'Abuelo/a', 'Tio/a', 'Hermano/a', 'Otro']`. Correcto. Pero falta campo condicional "Especifique" para opcion "Otro".

### 8.e `hosp_nombre` como select

```javascript
{
  id: 'hosp_nombre',
  label: 'Nombre del Hospital',
  type: 'select',
  searchable: true,
  options: [...unidadesMedicasNombres, 'HOSPITAL GENERAL SAN JUAN DE DIOS', 'HOSPITAL ROOSEVELT', 'HOSPITAL NACIONAL DE ANTIGUA', 'OTRO'],
  // + campo condicional hosp_nombre_otro para "OTRO"
}
```

### 8.f Tab 7 (Acciones de Respuesta) -- FUSIONAR (ALTA PRIORIDAD)

**Estado actual:** Despues de ocultar campos MSPAS, Tab 7 solo tiene 4 campos visibles:
1. `bai_realizada` (SI/NO)
2. `bai_casos_sospechosos` (condicional)
3. `vitamina_a_administrada` (SI/NO/DESCONOCIDO)
4. `vitamina_a_dosis` (condicional)

**Problema:** Un tab entero para 2-4 campos es desperdicio de navegacion. El usuario debe hacer click en "Siguiente" para pasar por un tab casi vacio.

**Recomendacion:** Fusionar Tab 7 con Tab 5 (Datos Clinicos) como seccion al final, despues de "Aislamiento". La BAI y la Vitamina A son acciones clinicas inmediatas, no acciones de respuesta epidemiologica.

Alternativamente, fusionar con Tab 9 (Clasificacion) como seccion "Acciones tomadas".

**Esto reduciria de 9 a 8 tabs**, mejorando el flujo.

---

## 9. OTROS HALLAZGOS

### 9.1 `temperatura_celsius` deberia ser `type: 'number'` no `type: 'text'`

**Problema:** Definido como texto con validacion regex `'^\\d{2}([.,]\\d{1,2})?$'`. Un campo numerico con `step: 0.1, min: 35, max: 42` seria mas apropiado y daria validacion nativa del navegador.

**Recomendacion:** Cambiar a `type: 'number'` con `validation: { min: 35, max: 42, step: 0.1 }`.

### 9.2 `asintomatico` es logicamente derivable

**Problema:** Si todos los signos (fiebre, exantema, koplik, tos, conjuntivitis, coriza, adenopatias, artralgia) = NO, entonces `asintomatico` = SI. Obligar al usuario a marcarlo manualmente es redundante.

**Recomendacion:** Auto-calcular. Si CUALQUIER signo = SI, auto-marcar `asintomatico = NO`. Si TODOS = NO, auto-marcar SI. Permitir override manual.

### 9.3 `fecha_captacion` vs `fecha_notificacion`

**Problema:** En el contexto IGSS, la captacion y la notificacion suelen ser el mismo dia (el medico ve al paciente y notifica inmediatamente). Tener ambas como required agrega friccion.

**Recomendacion:** Copiar `fecha_notificacion` a `fecha_captacion` por defecto. El usuario puede cambiarla si difieren.

### 9.4 Campos legacy ocultos — limpieza pendiente

Hay 6 campos `hidden: true` que son legacy:
- `tipo_vacuna`, `numero_dosis_spr`, `fecha_ultima_dosis`, `observaciones_vacuna` (Tab 4)
- `destino_viaje` (Tab 6)
- `contacto_enfermo_catarro` (Tab 6)

**Recomendacion:** Estos campos deberian tener un comentario claro de por que existen y una fecha de expiracion para su eliminacion. Si los datos legacy ya se migraron a los campos nuevos (dosis_spr, dosis_sr, dosis_sprv, viaje_pais/departamento/municipio), se pueden eliminar del schema.

### 9.5 `envio_ficha` es meta-redundante

**Problema:** Pregunta "Enviaron Ficha Epidemiologica?" dentro de LA PROPIA ficha epidemiologica. Si estan llenando este formulario, la respuesta es SI.

**Recomendacion:** Eliminar o hacer `hidden: true`. Si se refiere a si enviaron la ficha al MSPAS (EPIWEB), entonces renombrar a: "Se notifico al MSPAS (EPIWEB)?" con opciones SI/NO/PENDIENTE.

### 9.6 Validacion de fechas cruzadas ausente

**Problema:** No hay validacion de que:
- `fecha_inicio_sintomas` <= `fecha_inicio_erupcion` (los sintomas siempre preceden la erupcion)
- `fecha_inicio_erupcion` <= `fecha_notificacion` (no se notifica antes de la erupcion)
- `fecha_notificacion` <= `fecha_captacion` (si son diferentes)
- `hosp_fecha` <= `fecha_egreso` (no se egresa antes de hospitalizar)
- `muestra_suero_fecha` >= `fecha_inicio_sintomas` (no se toma muestra antes de enfermar)

**Recomendacion:** Agregar validaciones cruzadas que muestren warnings (no errores bloqueantes) cuando las fechas son inconsistentes.

### 9.7 `correo_responsable` no tiene validacion de email

**Problema:** Campo de correo con `validation: { maxLength: 150 }` pero sin patron de email.

**Recomendacion:** Agregar `validation: { pattern: '^[^@]+@[^@]+\\.[^@]+$', maxLength: 150 }` o `type: 'email'`.

---

## 10. RESUMEN DE PRIORIDADES

### Alta prioridad (impacto significativo en UX)

| # | Accion | Esfuerzo | Impacto |
|---|--------|----------|---------|
| 1 | Auto-derivar `diagnostico_sospecha` desde CIE-10 | Bajo | Alto -- elimina redundancia #1 |
| 2 | Fusionar Tab 7 en Tab 5 o Tab 9 | Medio | Alto -- 8 tabs en vez de 9 |
| 3 | `comunidad_linguistica` como select searchable | Bajo | Medio -- datos limpios, menos typing |
| 4 | Fix `familiar_viajo_exterior` condicional incorrecto | Bajo | Alto -- error logico actual |
| 5 | `muestra_hisopado/orina` no required | Bajo | Medio -- evita bloqueo innecesario |

### Media prioridad (mejora incremental)

| # | Accion | Esfuerzo | Impacto |
|---|--------|----------|---------|
| 6 | Seccion Encargado condicional a edad < 18 | Medio | Medio |
| 7 | `hosp_nombre` como select searchable | Bajo | Medio |
| 8 | `cargo_responsable` como select | Bajo | Bajo |
| 9 | Auto-calcular `asintomatico` | Medio | Bajo |
| 10 | Default `fecha_captacion` = `fecha_notificacion` | Bajo | Medio |
| 11 | `antigeno_prueba` y `resultado_prueba` no required | Bajo | Medio |

### Baja prioridad (polish)

| # | Accion | Esfuerzo | Impacto |
|---|--------|----------|---------|
| 12 | Reordenar tabs segun workflow hospitalario | Alto | Medio |
| 13 | Validacion cruzada de fechas | Alto | Medio |
| 14 | `temperatura_celsius` como number | Bajo | Bajo |
| 15 | Eliminar `envio_ficha` o renombrar | Bajo | Bajo |
| 16 | Limpiar campos legacy hidden | Bajo | Bajo |
| 17 | `secuenciacion_resultado` como select de genotipos | Bajo | Bajo |
| 18 | `viaje_departamento` reutilizar select existente | Bajo | Bajo |

---

## 11. METRICAS DE IMPACTO ESTIMADO

- **Clicks/taps eliminados por formulario:** ~5-8 (auto-derivaciones + defaults)
- **Campos visibles reducidos para caso tipico (adulto masculino, no viajo, sin hospitalizacion):** de ~65 a ~55
- **Tabs reducidos:** de 9 a 8 (fusion Tab 7)
- **Campos texto libre convertidos a select:** 5-7 (datos mas limpios para analisis)
- **Errores logicos corregidos:** 2 (familiar_viajo condicional, muestras required)
