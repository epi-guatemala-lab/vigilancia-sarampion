# Especificacion Completa del Formulario IGSS -- Vigilancia Sarampion/Rubeola

**Fecha:** 2026-03-26
**Version:** 1.0
**Fuentes:** Ficha MSPAS 2026 (PDF), GoData Guatemala API (outbreak `ba06833f`), EPIWEB MSPAS, formSchema.js actual (186 campos)

> Este documento lista TODOS los campos del formulario, organizados por tab.
> Para cada campo se especifica: que es, que opciones tiene, si es obligatorio,
> y a donde va la informacion (GoData, EPIWEB, PDF, solo IGSS).
>
> **Leyenda de destinos:**
> - G = GoData -- Se envia a GoData Guatemala
> - E = EPIWEB -- Se envia al MSPAS via bot Playwright
> - P = PDF -- Aparece en la ficha PDF generada
> - I = IGSS -- Solo para uso interno del instituto
>
> **Leyenda de cambios vs formulario actual:**
> - *(sin marca)* = Sin cambios
> - **(MOD)** = Modificado (opciones, tipo, o comportamiento cambia)
> - **(NUEVO)** = Campo nuevo que no existe en el formulario actual
> - **(OCULTO)** = Se oculta del formulario (se mantiene en BD para compatibilidad)
> - **(ELIMINADO)** = Se elimina completamente

---

## Resumen por Tab

| Tab | Nombre | Campos visibles | Campos ocultos/auto |
|-----|--------|----------------|---------------------|
| 1 | Datos Generales | 17 | 6 |
| 2 | Datos del Paciente | 19 | 3 |
| 3 | Embarazo | 7 | 0 |
| 4 | Antecedentes y Vacunacion | 17 | 4 |
| 5 | Datos Clinicos | 25 | 0 |
| 6 | Factores de Riesgo | 13 | 1 |
| 7 | Acciones de Respuesta | 4 | 6 |
| 8 | Laboratorio | 22 | 0 |
| 9 | Clasificacion y Datos IGSS | 22 | 0 |
| **Total** | | **146** | **20** |

---

## Tab 1: Datos Generales

### 1.1 Diagnostico Registrado (CIE-10)

- **ID:** `diagnostico_registrado`
- **Tipo:** Select
- **Obligatorio:** Si
- **Destino:** I P
- **Opciones:**

| Opcion | Codigo CIE-10 |
|--------|---------------|
| B05 - Sarampion | B05 |
| B050 - Sarampion complicado por encefalitis | B050 |
| B051 - Sarampion complicado por meningitis | B051 |
| B052 - Sarampion complicado por una neumonia | B052 |
| B053 - Sarampion complicado por otitis media | B053 |
| B054 - Sarampion con complicaciones intestinales | B054 |
| B055 - Sarampion confirmado por laboratorio | B055 |
| B056 - Sarampion confirmado por nexo epidemiologico | B056 |
| B057 - Sarampion confirmado clinicamente | B057 |
| B058 - Sarampion con otras complicaciones | B058 |
| B059 - Sospechoso de Sarampion | B059 |
| B06 - Rubeola | B06 |
| B060 - Rubeola con complicaciones neurologicas | B060 |
| B061 - Rubeola con otras complicaciones | B061 |
| B069 - Rubeola sin complicaciones | B069 |

- **Nota:** Campo exclusivo IGSS. Genera automaticamente el campo `codigo_cie10`. No existe en ficha MSPAS ni en GoData.

### 1.2 Codigo CIE-10

- **ID:** `codigo_cie10`
- **Tipo:** Text (solo lectura)
- **Obligatorio:** No (auto-generado)
- **Destino:** I
- **Formula:** Se extrae automaticamente del `diagnostico_registrado` seleccionado via `diagnosticosMap`
- **Ejemplo:** Si se selecciona "B05 - Sarampion", el valor es "B05"

### 1.3 Diagnostico de Sospecha **(MOD)**

- **ID:** `diagnostico_sospecha`
- **Tipo:** Checkbox (seleccion multiple) -- **Propuesta: cambiar a single-select + sub-pregunta**
- **Obligatorio:** Si
- **Destino:** G P
- **Opciones:**

| Opcion en formulario | GoData valor | GoData variable |
|---------------------|-------------|-----------------|
| Sarampion | SARAMPION | `diagnostico_de_sospecha_` |
| Rubeola | RUBEOLA | `diagnostico_de_sospecha_` |
| Dengue | DENGUE | `diagnostico_de_sospecha_` |
| Otra Arbovirosis | OTRO ARBOVIROSIS | `diagnostico_de_sospecha_` |
| Otra febril exantematica | OTRO FEBRIL EXANTEMATICA | `diagnostico_de_sospecha_` |
| Caso altamente sospechoso de Sarampion | (sub-pregunta) | `caso_altamente_sospechoso_de_sarampion` = SI/NO |

- **GoData:** SINGLE_ANSWER -- solo acepta una seleccion. Si el usuario marca multiples, se envia la primera.
- **Sub-pregunta GoData:** "Caso altamente sospechoso" solo aparece si `diagnostico_de_sospecha_` = SARAMPION
- **Cambio propuesto:** Considerar cambiar a single-select en React para alinear con GoData. La opcion "Caso altamente sospechoso" seria una sub-pregunta SI/NO visible solo si se selecciona Sarampion.

### 1.4 Especifique diagnostico de sospecha

- **ID:** `diagnostico_sospecha_otro`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `diagnostico_sospecha` incluye "Otra Arbovirosis" u "Otra febril exantematica"
- **GoData:** `especifique` (sub-q de OTRO ARBOVIROSIS) o `especifique_` (sub-q de OTRO FEBRIL EXANTEMATICA)

### 1.5 Unidad Medica que Reporta

- **ID:** `unidad_medica`
- **Tipo:** Select (con busqueda)
- **Obligatorio:** Si
- **Destino:** I G P E
- **Opciones:** Lista completa de unidades medicas IGSS (importada de `unidadesMedicas.js`), incluye opcion "OTRA"
- **GoData:** Se mapea a `especifique_establecimiento` (sub-pregunta de `otro_establecimiento` = "Seguro Social (IGSS)")
- **GoData tambien:** Se mapea a `servicio_de_salud_*` (campo de texto bajo la DDRISS correspondiente)

### 1.6 Especifique la unidad medica

- **ID:** `unidad_medica_otra`
- **Tipo:** Text
- **Obligatorio:** Si (cuando visible)
- **Destino:** I P
- **Condicion:** Visible si `unidad_medica` = "OTRA"

### 1.7 Seguro Social (IGSS) -- Hardcodeado

- **ID:** `es_seguro_social`
- **Tipo:** Radio (oculto)
- **Valor fijo:** "SI"
- **Destino:** G P
- **GoData:** `otro_establecimiento` = "Seguro Social (IGSS)"
- **Razon:** IGSS siempre es Seguro Social por definicion. El usuario no necesita seleccionarlo.

### 1.8 Establecimiento Privado -- Hardcodeado

- **ID:** `establecimiento_privado`
- **Tipo:** Radio (oculto)
- **Valor fijo:** "NO"
- **Destino:** G P
- **GoData:** No se selecciona "ESTABLECIMIENTO PRIVADO" en `otro_establecimiento`
- **Razon:** IGSS nunca es establecimiento privado.

### 1.9 Nombre establecimiento privado -- Hardcodeado

- **ID:** `establecimiento_privado_nombre`
- **Tipo:** Text (oculto)
- **Valor fijo:** vacio
- **Destino:** G

### 1.10 Fecha de Notificacion

- **ID:** `fecha_notificacion`
- **Tipo:** Date
- **Obligatorio:** Si
- **Destino:** G E P
- **Validacion:** No puede ser fecha futura
- **GoData:** `dateOfReporting` (campo estandar) + `fecha_de_notificacion` (cuestionario)

### 1.11 Fecha de Registro de Diagnostico

- **ID:** `fecha_registro_diagnostico`
- **Tipo:** Date
- **Obligatorio:** Si
- **Destino:** G E P
- **Validacion:** No puede ser fecha futura
- **GoData:** `fecha_de_consulta` (sub-pregunta de `fecha_de_notificacion`)

### 1.12 Semana Epidemiologica

- **ID:** `semana_epidemiologica`
- **Tipo:** Number (solo lectura)
- **Obligatorio:** Si (auto-calculado)
- **Destino:** I P
- **Formula:** Se calcula automaticamente de `fecha_notificacion` usando sistema CDC/MMWR (domingo-sabado)
- **Validacion:** 1--53

### 1.13 Servicio que Reporta

- **ID:** `servicio_reporta`
- **Tipo:** Select
- **Obligatorio:** Si
- **Destino:** I P
- **Opciones:**

| Opcion |
|--------|
| EMERGENCIA |
| CONSULTA EXTERNA |
| ENCAMAMIENTO |
| OTRO |

### 1.14 Responsable de Notificacion

- **ID:** `nom_responsable`
- **Tipo:** Text
- **Obligatorio:** Si
- **Destino:** G E P
- **GoData:** `nombre_de_quien_investiga`

### 1.15 Cargo

- **ID:** `cargo_responsable`
- **Tipo:** Text
- **Obligatorio:** Si
- **Destino:** G E P
- **GoData:** `cargo_de_quien_investiga`

### 1.16 Telefono del Responsable

- **ID:** `telefono_responsable`
- **Tipo:** Phone
- **Obligatorio:** No
- **Destino:** G P
- **GoData:** `telefono`

### 1.17 Correo Electronico

- **ID:** `correo_responsable`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G P
- **GoData:** `correo_electronico`
- **Validacion:** Maximo 150 caracteres

### 1.18 Enviaron Ficha Epidemiologica?

- **ID:** `envio_ficha`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** I
- **Opciones:** SI, NO

### 1.19 Fuente de Notificacion **(MOD)**

- **ID:** `fuente_notificacion`
- **Tipo:** Select
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones actuales vs propuesta:**

| # | Opcion actual | GoData valor | Cambio propuesto |
|---|--------------|-------------|------------------|
| 1 | Servicio de Salud | SERVICIO DE SALUD | Sin cambio |
| 2 | Privada | -- | **(ELIMINADO)** -- no existe en PDF ni GoData. Cubierto por flag `establecimiento_privado` |
| 3 | Laboratorio | LABORATORIO | Sin cambio |
| 4 | Comunidad | CASO REPORTADO POR LA COMUNIDAD | **(MOD)** texto -> "Caso Reportado por la Comunidad" |
| 5 | Busqueda Activa Institucional | BUSQUEDA ACTIVA INSTITUCIONAL | Sin cambio |
| 6 | Busqueda Activa Comunitaria | BUSQUEDA ACTIVA COMUNITARIA | Sin cambio |
| 7 | Busqueda Activa Laboratorial | BUSQUEDA ACTIVA LABORATORIAL | Sin cambio |
| 8 | Investigacion de Contactos | INVESTIGACION DE CONTACTOS | Sin cambio |
| 9 | Auto Notificacion | AUTO NOTIFICACION POR NUMERO GRATUITO | **(MOD)** texto -> "Auto Notificacion por Numero Gratuito" |
| 10 | Defuncion | -- | **(ELIMINADO)** -- no existe en PDF ni GoData |
| 11 | Otra | OTRO | Sin cambio |

- **GoData:** `fuente_de_notificacion_` (SINGLE_ANSWER)

### 1.20 Otra fuente de notificacion

- **ID:** `fuente_notificacion_otra`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `fuente_notificacion` = "Otra"
- **GoData:** `especifique_fuente`

### 1.21 Fecha Visita Domiciliaria

- **ID:** `fecha_visita_domiciliaria`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** G P
- **Validacion:** No puede ser fecha futura
- **GoData:** `fecha_de_investigacion_domiciliaria`
- **Nota:** IGSS no realiza investigacion domiciliaria. Se mantiene opcional para registrar cuando el MSPAS la realiza.

### 1.22 Fecha Inicio Investigacion

- **ID:** `fecha_inicio_investigacion`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** I
- **Validacion:** No puede ser fecha futura

### 1.23 Busqueda Activa

- **ID:** `busqueda_activa`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** I
- **Opciones:** Retrospectiva en el servicio, Comunidad, Otras

### 1.24 Otra busqueda activa

- **ID:** `busqueda_activa_otra`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I
- **Condicion:** Visible si `busqueda_activa` = "Otras"

---

## Tab 2: Datos del Paciente

### 2.1 Numero de Afiliacion

- **ID:** `afiliacion`
- **Tipo:** Text
- **Obligatorio:** Si
- **Destino:** I P
- **Validacion:** 3--20 caracteres
- **Nota:** Identificador unico del paciente en el sistema IGSS. No existe en MSPAS ni GoData.

### 2.2 Tipo de Identificacion

- **ID:** `tipo_identificacion`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** G E P
- **Opciones:**

| Opcion | GoData sub-pregunta activada |
|--------|------------------------------|
| DPI | `no_de_dpi` (NUMERIC) |
| PASAPORTE | `no_de_pasaporte` (TEXT) |
| OTRO | `especifique_cui` (TEXT) |

- **GoData:** `codigo_unico_de_identificacion_dpi_pasaporte_otro`

### 2.3 Numero de Identificacion

- **ID:** `numero_identificacion`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G E P
- **Validacion:** Maximo 30 caracteres
- **GoData:** Se enruta al sub-campo correcto segun `tipo_identificacion`: `no_de_dpi`, `no_de_pasaporte`, o `especifique_cui`
- **Nota:** React usa un campo unificado; GoData tiene sub-campos separados por tipo.

### 2.4 Nombres

- **ID:** `nombres`
- **Tipo:** Text
- **Obligatorio:** Si
- **Destino:** G E P
- **Validacion:** 2--100 caracteres
- **GoData:** `firstName` (campo estandar). GoData tiene `middleName` adicional -- IGSS captura todo en un solo campo.

### 2.5 Apellidos

- **ID:** `apellidos`
- **Tipo:** Text
- **Obligatorio:** Si
- **Destino:** G E P
- **Validacion:** 2--100 caracteres
- **GoData:** `lastName` (campo estandar)

### 2.6 Sexo

- **ID:** `sexo`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:**

| Opcion | Label | GoData valor |
|--------|-------|-------------|
| M | Masculino | MALE |
| F | Femenino | FEMALE |

- **GoData:** `gender` (campo estandar)

### 2.7 Fecha de Nacimiento

- **ID:** `fecha_nacimiento`
- **Tipo:** Date
- **Obligatorio:** Si
- **Destino:** G E P
- **Validacion:** No puede ser fecha futura
- **GoData:** `dob` (campo estandar)

### 2.8 Edad en Anios

- **ID:** `edad_anios`
- **Tipo:** Number (solo lectura)
- **Obligatorio:** No (auto-calculado)
- **Destino:** G E P
- **Formula:** `floor((fecha_actual - fecha_nacimiento) / 365.25)`
- **GoData:** `age.years` (campo estandar)

### 2.9 Edad en Meses

- **ID:** `edad_meses`
- **Tipo:** Number (solo lectura)
- **Obligatorio:** No (auto-calculado)
- **Destino:** G E P
- **Formula:** Meses restantes despues de calcular anios completos (0--11)
- **GoData:** `age.months` (campo estandar)

### 2.10 Edad en Dias

- **ID:** `edad_dias`
- **Tipo:** Number (solo lectura)
- **Obligatorio:** No (auto-calculado)
- **Destino:** I E P
- **Formula:** Dias restantes despues de calcular meses completos (0--31)
- **GoData:** No tiene campo equivalente

### 2.11 Pueblo / Etnia **(MOD)**

- **ID:** `pueblo_etnia`
- **Tipo:** Select
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones actuales vs propuesta:**

| # | Opcion actual | GoData valor | Cambio |
|---|--------------|-------------|--------|
| 1 | Maya | MAYA | Sin cambio |
| 2 | Ladino / Mestizo | LADINO | **(MOD)** cambiar texto a "Ladino" para alinear con MSPAS/GoData |
| 3 | Garifuna | GARIFUNA | Sin cambio (GoData dice GARIFUNA con acento) |
| 4 | Xinca | XINCA | Sin cambio |
| 5 | Otros | -- | **(MOD)** mapear a "DESCONOCIDO" en GoData |
| 6 | Extranjero | -- | **(MOD)** mapear a "DESCONOCIDO" en GoData; evaluar eliminar |
| 7 | Desconocido | DESCONOCIDO | Sin cambio |

- **GoData:** `pueblo` (SINGLE_ANSWER, 5 opciones: LADINO, MAYA, GARIFUNA, XINCA, DESCONOCIDO)

### 2.12 Comunidad Linguistica **(MOD)**

- **ID:** `comunidad_linguistica`
- **Tipo:** Text libre -> **Propuesta: cambiar a Select**
- **Obligatorio:** No
- **Destino:** G E P
- **Condicion propuesta:** Solo visible si `pueblo_etnia` = "Maya"
- **Opciones propuestas (23 comunidades mayas de GoData):**

| # | Opcion | GoData valor |
|---|--------|-------------|
| 1 | Achi | Achi' |
| 2 | Akateka | Akateka |
| 3 | Awakateka | Awakateka |
| 4 | Ch'orti' | Ch'orti' |
| 5 | Chalchiteka | Chalchiteka |
| 6 | Chuj | Chuj |
| 7 | Itza' | Itza' |
| 8 | Ixil | Ixil |
| 9 | Jakalteka | Jakalteka |
| 10 | Kaqchikel | Kaqchikel |
| 11 | K'iche' | K'iche' |
| 12 | Mam | Mam |
| 13 | Mopan | Mopan |
| 14 | Poqomam | Poqomam |
| 15 | Pocomchi' | Pocomchi' |
| 16 | Q'anjob'al | Q'anjob'al |
| 17 | Q'eqchi' | Q'eqchi' |
| 18 | Sakapulteka | Sakapulteka |
| 19 | Sipakapensa | Sipakapensa |
| 20 | Tektiteka | Tektiteka |
| 21 | Tz'utujil | Tz'utujil |
| 22 | Uspanteka | Uspanteka |
| 23 | No indica | No indica |

- **GoData:** `comunidad_linguistica` (SINGLE_ANSWER, sub-pregunta de `pueblo` = MAYA)

### 2.13 Es Extranjero **(NUEVO)**

- **ID:** `es_extranjero`
- **Tipo:** Inferido automaticamente
- **Obligatorio:** No (auto-calculado)
- **Destino:** G P
- **Formula:** SI si `pais_residencia` != "GUATEMALA", NO en caso contrario
- **GoData:** `extranjero_` (SI/NO)
- **Nota:** GoData y PDF MSPAS tienen este campo. Se infiere de `pais_residencia` para no pedir doble dato al usuario.

### 2.14 Es Migrante

- **ID:** `es_migrante`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Opciones:** SI, NO
- **GoData:** `migrante` (SI/NO)

### 2.15 Ocupacion

- **ID:** `ocupacion`
- **Tipo:** Select (con busqueda)
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** Catalogo MSPAS EPIWEB (441 opciones, importado de `mspasOcupaciones.js`)
- **GoData:** `ocupacion_` (TEXT libre -- se envia el texto seleccionado)
- **Nota:** Se mantiene como select para compatibilidad con EPIWEB. GoData recibe como texto libre.

### 2.16 Escolaridad

- **ID:** `escolaridad`
- **Tipo:** Select
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones y mapeo GoData:**

| # | Opcion formulario | GoData valor | Notas |
|---|------------------|-------------|-------|
| 1 | Ninguna | NINGUNO | |
| 2 | Primaria Incompleta | PRIMARIA | Mapeo agrupado |
| 3 | Primaria Completa | PRIMARIA | Mapeo agrupado |
| 4 | Primaria | PRIMARIA | |
| 5 | Secundaria Incompleta | BASICOS | Mapeo agrupado |
| 6 | Secundaria Completa | BASICOS | Mapeo agrupado |
| 7 | Secundaria | BASICOS | |
| 8 | Diversificado Incompleto | DIVERSIFICADO | Mapeo agrupado |
| 9 | Diversificado Completo | DIVERSIFICADO | Mapeo agrupado |
| 10 | Diversificado | DIVERSIFICADO | |
| 11 | Universitaria Incompleta | UNIVERSIDAD | Mapeo agrupado |
| 12 | Universitaria Completa | UNIVERSIDAD | Mapeo agrupado |
| 13 | Universitario | UNIVERSIDAD | |
| 14 | Postgrado | UNIVERSIDAD | Mapeo agrupado |
| 15 | Alfabeto | OTRO | Mapeo |
| 16 | Analfabeto | NINGUNO | Mapeo |
| 17 | No aplica | NO APLICA | |

- **GoData:** `escolaridad_` (SINGLE_ANSWER, 9 opciones: NO APLICA, PRE PRIMARIA, PRIMARIA, BASICOS, DIVERSIFICADO, UNIVERSIDAD, NINGUNO, OTRO, NO INDICA)
- **Nota:** Se mantienen las 17 opciones para EPIWEB. El mapeo a las 9 opciones de GoData se hace automaticamente.

### 2.17 Telefono del Paciente

- **ID:** `telefono_paciente`
- **Tipo:** Phone
- **Obligatorio:** No
- **Destino:** G P
- **GoData:** `telefono_` (NUMERIC)

### 2.18 Pais de Residencia **(MOD)**

- **ID:** `pais_residencia`
- **Tipo:** Text (default "GUATEMALA") -> **Propuesta: cambiar a Select GUATEMALA/OTRO + especifique**
- **Obligatorio:** No (default GUATEMALA)
- **Destino:** G E P
- **Opciones propuestas:**

| Opcion | GoData valor |
|--------|-------------|
| GUATEMALA | GUATEMALA |
| OTRO | OTRO (activa sub-campo `especifique_pais`) |

- **GoData:** `pais_de_residencia_` (SINGLE_ANSWER: GUATEMALA, OTRO -> `especifique_pais` TEXT)
- **Cambio:** Actualmente es texto libre con default "GUATEMALA". GoData solo acepta GUATEMALA/OTRO.

### 2.19 Departamento de Residencia

- **ID:** `departamento_residencia`
- **Tipo:** Select
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** 22 departamentos de Guatemala

| # | Departamento |
|---|-------------|
| 1 | ALTA VERAPAZ |
| 2 | BAJA VERAPAZ |
| 3 | CHIMALTENANGO |
| 4 | CHIQUIMULA |
| 5 | EL PROGRESO |
| 6 | ESCUINTLA |
| 7 | GUATEMALA |
| 8 | HUEHUETENANGO |
| 9 | IZABAL |
| 10 | JALAPA |
| 11 | JUTIAPA |
| 12 | PETEN |
| 13 | QUETZALTENANGO |
| 14 | QUICHE |
| 15 | RETALHULEU |
| 16 | SACATEPEQUEZ |
| 17 | SAN MARCOS |
| 18 | SANTA ROSA |
| 19 | SOLOLA |
| 20 | SUCHITEPEQUEZ |
| 21 | TOTONICAPAN |
| 22 | ZACAPA |

- **GoData:** `departamento_de_residencia_` (cascading bajo `pais_de_residencia_` = GUATEMALA)

### 2.20 Municipio de Residencia

- **ID:** `municipio_residencia`
- **Tipo:** Select (cascading desde departamento, con busqueda)
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** Se cargan dinamicamente segun departamento seleccionado (importado de `mspasMunicipios.js`)
- **GoData:** `municipio_de_residencia_*` (cascading por departamento; variable suffixed con numero)

### 2.21 Poblado / Localidad

- **ID:** `poblado`
- **Tipo:** Select (cascading desde municipio, con busqueda)
- **Obligatorio:** No
- **Destino:** G E P
- **Opciones:** Se cargan dinamicamente segun departamento + municipio (importado de `mspasPoblados.js`)
- **GoData:** `lugar_poblado_` (TEXT libre -- se envia el nombre seleccionado como texto)

### 2.22 Direccion

- **ID:** `direccion_exacta`
- **Tipo:** Textarea
- **Obligatorio:** No
- **Destino:** G E P
- **Validacion:** Maximo 300 caracteres
- **GoData:** `direccion_de_residencia_` (TEXT)

### 2.23 Nombre del Encargado

- **ID:** `nombre_encargado`
- **Tipo:** Text
- **Obligatorio:** Si
- **Destino:** G E P
- **GoData:** `nombre_del_tutor_` (sub-pregunta, valor = "SI" activa nombre + parentesco + ID)
- **Nota:** IGSS siempre muestra este campo. GoData tiene un gate "Tiene tutor?" SI/NO -- se envia como "SI" cuando hay valor.

### 2.24 Parentesco del Encargado

- **ID:** `parentesco_tutor`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** G P
- **Opciones:**

| Opcion |
|--------|
| Madre |
| Padre |
| Abuelo/a |
| Tio/a |
| Hermano/a |
| Otro |

- **GoData:** `parentesco_` (TEXT libre -- se envia el texto seleccionado)

### 2.25 Tipo de Identificacion del Encargado

- **ID:** `tipo_id_tutor`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** G P
- **Opciones:** DPI, PASAPORTE, OTRO
- **GoData:** `codigo_unico_de_identificacion_dpi_pasaporte_otro_` (sub-pregunta del tutor)

### 2.26 Numero de Identificacion del Encargado

- **ID:** `numero_id_tutor`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G P
- **Validacion:** Maximo 30 caracteres
- **GoData:** Se enruta a `no_de_dpi_`, `no_de_pasaporte_`, o `especifique_doc` segun `tipo_id_tutor`

### 2.27 Telefono del Encargado

- **ID:** `telefono_encargado`
- **Tipo:** Phone
- **Obligatorio:** No
- **Destino:** I P
- **Nota:** Campo exclusivo IGSS para contacto adicional.

---

## Tab 3: Embarazo

**Condicion general:** Todo este tab solo es visible si `sexo` = F

### 3.1 Esta Embarazada?

- **ID:** `esta_embarazada`
- **Tipo:** Radio
- **Obligatorio:** Si (cuando visible)
- **Destino:** G E P
- **Opciones:** SI, NO, N/A
- **GoData:** `pregnancyStatus` (campo estandar de referencia)

### 3.2 Esta Lactando?

- **ID:** `lactando`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** I P
- **Opciones:** SI, NO
- **GoData:** No tiene campo equivalente

### 3.3 Semanas de Embarazo

- **ID:** `semanas_embarazo`
- **Tipo:** Number
- **Obligatorio:** Si (cuando visible)
- **Destino:** I E P
- **Condicion:** Visible si `esta_embarazada` = "SI"
- **Validacion:** 1--42
- **GoData:** No tiene campo directo

### 3.4 Trimestre

- **ID:** `trimestre_embarazo`
- **Tipo:** Select (solo lectura, auto-calculado)
- **Obligatorio:** No (auto-calculado)
- **Destino:** I E P
- **Condicion:** Visible si `esta_embarazada` = "SI"
- **Formula:** `ceil(semanas_embarazo / 13)` -> 1, 2, o 3
- **Opciones:** 1, 2, 3

### 3.5 Fecha Probable de Parto

- **ID:** `fecha_probable_parto`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `esta_embarazada` = "SI"

### 3.6 Vacuna (en embarazada)

- **ID:** `vacuna_embarazada`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `esta_embarazada` = "SI"
- **Opciones:** SI, NO, N/S, N/A

### 3.7 Fecha de Vacunacion (embarazada)

- **ID:** `fecha_vacunacion_embarazada`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `vacuna_embarazada` = "SI"
- **Validacion:** No puede ser fecha futura

---

## Tab 4: Antecedentes y Vacunacion

### 4.1 Vacunado contra Sarampion **(MOD)**

- **ID:** `vacunado`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones actuales vs GoData:**

| # | Opcion actual | GoData valor | Notas |
|---|--------------|-------------|-------|
| 1 | SI | SI | |
| 2 | NO | NO | |
| 3 | DESCONOCIDO | DESCONOCIDO | |
| -- | (no existe) | VERBAL | **(NUEVO)** GoData tiene " VERBAL" (con espacio al inicio) |

- **GoData:** `paciente_vacunado_` (SINGLE_ANSWER, 4 opciones: SI, NO, " VERBAL", DESCONOCIDO)
- **Propuesta:** Agregar opcion "VERBAL" para cuando el paciente informa verbalmente pero no tiene carne. Alternativamente, mapear: cuando `fuente_info_vacuna` = "Verbal", enviar "VERBAL" a GoData en vez de "SI".

### 4.2 Fuente de Informacion sobre Vacunacion

- **ID:** `fuente_info_vacuna`
- **Tipo:** Select
- **Obligatorio:** Si (cuando visible)
- **Destino:** G P
- **Condicion:** Visible si `vacunado` = "SI"
- **Opciones:**

| # | Opcion | GoData valor |
|---|--------|-------------|
| 1 | Carne de Vacunacion | CARNE DE VACUNACION |
| 2 | SIGSA 5a Cuaderno | SIGSA 5A CUADERNO |
| 3 | SIGSA 5B Otros Grupos | SIGSA 5B OTROS GRUPOS |
| 4 | Registro Unico de Vacunacion | REGISTRO UNICO DE VACUNACION |
| 5 | Verbal | -- (GoData no tiene; se mapea a `vacunado` = VERBAL) |

- **GoData:** `fuente_de_la_informacion_sobre_la_vacunacion_` (SINGLE_ANSWER, 4 opciones -- no incluye "Verbal")
- **Nota:** Cuando fuente = "Verbal", NO se envia a GoData fuente; en su lugar se cambia `paciente_vacunado_` a "VERBAL".

### 4.3 Sector de Vacunacion

- **ID:** `sector_vacunacion`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `vacunado` = "SI"
- **Opciones:**

| Opcion | GoData valor |
|--------|-------------|
| MSPAS | MSPAS |
| IGSS | IGSS |
| Privado | PRIVADO |

- **GoData:** `vacunacion_en_el_sector_` (SINGLE_ANSWER)

### 4.4 Numero de Dosis SPR

- **ID:** `dosis_spr`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** G E P
- **Condicion:** Visible si `vacunado` = "SI"
- **Opciones:** 1, 2, 3, Mas de 3, No recuerda
- **GoData:** `numero_de_dosis` (NUMERIC, sub-pregunta de `tipo_de_vacuna_recibida_` = "SPR -- Sarampion Paperas Rubeola")

### 4.5 Fecha Ultima Dosis SPR

- **ID:** `fecha_ultima_spr`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** G E P
- **Condicion:** Visible si `vacunado` = "SI"
- **Validacion:** No puede ser fecha futura
- **GoData:** `fecha_de_la_ultima_dosis` (TIME, sub-pregunta de SPR)

### 4.6 Numero de Dosis SR

- **ID:** `dosis_sr`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** G E P
- **Condicion:** Visible si `vacunado` = "SI"
- **Opciones:** 1, 2, 3, Mas de 3, No recuerda
- **GoData:** `numero_de_dosis_` (NUMERIC, sub-pregunta de `tipo_de_vacuna_recibida_` = "SR -- Sarampion Rubeola")

### 4.7 Fecha Ultima Dosis SR

- **ID:** `fecha_ultima_sr`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** G E P
- **Condicion:** Visible si `vacunado` = "SI"
- **Validacion:** No puede ser fecha futura
- **GoData:** `fecha_de_la_ultima_dosis_` (TIME, sub-pregunta de SR)

### 4.8 Numero de Dosis SPRV

- **ID:** `dosis_sprv`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** I E P
- **Condicion:** Visible si `vacunado` = "SI"
- **Opciones:** 1, 2, 3, Mas de 3, No recuerda
- **GoData:** NO EXISTE. SPRV (Sarampion Paperas Rubeola Varicela) no esta configurado en GoData Guatemala.
- **Nota:** Se mantiene en el formulario y BD para EPIWEB y PDF. No se sincroniza a GoData.

### 4.9 Fecha Ultima Dosis SPRV

- **ID:** `fecha_ultima_sprv`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** I E P
- **Condicion:** Visible si `vacunado` = "SI"
- **Validacion:** No puede ser fecha futura
- **GoData:** NO EXISTE

### 4.10 Tipo de Vacuna (legacy) **(OCULTO)**

- **ID:** `tipo_vacuna`
- **Tipo:** Select (oculto)
- **Destino:** I (compatibilidad retroactiva)
- **Opciones:** Antisarampinosa, Antirubeoloica, SR Sarampion Rubeola, SRP Sarampion Rubeola Paperas, No recuerda
- **Nota:** Campo legacy oculto. Se mantiene en BD para datos historicos.

### 4.11 Numero de Dosis legacy **(OCULTO)**

- **ID:** `numero_dosis_spr`
- **Tipo:** Select (oculto)
- **Destino:** I
- **Opciones:** 1 dosis, 2 dosis, 3 dosis, Mas de 3 dosis, No recuerda

### 4.12 Fecha Ultima Dosis legacy **(OCULTO)**

- **ID:** `fecha_ultima_dosis`
- **Tipo:** Date (oculto)
- **Destino:** I

### 4.13 Observaciones de Vacunacion **(OCULTO)**

- **ID:** `observaciones_vacuna`
- **Tipo:** Text (oculto)
- **Destino:** I

### 4.14 Tiene Antecedentes Medicos?

- **ID:** `tiene_antecedentes_medicos`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `antecedentes_medicos_` (SINGLE_ANSWER: SI, NO, DESCONOCIDO)

### 4.15 Detalle de Antecedentes Medicos

- **ID:** `antecedentes_medicos_detalle`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `tiene_antecedentes_medicos` = "SI"
- **Validacion:** Maximo 500 caracteres
- **GoData:** `especifique_A` (TEXT, sub-pregunta de `especifique_ant` = "OTRO")

### 4.16 Desnutricion

- **ID:** `antecedente_desnutricion`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `tiene_antecedentes_medicos` = "SI"
- **Opciones:** SI, NO
- **GoData:** Si = SI, se incluye "DESNUTRICION" en `especifique_ant` (MULTI_ANSWER)

### 4.17 Inmunocompromiso

- **ID:** `antecedente_inmunocompromiso`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `tiene_antecedentes_medicos` = "SI"
- **Opciones:** SI, NO
- **GoData:** Si = SI, se incluye "INMUNOCOMPROMISO" en `especifique_ant`

### 4.18 Enfermedad Cronica

- **ID:** `antecedente_enfermedad_cronica`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `tiene_antecedentes_medicos` = "SI"
- **Opciones:** SI, NO
- **GoData:** Si = SI, se incluye "ENFERMEDAD CRONICA" en `especifique_ant`

---

## Tab 5: Datos Clinicos

### 5.1 Fecha Inicio Sintomas

- **ID:** `fecha_inicio_sintomas`
- **Tipo:** Date
- **Obligatorio:** Si
- **Destino:** G E P
- **Validacion:** No puede ser fecha futura
- **GoData:** `fecha_de_inicio_de_sintomas_` (TIME) + `dateOfOnset` (campo estandar)

### 5.2 Fecha de Captacion

- **ID:** `fecha_captacion`
- **Tipo:** Date
- **Obligatorio:** Si
- **Destino:** I E P
- **Validacion:** No puede ser fecha futura
- **Nota:** EPIWEB requiere este campo. No existe en GoData ni PDF MSPAS.

### 5.3 Fecha Inicio Erupcion

- **ID:** `fecha_inicio_erupcion`
- **Tipo:** Date
- **Obligatorio:** Si
- **Destino:** G E P
- **Validacion:** No puede ser fecha futura
- **GoData:** `fecha_de_inicio_de_exantema_rash_` (TIME)

### 5.4 Sitio de Inicio de Erupcion

- **ID:** `sitio_inicio_erupcion`
- **Tipo:** Select
- **Obligatorio:** Si
- **Destino:** I E P
- **Opciones:**

| Opcion |
|--------|
| Retroauricular |
| Cara |
| Cuello |
| Torax |
| Otro |

- **GoData:** No tiene campo equivalente
- **EPIWEB:** Campo requerido

### 5.5 Otro sitio de erupcion

- **ID:** `sitio_inicio_erupcion_otro`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `sitio_inicio_erupcion` = "Otro"

### 5.6 Fecha Inicio Fiebre

- **ID:** `fecha_inicio_fiebre`
- **Tipo:** Date
- **Obligatorio:** Si
- **Destino:** G E P
- **Validacion:** No puede ser fecha futura
- **GoData:** `fecha_de_inicio_de_fiebre_` (TIME)

### 5.7 Temperatura C

- **ID:** `temperatura_celsius`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G P
- **Validacion:** Patron `^\d{2}([.,]\d{1,2})?$` (ej: 38.5 o 38,5)
- **GoData:** `temp_c` (NUMERIC, sub-pregunta de `que_sintomas_` = "Fiebre")

### Signos y Sintomas (5.8--5.16)

**Estructura React:** 8 campos radio individuales con opciones SI/NO/DESCONOCIDO cada uno.

**Estructura GoData:** Gate `sintomas_` (SI/NO), luego `que_sintomas_` (MULTI_ANSWER con 8 opciones). Solo se marcan los sintomas presentes; no hay concepto de "DESCONOCIDO" por sintoma.

**Mapeo GoData:**
- Si al menos un signo = "SI" -> `sintomas_` = "SI", y el array `que_sintomas_` incluye los que son SI
- Si todos los signos = "NO" -> `sintomas_` = "NO"
- Los signos "DESCONOCIDO" se excluyen del array (perdida de informacion aceptable)

### 5.8 Fiebre

- **ID:** `signo_fiebre`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `que_sintomas_` incluye "Fiebre"

### 5.9 Exantema

- **ID:** `signo_exantema`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `que_sintomas_` incluye "Exantema/ Rash"

### 5.10 Manchas de Koplik

- **ID:** `signo_manchas_koplik`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `que_sintomas_` incluye "Manchas de Koplik"

### 5.11 Tos

- **ID:** `signo_tos`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `que_sintomas_` incluye "Tos"

### 5.12 Conjuntivitis

- **ID:** `signo_conjuntivitis`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `que_sintomas_` incluye "Conjuntivitis"

### 5.13 Coriza (catarro)

- **ID:** `signo_coriza`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `que_sintomas_` incluye "Coriza / Catarro"

### 5.14 Adenopatias

- **ID:** `signo_adenopatias`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `que_sintomas_` incluye "Adenopatias"

### 5.15 Artralgia o Artritis

- **ID:** `signo_artralgia`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `que_sintomas_` incluye "Artralgia / Artritis"

### 5.16 Asintomatico

- **ID:** `asintomatico`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** I P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** No tiene campo directo. Si asintomatico = SI, se envian todos los sintomas como NO.

### 5.17 Fue Hospitalizado?

- **ID:** `hospitalizado`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `hospitalizacion_` (SINGLE_ANSWER: SI, NO, DESCONOCIDO)

### 5.18 Nombre del Hospital

- **ID:** `hosp_nombre`
- **Tipo:** Text
- **Obligatorio:** Si (cuando visible)
- **Destino:** G E P
- **Condicion:** Visible si `hospitalizado` = "SI"
- **GoData:** `nombre_del_hospital_` (TEXT)

### 5.19 Fecha de Hospitalizacion

- **ID:** `hosp_fecha`
- **Tipo:** Date
- **Obligatorio:** Si (cuando visible)
- **Destino:** G E P
- **Condicion:** Visible si `hospitalizado` = "SI"
- **Validacion:** No puede ser fecha futura
- **GoData:** `fecha_de_hospitalizacion_` (TIME)

### 5.20 No. de Registro Medico

- **ID:** `no_registro_medico`
- **Tipo:** Text
- **Obligatorio:** Si (cuando visible)
- **Destino:** I P
- **Condicion:** Visible si `hospitalizado` = "SI"

### 5.21 Condicion de Egreso

- **ID:** `condicion_egreso`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `hospitalizado` = "SI"
- **Opciones:** MEJORADO, GRAVE, MUERTO
- **Nota:** Este es el egreso hospitalario. Diferente de `condicion_final_paciente` en Tab 9.

### 5.22 Fecha de Egreso

- **ID:** `fecha_egreso`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `hospitalizado` = "SI"
- **Validacion:** No puede ser fecha futura

### 5.23 Fecha de Defuncion

- **ID:** `fecha_defuncion`
- **Tipo:** Date
- **Obligatorio:** Si (cuando visible)
- **Destino:** G P
- **Condicion:** Visible si `condicion_egreso` = "MUERTO"
- **Validacion:** No puede ser fecha futura
- **GoData:** `fecha_de_defuncion` (TIME, sub-pregunta de `condicion_final_del_paciente` = "3")

### 5.24 Medico que Certifica Defuncion

- **ID:** `medico_certifica_defuncion`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `condicion_egreso` = "MUERTO"

### 5.25 Motivo de Consulta / Observaciones Clinicas

- **ID:** `motivo_consulta`
- **Tipo:** Textarea
- **Obligatorio:** No
- **Destino:** I P
- **Validacion:** Maximo 500 caracteres

### 5.26 Presenta Complicaciones?

- **ID:** `tiene_complicaciones`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `complicaciones_` (SINGLE_ANSWER: SI, NO, DESCONOCIDO)

### 5.27 Neumonia

- **ID:** `comp_neumonia`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `tiene_complicaciones` = "SI"
- **Opciones:** SI, NO
- **GoData:** Si = SI, se incluye "NEUMONIA" en `especifique_complicaciones_` (MULTI_ANSWER)

### 5.28 Encefalitis

- **ID:** `comp_encefalitis`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `tiene_complicaciones` = "SI"
- **Opciones:** SI, NO
- **GoData:** "ENCEFALITIS" en `especifique_complicaciones_`

### 5.29 Diarrea

- **ID:** `comp_diarrea`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `tiene_complicaciones` = "SI"
- **Opciones:** SI, NO
- **GoData:** "DIARREA" en `especifique_complicaciones_`

### 5.30 Trombocitopenia

- **ID:** `comp_trombocitopenia`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `tiene_complicaciones` = "SI"
- **Opciones:** SI, NO
- **GoData:** "TROMBOCITOPENIA" en `especifique_complicaciones_`

### 5.31 Otitis

- **ID:** `comp_otitis`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `tiene_complicaciones` = "SI"
- **Opciones:** SI, NO
- **GoData:** "OTITIS MEDIA AGUDA" en `especifique_complicaciones_`
- **Nota:** GoData dice "OTITIS MEDIA AGUDA", el formulario dice "Otitis". El mapeo expande el nombre.

### 5.32 Ceguera

- **ID:** `comp_ceguera`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `tiene_complicaciones` = "SI"
- **Opciones:** SI, NO
- **GoData:** "CEGUERA" en `especifique_complicaciones_`

### 5.33 Otra complicacion

- **ID:** `comp_otra_texto`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `tiene_complicaciones` = "SI"
- **Validacion:** Maximo 300 caracteres
- **GoData:** "OTRA" en `especifique_complicaciones_` + `especique` (TEXT -- nota: typo en GoData, sin la 'f')

### 5.34 Se realizo aislamiento respiratorio?

- **ID:** `aislamiento_respiratorio`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `aislamiento_respiratorio` (SINGLE_ANSWER: SI, NO, DESCONOCIDO)

### 5.35 Fecha de Aislamiento

- **ID:** `fecha_aislamiento`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `aislamiento_respiratorio` = "SI"
- **Validacion:** No puede ser fecha futura
- **GoData:** `fecha_de_aislamiento` (TIME)

---

## Tab 6: Factores de Riesgo

### 6.1 Contacto con caso sospechoso (7-23 dias antes)

- **ID:** `contacto_sospechoso_7_23`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `tuvo_contacto_con_un_caso_sospechoso_o_confirmado` (SINGLE_ANSWER: Si, No, Desconocido)
- **Nota:** GoData dice "sospechoso o confirmado". El formulario dice solo "sospechoso".

### 6.2 Caso sospechoso en comunidad/municipio (ultimos 3 meses)

- **ID:** `caso_sospechoso_comunidad_3m`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `Existe_caso_en_muni` (SINGLE_ANSWER: Si, No, Desconocido)

### 6.3 Viajo durante los 7-23 dias previos

- **ID:** `viajo_7_23_previo`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** SI, NO
- **GoData:** `viajo_durante_los_7_23_dias` (SINGLE_ANSWER: Si, No)
- **Nota:** Ni React ni GoData tienen opcion "DESCONOCIDO" para este campo.

### 6.4 Pais de Destino del Viaje **(MOD)**

- **ID:** `viaje_pais`
- **Tipo:** Text -> **Propuesta: cambiar a Select GUATEMALA/OTRO + especifique**
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `viajo_7_23_previo` = "SI"
- **Opciones propuestas:**

| Opcion | GoData valor |
|--------|-------------|
| GUATEMALA | GUATEMALA (activa sub-campo departamento) |
| OTRO | OTRO (activa sub-campo `especifique_pais1`) |

- **GoData:** `pais_departamento_y_municipio` (SINGLE_ANSWER: GUATEMALA, OTRO)

### 6.5 Departamento de Destino **(MOD)**

- **ID:** `viaje_departamento`
- **Tipo:** Text -> **Propuesta: cambiar a Select (22 departamentos)**
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `viajo_7_23_previo` = "SI" y `viaje_pais` = "GUATEMALA"
- **GoData:** `departamento` (SINGLE_ANSWER, 22 departamentos)

### 6.6 Municipio de Destino

- **ID:** `viaje_municipio`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `viajo_7_23_previo` = "SI"
- **Validacion:** Maximo 60 caracteres
- **GoData:** `municipio` (TEXT libre)

### 6.7 Fecha de Salida

- **ID:** `viaje_fecha_salida`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `viajo_7_23_previo` = "SI"
- **Validacion:** No puede ser fecha futura
- **GoData:** `fecha_de_salida_viaje` (TIME)

### 6.8 Fecha de Regreso

- **ID:** `viaje_fecha_entrada`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `viajo_7_23_previo` = "SI"
- **Validacion:** No puede ser fecha futura
- **GoData:** `fecha_de_entrada_viaje` (TIME)

### 6.9 Destino de viaje (legacy) **(OCULTO)**

- **ID:** `destino_viaje`
- **Tipo:** Text (oculto)
- **Destino:** I (compatibilidad retroactiva con EPIWEB)

### 6.10 Familiar viajo al exterior?

- **ID:** `familiar_viajo_exterior`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `viajo_7_23_previo` = "SI"
- **Opciones:** SI, NO
- **GoData:** `alguna_persona_de_su_casa_ha_viajado_al_exterior` (SINGLE_ANSWER: Si, No)

### 6.11 Fecha de Retorno del Familiar

- **ID:** `familiar_fecha_retorno`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `familiar_viajo_exterior` = "SI"
- **Validacion:** No puede ser fecha futura
- **GoData:** `fecha_de_retorno` (TIME)

### 6.12 Contacto con enfermo con catarro/erupcion?

- **ID:** `contacto_enfermo_catarro`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** I E P
- **Opciones:** SI, NO
- **GoData:** No tiene campo equivalente (campo EPIWEB legacy)

### 6.13 Contacto con embarazada?

- **ID:** `contacto_embarazada`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `el_paciente_estuvo_en_contacto_con_una_mujer_embarazada1` (SINGLE_ANSWER: Si, No, Desconocido)

### 6.14 Fuente Posible de Contagio **(MOD)**

- **ID:** `fuente_posible_contagio`
- **Tipo:** Select (single) -> **Propuesta: cambiar a multi-select para alinear con GoData**
- **Obligatorio:** No
- **Destino:** G P
- **Opciones:**

| # | Opcion | GoData valor |
|---|--------|-------------|
| 1 | Contacto en el hogar | Contacto en el hogar |
| 2 | Servicio de Salud | Servicio de Salud |
| 3 | Institucion Educativa | Institucion Educativa |
| 4 | Espacio Publico | Espacio Publico |
| 5 | Evento Masivo | Evento Masivo |
| 6 | Transporte Internacional | Transporte Internacional |
| 7 | Comunidad | Comunidad |
| 8 | Desconocido | Desconocido |
| 9 | Otro | Otro (activa `otro_especifique`) |

- **GoData:** `fuente_posible_de_contagio1` (MULTI_ANSWER -- permite multiples selecciones)
- **Nota:** GoData permite seleccionar multiples fuentes. React actualmente es single-select.

### 6.15 Otra fuente de contagio

- **ID:** `fuente_contagio_otro`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `fuente_posible_contagio` incluye "Otro"
- **Validacion:** Maximo 200 caracteres
- **GoData:** `otro_especifique` (TEXT)

---

## Tab 7: Acciones de Respuesta

**Contexto IGSS:** El IGSS no realiza actividades de campo (BAC, vacunacion de bloqueo/barrido, monitoreo rapido). Esas son responsabilidad del MSPAS. Se ocultan los campos correspondientes pero se mantienen en BD para compatibilidad con GoData (se envian como "NO"/vacio).

**GoData gate:** GoData tiene un campo `acciones_de_respuesta` (SI/NO) que controla toda la seccion. Si NO -> sub-pregunta `por_que_no_acciones_respuesta`. Este gate no existe en el formulario React.

### 7.1 Se realizo BAI?

- **ID:** `bai_realizada`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Opciones:** SI, NO
- **GoData:** `se_realizo_busqueda_activa_institucional_de_casos_bai` (SINGLE_ANSWER: "1" = Si, "2" = No)
- **Nota:** IGSS si puede realizar BAI dentro de sus instalaciones.

### 7.2 Casos sospechosos en BAI

- **ID:** `bai_casos_sospechosos`
- **Tipo:** Number
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `bai_realizada` = "SI"
- **Validacion:** 0--9999
- **GoData:** `numero_de_casos_sospechosos_identificados_en_bai` (NUMERIC)

### 7.3 Se realizo BAC? **(OCULTO)**

- **ID:** `bac_realizada`
- **Tipo:** Radio (oculto)
- **Destino:** G (se envia como "2" = No)
- **Razon:** IGSS no realiza busqueda activa comunitaria. Actividad de campo MSPAS.

### 7.4 Casos sospechosos en BAC **(OCULTO)**

- **ID:** `bac_casos_sospechosos`
- **Tipo:** Number (oculto)
- **Destino:** G

### 7.5 Vacunacion de bloqueo? **(OCULTO)**

- **ID:** `vacunacion_bloqueo`
- **Tipo:** Radio (oculto)
- **Destino:** G (se envia como "2" = No)
- **Razon:** IGSS no realiza vacunacion de bloqueo.

### 7.6 Monitoreo rapido de vacunacion? **(OCULTO)**

- **ID:** `monitoreo_rapido_vacunacion`
- **Tipo:** Radio (oculto)
- **Destino:** G (se envia como "2" = No)
- **Razon:** Actividad de campo MSPAS.

### 7.7 Vacunacion de barrido? **(OCULTO)**

- **ID:** `vacunacion_barrido`
- **Tipo:** Radio (oculto)
- **Destino:** G (se envia como "2" = No)
- **Razon:** IGSS no hace vacunacion de barrido.

### 7.8 Se administro Vitamina A?

- **ID:** `vitamina_a_administrada`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Opciones:** SI, NO, DESCONOCIDO
- **GoData:** `se_le_administro_vitamina_a` (SINGLE_ANSWER: "1" = Si, "2" = No, "3" = Desconocido)
- **Nota:** IGSS si administra Vitamina A en sus hospitales.

### 7.9 Dosis de Vitamina A

- **ID:** `vitamina_a_dosis`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `vitamina_a_administrada` = "SI"
- **Opciones:** 1, 2, 3, 4 o mas, Desconocido
- **GoData:** `numero_de_dosis_de_vitamina_a_recibidas` (NUMERIC)

---

## Tab 8: Laboratorio

**Nota GoData:** GoData maneja resultados de laboratorio via un endpoint API separado (`lab-results`), no via el cuestionario del caso. Los campos aqui se envian como registros de lab-results asociados al caso.

### 8.1 Recolecto Muestra

- **ID:** `recolecto_muestra`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones:** SI, NO

### 8.2 Motivo de no recoleccion

- **ID:** `motivo_no_recoleccion`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I E P
- **Condicion:** Visible si `recolecto_muestra` = "NO"

### 8.3 Suero

- **ID:** `muestra_suero`
- **Tipo:** Radio
- **Obligatorio:** Si (cuando visible)
- **Destino:** G E P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Opciones:** SI, NO
- **GoData:** Lab-results con `sampleType` = SERUM

### 8.4 Fecha Recoleccion Suero

- **ID:** `muestra_suero_fecha`
- **Tipo:** Date
- **Obligatorio:** Si (cuando visible)
- **Destino:** G E P
- **Condicion:** Visible si `muestra_suero` = "SI"
- **Validacion:** No puede ser fecha futura
- **GoData:** `dateSampleTaken` en lab-result

### 8.5 Hisopado Nasofaringeo

- **ID:** `muestra_hisopado`
- **Tipo:** Radio
- **Obligatorio:** Si (cuando visible)
- **Destino:** G E P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Opciones:** SI, NO
- **GoData:** Lab-results con `sampleType` = THROAT_SWAB

### 8.6 Fecha Recoleccion Hisopado

- **ID:** `muestra_hisopado_fecha`
- **Tipo:** Date
- **Obligatorio:** Si (cuando visible)
- **Destino:** G E P
- **Condicion:** Visible si `muestra_hisopado` = "SI"
- **Validacion:** No puede ser fecha futura

### 8.7 Orina

- **ID:** `muestra_orina`
- **Tipo:** Radio
- **Obligatorio:** Si (cuando visible)
- **Destino:** G E P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Opciones:** SI, NO
- **GoData:** Lab-results con `sampleType` = URINE

### 8.8 Fecha Recoleccion Orina

- **ID:** `muestra_orina_fecha`
- **Tipo:** Date
- **Obligatorio:** Si (cuando visible)
- **Destino:** G E P
- **Condicion:** Visible si `muestra_orina` = "SI"
- **Validacion:** No puede ser fecha futura

### 8.9 Otra Muestra

- **ID:** `muestra_otra`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Opciones:** SI, NO

### 8.10 Descripcion Otra Muestra

- **ID:** `muestra_otra_descripcion`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `muestra_otra` = "SI"

### 8.11 Fecha Recoleccion Otra Muestra

- **ID:** `muestra_otra_fecha`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `muestra_otra` = "SI"
- **Validacion:** No puede ser fecha futura

### 8.12 Antigeno

- **ID:** `antigeno_prueba`
- **Tipo:** Select
- **Obligatorio:** Si (cuando visible)
- **Destino:** G E P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Opciones:** Sarampion, Rubeola, Dengue, Otros
- **GoData:** `testedFor` en lab-result

### 8.13 Otro Antigeno

- **ID:** `antigeno_otro`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `antigeno_prueba` = "Otros"

### 8.14 Resultado de Prueba

- **ID:** `resultado_prueba`
- **Tipo:** Select
- **Obligatorio:** Si (cuando visible)
- **Destino:** G E P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Opciones:** Negativo, Positivo, Muestra Inadecuada, Indeterminada
- **GoData:** `result` en lab-result

### 8.15 Fecha Recepcion en Laboratorio

- **ID:** `fecha_recepcion_laboratorio`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Validacion:** No puede ser fecha futura
- **GoData:** `dateSampleDelivered` en lab-result

### 8.16 Fecha de Resultado

- **ID:** `fecha_resultado_laboratorio`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Validacion:** No puede ser fecha futura
- **GoData:** `dateOfResult` en lab-result

### 8.17 Resultado IgG Cualitativo

- **ID:** `resultado_igg_cualitativo`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Opciones:** REACTIVO, NO REACTIVO, INDETERMINADO, PENDIENTE, N/A
- **Nota:** Campo exclusivo del laboratorio IGSS. No se sincroniza directamente a GoData.

### 8.18 Resultado IgG Numerico

- **ID:** `resultado_igg_numerico`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Nota:** Valor cuantitativo del laboratorio IGSS.

### 8.19 Resultado IgM Cualitativo

- **ID:** `resultado_igm_cualitativo`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Opciones:** REACTIVO, NO REACTIVO, INDETERMINADO, PENDIENTE, N/A

### 8.20 Resultado IgM Numerico

- **ID:** `resultado_igm_numerico`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `recolecto_muestra` = "SI"

### 8.21 Resultado RT-PCR Orina

- **ID:** `resultado_pcr_orina`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Opciones:** POSITIVO, NEGATIVO, PENDIENTE, N/A

### 8.22 Resultado RT-PCR Hisopado

- **ID:** `resultado_pcr_hisopado`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Opciones:** POSITIVO, NEGATIVO, PENDIENTE, N/A

### 8.23 Motivo por el que no se tomaron 3 muestras

- **ID:** `motivo_no_3_muestras`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Validacion:** Maximo 500 caracteres

### 8.24 Resultados Detallados por Muestra (Formato 2026)

- **ID:** `lab_muestras_json`
- **Tipo:** lab_matrix (componente especial)
- **Obligatorio:** No
- **Destino:** I G P
- **Condicion:** Visible si `recolecto_muestra` = "SI"
- **Nota:** Matriz interactiva donde se registra cada muestra individual con tipo, fecha, resultado. Formato JSON almacenado en BD.

### 8.25 Resultado de Secuenciacion

- **ID:** `secuenciacion_resultado`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G P
- **Validacion:** Maximo 200 caracteres
- **GoData:** `sequence[resultId]` en lab-result
- **Nota:** Genotipo o resultado de secuenciacion genomica.

### 8.26 Fecha de Secuenciacion

- **ID:** `secuenciacion_fecha`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** G P
- **Validacion:** No puede ser fecha futura
- **GoData:** `sequence[dateResult]` en lab-result

---

## Tab 9: Clasificacion y Datos IGSS

### 9.1 No. de Contactos Directos

- **ID:** `contactos_directos`
- **Tipo:** Number
- **Obligatorio:** No
- **Destino:** I P
- **Validacion:** 0--999

### 9.2 Clasificacion del Caso

- **ID:** `clasificacion_caso`
- **Tipo:** Select
- **Obligatorio:** Si
- **Destino:** G E P
- **Opciones y mapeo GoData:**

| # | Opcion formulario | GoData `clasificacion` | GoData `clasificacion_final` | Notas |
|---|------------------|----------------------|------------------------------|-------|
| 1 | SOSPECHOSO | "2" (Pendiente) | -- | No se envia clasificacion_final |
| 2 | CONFIRMADO SARAMPION | "CLASIFICADO" | "1" | Activa `criterio_de_confirmacion_sarampion` |
| 3 | CONFIRMADO RUBEOLA | "CLASIFICADO" | "2" | Activa `criterio_de_confirmacion_rubeola` |
| 4 | DESCARTADO | "CLASIFICADO" | "3" | Activa `criterio_para_descartar_el_caso` |
| 5 | PENDIENTE | "2" (Pendiente) | -- | |
| 6 | NO CUMPLE DEFINICION | "CLASIFICADO" | "5" | |
| 7 | CLINICO | -- | -- | Solo IGSS. No se envia a GoData |
| 8 | FALSO | -- | -- | Solo IGSS |
| 9 | ERROR DIAGNOSTICO | -- | -- | Solo IGSS |
| 10 | SUSPENDIDO | -- | -- | Solo IGSS |

- **GoData:** Estructura de 2 niveles: `clasificacion` (CLASIFICADO / "2" Pendiente) + `clasificacion_final` (1/2/3/5)
- **Nota:** Opciones 7--10 son exclusivas IGSS para gestion interna y no se sincronican a GoData.

### 9.3 Criterio de Confirmacion

- **ID:** `criterio_confirmacion`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `clasificacion_caso` = "CONFIRMADO SARAMPION" o "CONFIRMADO RUBEOLA"
- **Opciones y mapeo GoData:**

| Opcion | GoData (Sarampion) | GoData (Rubeola) |
|--------|-------------------|------------------|
| Laboratorio | LABSR | LABRB |
| Nexo Epidemiologico | NE | NERB |
| Clinico | CX | CXRB |

- **GoData:** `criterio_de_confirmacion_sarampion` o `criterio_de_confirmacion_rubeola` segun clasificacion

### 9.4 Criterio de Descarte

- **ID:** `criterio_descarte`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `clasificacion_caso` = "DESCARTADO"
- **Opciones y mapeo GoData:**

| # | Opcion formulario | GoData valor |
|---|------------------|-------------|
| 1 | Laboratorial | LAB |
| 2 | Reaccion Vacunal | RVAC |
| 3 | Dengue | OTRO + especifique "Dengue" |
| 4 | Parvovirus B19 | OTRO + especifique "Parvovirus B19" |
| 5 | Herpes 6 | OTRO + especifique "Herpes 6" |
| 6 | Reaccion Alergica | OTRO + especifique "Reaccion Alergica" |
| 7 | Otro Diagnostico | OTRO + especifique (texto libre) |
| 8 | Clinico | CX2 |

- **GoData:** `criterio_para_descartar_el_caso` (SINGLE_ANSWER: LAB, RVAC, CX2, OTRO -> `especifiqueX` TEXT)
- **Nota:** GoData solo tiene 4 opciones. Las opciones 3--7 del formulario se agrupan en OTRO con texto especifico.

### 9.5 Fuente de Infeccion

- **ID:** `fuente_infeccion`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `clasificacion_caso` = "CONFIRMADO SARAMPION" o "CONFIRMADO RUBEOLA"
- **Opciones:**

| # | Opcion | GoData valor | Sub-campo |
|---|--------|-------------|-----------|
| 1 | Importado | "1" | `importado_pais_de_importacion` (TEXT) |
| 2 | Relacionado con la importacion | "2" | `pais_de_importacion` (TEXT) |
| 3 | Endemico | "3" | -- |
| 4 | Fuente desconocida | "4" | -- |

- **GoData:** `fuente_de_infeccion_de_los_casos_confirmados` (SINGLE_ANSWER: "1", "2", "3", "4")

### 9.6 Pais de Importacion

- **ID:** `pais_importacion`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `fuente_infeccion` = "Importado"
- **Validacion:** Maximo 60 caracteres
- **GoData:** `importado_pais_de_importacion` (si fuente = "1") o `pais_de_importacion` (si fuente = "2")

### 9.7 Contacto con otro caso confirmado?

- **ID:** `contacto_otro_caso`
- **Tipo:** Radio
- **Obligatorio:** No
- **Destino:** G P
- **Opciones:** SI, NO
- **GoData:** `contacto_de_otro_caso` (SINGLE_ANSWER: SI, NO)

### 9.8 Detalle del contacto

- **ID:** `contacto_otro_caso_detalle`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `contacto_otro_caso` = "SI"
- **Validacion:** Maximo 300 caracteres

### 9.9 Caso Analizado por **(MOD)**

- **ID:** `caso_analizado_por`
- **Tipo:** Select (single) -> **Propuesta: cambiar a multi-select para alinear con GoData**
- **Obligatorio:** No
- **Destino:** G P
- **Opciones:**

| # | Opcion | GoData valor |
|---|--------|-------------|
| 1 | CONAPI | "1" |
| 2 | DEGR | "2" |
| 3 | Comision Nacional | "3" |
| 4 | Otros | "4" (activa `especifique_otro_clasificacion`) |

- **GoData:** `caso_analizado_por` (MULTI_ANSWER: "1", "2", "3", "4")
- **Nota:** GoData permite seleccionar multiples. React actualmente es single-select.

### 9.10 Especifique quien analizo

- **ID:** `caso_analizado_por_otro`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `caso_analizado_por` = "Otros"
- **Validacion:** Maximo 150 caracteres
- **GoData:** `especifique_otro_clasificacion` (TEXT)

### 9.11 Fecha de Clasificacion Final

- **ID:** `fecha_clasificacion_final`
- **Tipo:** Date
- **Obligatorio:** No
- **Destino:** G P
- **Validacion:** No puede ser fecha futura
- **GoData:** `fecha_de_clasificacion` (TIME)

### 9.12 Responsable de Clasificacion

- **ID:** `responsable_clasificacion`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I P

### 9.13 Condicion Final del Paciente

- **ID:** `condicion_final_paciente`
- **Tipo:** Select
- **Obligatorio:** No
- **Destino:** G P
- **Opciones:**

| # | Opcion | GoData valor |
|---|--------|-------------|
| 1 | Recuperado | "1" |
| 2 | Con Secuelas | "2" |
| 3 | Fallecido | "3" (activa fecha_defuncion + causa_muerte) |
| 4 | Desconocido | "4" |

- **GoData:** `condicion_final_del_paciente` (SINGLE_ANSWER: "1", "2", "3", "4")

### 9.14 Causa de Muerte en Certificado

- **ID:** `causa_muerte_certificado`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** G P
- **Condicion:** Visible si `condicion_final_paciente` = "Fallecido"
- **Validacion:** Maximo 300 caracteres
- **GoData:** `causa_de_muerte_segun_certificado_de_defuncion` (TEXT, sub-pregunta de condicion = "3")

### 9.15 Observaciones

- **ID:** `observaciones`
- **Tipo:** Textarea
- **Obligatorio:** No
- **Destino:** I P
- **Validacion:** Maximo 1000 caracteres

### 9.16 Es empleado del Seguro Social?

- **ID:** `es_empleado_igss`
- **Tipo:** Radio
- **Obligatorio:** Si
- **Destino:** I P
- **Opciones:** SI, NO
- **Nota:** Inicia la seccion "Datos IGSS" para rastreo ocupacional.

### 9.17 Unidad Medica en la que Trabaja

- **ID:** `unidad_medica_trabaja`
- **Tipo:** Select (con busqueda)
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `es_empleado_igss` = "SI"
- **Opciones:** Misma lista de unidades medicas IGSS

### 9.18 Puesto que Desempena

- **ID:** `puesto_desempena`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I P
- **Condicion:** Visible si `es_empleado_igss` = "SI"

### 9.19 Subgerencia IGSS

- **ID:** `subgerencia_igss`
- **Tipo:** Select (con busqueda, cascading)
- **Obligatorio:** No
- **Destino:** I
- **Condicion:** Visible si `es_empleado_igss` = "SI"
- **Opciones:** 8 subgerencias IGSS + OTRA (importado de `igssOrganizacion.js`)

### 9.20 Especifique Subgerencia

- **ID:** `subgerencia_igss_otra`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I
- **Condicion:** Visible si `subgerencia_igss` = "OTRA"

### 9.21 Direccion IGSS

- **ID:** `direccion_igss`
- **Tipo:** Select (cascading desde subgerencia)
- **Obligatorio:** No
- **Destino:** I
- **Condicion:** Visible si `es_empleado_igss` = "SI"
- **Opciones:** Se cargan dinamicamente segun subgerencia seleccionada

### 9.22 Especifique Direccion

- **ID:** `direccion_igss_otra`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I
- **Condicion:** Visible si `direccion_igss` = "OTRA"

### 9.23 Departamento IGSS

- **ID:** `departamento_igss`
- **Tipo:** Select (cascading)
- **Obligatorio:** No
- **Destino:** I
- **Condicion:** Visible si `es_empleado_igss` = "SI"

### 9.24 Especifique Departamento

- **ID:** `departamento_igss_otro`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I
- **Condicion:** Visible si `departamento_igss` = "OTRO"

### 9.25 Seccion IGSS

- **ID:** `seccion_igss`
- **Tipo:** Select (cascading)
- **Obligatorio:** No
- **Destino:** I
- **Condicion:** Visible si `es_empleado_igss` = "SI"

### 9.26 Especifique Seccion

- **ID:** `seccion_igss_otra`
- **Tipo:** Text
- **Obligatorio:** No
- **Destino:** I
- **Condicion:** Visible si `seccion_igss` = "OTRA"

---

## Campos Inferidos Automaticamente (No visibles, calculados al enviar)

### Area de Salud MSPAS (DDRISS) **(NUEVO)**

- **ID propuesto:** `area_salud_mspas`
- **Tipo:** Inferido automaticamente
- **Destino:** G P
- **Formula:** Se deduce de `departamento_residencia` segun la tabla:

| Departamento | DDRISS (Area de Salud) |
|-------------|----------------------|
| ALTA VERAPAZ | ALTA VERAPAZ |
| BAJA VERAPAZ | BAJA VERAPAZ |
| CHIMALTENANGO | CHIMALTENANGO |
| CHIQUIMULA | CHIQUIMULA |
| EL PROGRESO | EL PROGRESO |
| ESCUINTLA | ESCUINTLA |
| GUATEMALA | GUATEMALA CENTRAL (default) |
| HUEHUETENANGO | HUEHUETENANGO |
| IZABAL | IZABAL |
| JALAPA | JALAPA |
| JUTIAPA | JUTIAPA |
| PETEN | PETEN NORTE (default) |
| QUETZALTENANGO | QUETZALTENANGO |
| QUICHE | QUICHE |
| RETALHULEU | RETALHULEU |
| SACATEPEQUEZ | SACATEPEQUEZ |
| SAN MARCOS | SAN MARCOS |
| SANTA ROSA | SANTA ROSA |
| SOLOLA | SOLOLA |
| SUCHITEPEQUEZ | SUCHITEPEQUEZ |
| TOTONICAPAN | TOTONICAPAN |
| ZACAPA | ZACAPA |

- **GoData:** `direccion_de_area_de_salud` (SINGLE_ANSWER, 29 opciones)
- **Nota:** Guatemala se subdivide en 4 DDRISS (Central, Nor Occidente, Nor Oriente, Sur) y Peten en 3 (Norte, Sur Occidente, Sur Oriente) + Ixcan e Ixil son areas separadas. Para el IGSS, que no tiene estructura DAS propia, se infiere la DDRISS principal del departamento. Si se requiere precision mayor (ej: Guatemala Nor Oriente vs Sur), se puede agregar un campo manual.

### Distrito Municipal de Salud (DMS) **(NUEVO)**

- **ID propuesto:** `distrito_salud_mspas`
- **Tipo:** Inferido automaticamente
- **Destino:** G P
- **Formula:** Se deduce de `municipio_residencia` usando catalogo de DMS por DDRISS de GoData
- **GoData:** `distrito_municipal_de_salud_dms*` (variable suffixed por area; SINGLE_ANSWER con distritos per area)
- **Nota:** Cada DDRISS tiene su propio conjunto de DMS en GoData (variable names distintas). El mapeo automatico usa el municipio para buscar en la tabla de DMS del area correspondiente.

### Servicio de Salud **(NUEVO)**

- **ID propuesto:** `servicio_salud_mspas`
- **Tipo:** Hardcodeado
- **Valor:** = nombre de la unidad medica IGSS seleccionada
- **Destino:** G
- **GoData:** `servicio_de_salud*` (TEXT, sub-pregunta por DDRISS)

### Extranjero **(NUEVO)**

- **ID propuesto:** `es_extranjero`
- **Tipo:** Inferido
- **Formula:** "SI" si `pais_residencia` != "GUATEMALA", "NO" si `pais_residencia` = "GUATEMALA"
- **Destino:** G P
- **GoData:** `extranjero_` (SINGLE_ANSWER: SI, NO)

### Sintomas Gate **(NUEVO)**

- **Tipo:** Inferido
- **Formula:** "SI" si cualquier `signo_*` = "SI", "NO" si todos son "NO"
- **Destino:** G
- **GoData:** `sintomas_` (SINGLE_ANSWER: SI, NO) -- gate antes de `que_sintomas_`

### Acciones de Respuesta Gate **(NUEVO)**

- **Tipo:** Inferido
- **Formula:** "SI" si `bai_realizada` = "SI" o `vitamina_a_administrada` = "SI", "NO" en caso contrario
- **Destino:** G
- **GoData:** `acciones_de_respuesta` (SINGLE_ANSWER: SI, NO)

### Clasificacion Gate **(NUEVO)**

- **Tipo:** Inferido
- **Formula:** "CLASIFICADO" si `clasificacion_caso` es CONFIRMADO/DESCARTADO/NO CUMPLE DEFINICION, "2" si es SOSPECHOSO/PENDIENTE
- **Destino:** G
- **GoData:** `clasificacion` (SINGLE_ANSWER: CLASIFICADO, "2")

---

## Campos Auto-generados al Envio

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `registro_id` | UUID | Identificador unico del registro |
| `timestamp_envio` | ISO datetime | Fecha y hora del envio |
| `nombre_apellido` | Computed | `nombres` + " " + `apellidos` |

---

## Seccion GoData: Lugares Visitados y Rutas de Desplazamiento **(NUEVO)**

Esta seccion existe en GoData y en la ficha PDF MSPAS pero NO existe en el formulario React actual. Es la discrepancia mas grande identificada.

### Estructura en GoData

- **Variable gate:** `lugares_visitados_y_rutas_de_desplazamiento_del_caso`
  - Opciones: "1" (Se Investigo), "2" (No se Investigo), "DESCONOCIDO"
- **Slot 1:** (si gate = "1")
  - `sitio_ruta_de_desplazamiento_1` (TEXT)
  - `direccion_del_lugar_y_rutas_de_desplazamiento_1` (TEXT)
  - `fecha_en_que_visito_el_lugar_ruta_1` (DATE)
  - `tipo_de_abordaje_realizado_1` (MULTI_ANSWER: BLOQUEO, BARRIDO, "3" = BAC, "4" = BAI)
  - `fecha_de_abordaje_1` (DATE)
- **Slot 2:** (identico al Slot 1 con suffixes `_2`)

### Propuesta para formulario IGSS

Como el IGSS no realiza investigacion de campo (rutas, abordajes), esta seccion se puede:
- **Opcion A:** Agregar como seccion oculta que se llena automaticamente como "DESCONOCIDO" al sincronizar con GoData
- **Opcion B:** Agregar como seccion opcional visible en Tab 7 (Acciones de Respuesta) para los casos donde el MSPAS comparta informacion

**Decision pendiente del usuario.**

---

## Resumen de Cambios Propuestos

### Modificaciones a campos existentes (MOD)

| Campo | Cambio |
|-------|--------|
| `diagnostico_sospecha` | Evaluar cambiar de checkbox (multi) a single-select + sub-pregunta |
| `fuente_notificacion` | Eliminar "Privada" y "Defuncion"; alinear textos con GoData |
| `pueblo_etnia` | Cambiar "Ladino / Mestizo" a "Ladino" |
| `comunidad_linguistica` | Cambiar de text libre a select con 23 comunidades mayas |
| `pais_residencia` | Cambiar de text a select GUATEMALA/OTRO |
| `viaje_pais` | Cambiar de text a select GUATEMALA/OTRO |
| `viaje_departamento` | Cambiar de text a select (22 departamentos) |
| `fuente_posible_contagio` | Evaluar cambiar de single a multi-select |
| `caso_analizado_por` | Evaluar cambiar de single a multi-select |

### Campos nuevos (NUEVO)

| Campo | Tipo | Destino |
|-------|------|---------|
| `es_extranjero` | Inferido de pais_residencia | G P |
| `area_salud_mspas` | Inferido de departamento_residencia | G P |
| `distrito_salud_mspas` | Inferido de municipio_residencia | G P |
| `servicio_salud_mspas` | Hardcodeado = unidad medica | G |
| Gates GoData (sintomas, acciones, clasificacion) | Inferidos | G |
| Seccion "Lugares Visitados" (decision pendiente) | 12 sub-campos | G P |

### Campos ocultos (se mantienen en BD)

| Campo | Razon |
|-------|-------|
| `es_seguro_social` | Hardcodeado SI |
| `establecimiento_privado` | Hardcodeado NO |
| `establecimiento_privado_nombre` | Hardcodeado vacio |
| `tipo_vacuna` (legacy) | Compatibilidad retroactiva |
| `numero_dosis_spr` (legacy) | Compatibilidad retroactiva |
| `fecha_ultima_dosis` (legacy) | Compatibilidad retroactiva |
| `observaciones_vacuna` (legacy) | Compatibilidad retroactiva |
| `destino_viaje` (legacy) | Compatibilidad EPIWEB |
| `bac_realizada` | IGSS no hace BAC; se envia "NO" a GoData |
| `bac_casos_sospechosos` | Dependiente de BAC |
| `vacunacion_bloqueo` | IGSS no hace; se envia "NO" a GoData |
| `monitoreo_rapido_vacunacion` | IGSS no hace; se envia "NO" a GoData |
| `vacunacion_barrido` | IGSS no hace; se envia "NO" a GoData |

### Campos eliminados de opciones

| Cambio | Detalle |
|--------|---------|
| Fuente notificacion: "Privada" | No existe en PDF ni GoData |
| Fuente notificacion: "Defuncion" | No existe en PDF ni GoData |

---

## Referencia: Variables GoData (Top-Level)

Las 9 variables top-level del cuestionario GoData del outbreak "Taller Sarampion":

| # | Variable GoData | Tipo | Seccion |
|---|----------------|------|---------|
| 1 | `diagnostico_de_sospecha_` | SINGLE_ANSWER | Diagnostico |
| 2 | `fecha_de_notificacion` | SINGLE_ANSWER (gate) | Unidad Notificadora |
| 3 | `informacion_del_paciente` | SINGLE_ANSWER (gate) | Paciente |
| 4 | `antecedentes_medicos_y_de_vacunacion` | SINGLE_ANSWER (gate) | Antecedentes |
| 5 | `datos_clinicos` | SINGLE_ANSWER (gate) | Datos Clinicos |
| 6 | `factores_de_riesgo` | SINGLE_ANSWER (gate) | Factores Riesgo |
| 7 | `acciones_de_respuesta` | SINGLE_ANSWER (gate) | Acciones |
| 8 | `clasificacion` | SINGLE_ANSWER | Clasificacion |
| 9 | `lugares_visitados_y_rutas_de_desplazamiento_del_caso` | SINGLE_ANSWER | Rutas |

Cada variable "gate" tiene sub-preguntas anidadas que contienen los campos reales. El mapeo desde el formulario React debe construir la estructura anidada correcta para el API de GoData.

---

## Referencia: GoData DDRISS (29 Areas de Salud)

| # | Area de Salud (DDRISS) | Departamento(s) |
|---|----------------------|-----------------|
| 1 | ALTA VERAPAZ | Alta Verapaz |
| 2 | BAJA VERAPAZ | Baja Verapaz |
| 3 | CHIMALTENANGO | Chimaltenango |
| 4 | CHIQUIMULA | Chiquimula |
| 5 | EL PROGRESO | El Progreso |
| 6 | ESCUINTLA | Escuintla |
| 7 | GUATEMALA CENTRAL | Guatemala (zonas centrales) |
| 8 | GUATEMALA NOR OCCIDENTE | Guatemala (Mixco, San Juan Sacatepequez...) |
| 9 | GUATEMALA NOR ORIENTE | Guatemala (Chinautla, Palencia...) |
| 10 | GUATEMALA SUR | Guatemala (Villa Nueva, Amatitlan...) |
| 11 | HUEHUETENANGO | Huehuetenango |
| 12 | IXCAN | Quiche (Ixcan) |
| 13 | IXIL | Quiche (Nebaj, Chajul, Cotzal) |
| 14 | IZABAL | Izabal |
| 15 | JALAPA | Jalapa |
| 16 | JUTIAPA | Jutiapa |
| 17 | PETEN NORTE | Peten (Flores, San Benito...) |
| 18 | PETEN SUR OCCIDENTE | Peten (La Libertad, Sayaxche...) |
| 19 | PETEN SUR ORIENTE | Peten (Poptun, San Luis...) |
| 20 | QUETZALTENANGO | Quetzaltenango |
| 21 | QUICHE | Quiche (excepto Ixcan e Ixil) |
| 22 | RETALHULEU | Retalhuleu |
| 23 | SACATEPEQUEZ | Sacatepequez |
| 24 | SAN MARCOS | San Marcos |
| 25 | SANTA ROSA | Santa Rosa |
| 26 | SOLOLA | Solola |
| 27 | SUCHITEPEQUEZ | Suchitepequez |
| 28 | TOTONICAPAN | Totonicapan |
| 29 | ZACAPA | Zacapa |

---

*Fin del documento. Cualquier campo no listado aqui NO existe en el formulario.*
