# Matriz de Campos Obligatorios vs Opcionales — Vigilancia Sarampion/Rubeola

**Fecha de analisis:** 2026-03-26
**Sistemas comparados:** Formulario IGSS, GoData Guatemala, MSPAS EPIWEB, Ficha MSPAS 2026 (PDF)

---

## Seccion 1: Resumen Ejecutivo

| Metrica | Cantidad |
|---------|----------|
| **Total de campos unicos (no hidden/legacy)** | 112 |
| Requeridos en TODOS los sistemas (Universal) | 14 |
| Requeridos solo en GoData (campos estandar) | 3 |
| Requeridos solo en EPIWEB (no en GoData) | 8 |
| Requeridos solo en nuestro formulario IGSS | 12 |
| Opcionales en todos los sistemas | 55 |
| Exclusivos IGSS (no existen en GoData/MSPAS) | 20 |

### Hallazgos clave

1. **GoData es el menos exigente** en el cuestionario de investigacion: solo 5 campos del template son REQUIRED (fecha_notificacion, DAS, DMS, municipios, fecha_exantema, vacunado). Sin embargo, los **campos estandar** (firstName, lastName, gender, dateOfOnset, dateOfReporting, visualId) son obligatorios a nivel de plataforma.

2. **MSPAS EPIWEB es el mas exigente**: requiere 32+ campos para aceptar el formulario, incluyendo signos/sintomas como radio buttons que deben estar en SI o NO (no pueden quedar en blanco), vacunacion, hospitalizacion, y factores de riesgo.

3. **Nuestro formulario IGSS requiere 38 campos**, de los cuales 12 son requeridos solo por nosotros (no por GoData ni EPIWEB). Varios de estos son justificables para calidad de datos epidemiologicos.

4. **20 campos son exclusivos IGSS** (no existen en GoData ni MSPAS): afiliacion, datos de empleado IGSS, organigrama IGSS, resultados detallados de lab IGSS, y campos formato 2026.

---

## Seccion 2: Tabla Completa por Seccion del Formulario

**Leyenda:**
- **REQ** = Requerido
- **OPC** = Opcional
- **N/A** = No existe en ese sistema
- **COND** = Requerido condicionalmente (ej: si hospitalizado=SI)
- **AUTO** = Se calcula automaticamente

### Tab 1: Datos Generales

| Campo (id) | Label | IGSS Form | GoData | MSPAS EPIWEB | Recomendacion |
|-------------|-------|-----------|--------|-------------|---------------|
| diagnostico_registrado | Diagnostico CIE-10 | REQ | N/A | N/A | REQ (interno IGSS) |
| diagnostico_sospecha | Dx de Sospecha | REQ | OPC (diagnostico_de_sospecha_) | N/A | REQ (util para triaje) |
| unidad_medica | Unidad Medica que Reporta | REQ | N/A (usa DAS/DMS) | REQ (cbox_centroP) | REQ |
| fecha_notificacion | Fecha de Notificacion | REQ | REQ (fecha_de_notificacion) | REQ (fecha_not) | REQ |
| fecha_registro_diagnostico | Fecha Registro Dx | REQ | N/A | N/A | OPC (solo IGSS interno) |
| semana_epidemiologica | Semana Epi | REQ | N/A (auto) | AUTO (semana_epi) | AUTO (derivable) |
| servicio_reporta | Servicio que Reporta | REQ | OPC (servicio_de_salud) | N/A | OPC (reducir carga) |
| nom_responsable | Responsable | REQ | OPC (nombre_de_quien_investiga) | REQ | REQ |
| cargo_responsable | Cargo | REQ | OPC (cargo_de_quien_investiga) | REQ | REQ |
| telefono_responsable | Telefono | OPC | OPC (telefono) | OPC | OPC |
| correo_responsable | Correo | OPC | OPC (correo_electronico) | N/A | OPC |
| envio_ficha | Enviaron Ficha? | REQ | N/A | N/A | OPC (solo tracking IGSS) |
| fuente_notificacion | Fuente Notificacion | REQ | OPC (fuente_de_notificacion_) | REQ (cb_fuente_noti) | REQ |
| fecha_visita_domiciliaria | Visita Domiciliaria | OPC | OPC (fecha_de_investigacion_domiciliaria) | OPC | OPC |
| fecha_inicio_investigacion | Inicio Investigacion | OPC | N/A | OPC (fecha_investigacion) | OPC |
| busqueda_activa | Busqueda Activa | OPC | N/A | OPC (slc_activa) | OPC |
| N/A (DAS) | Dir. Area de Salud | N/A | REQ (direccion_de_area_de_salud) | N/A | **AGREGAR como OPC** |
| N/A (DMS) | Distrito Mun. Salud | N/A | REQ (distrito_municipal_de_salud_dms) | N/A | **AGREGAR como OPC** |

### Tab 2: Datos del Paciente

| Campo (id) | Label | IGSS Form | GoData | MSPAS EPIWEB | Recomendacion |
|-------------|-------|-----------|--------|-------------|---------------|
| afiliacion | No. Afiliacion | REQ | N/A | N/A | REQ (ID unico IGSS) |
| tipo_identificacion | Tipo ID | OPC | OPC (codigo_unico_de_identificacion) | N/A | OPC |
| numero_identificacion | No. ID (DPI/Pasaporte) | OPC | OPC (no_de_dpi / no_de_pasaporte) | N/A | OPC |
| nombres | Nombres | REQ | REQ (firstName — campo estandar) | REQ | REQ |
| apellidos | Apellidos | REQ | REQ (lastName — campo estandar) | REQ | REQ |
| sexo | Sexo | REQ | REQ (gender — campo estandar) | REQ | REQ |
| fecha_nacimiento | Fecha Nacimiento | REQ | OPC (ageDob — campo estandar) | REQ (fecha_nac) | REQ |
| edad_anios | Edad Anos | AUTO | AUTO | AUTO | AUTO |
| edad_meses | Edad Meses | AUTO | N/A | AUTO | AUTO |
| edad_dias | Edad Dias | AUTO | N/A | AUTO | AUTO |
| pueblo_etnia | Pueblo/Etnia | REQ | OPC (pueblo) | REQ (cbox_etnia) | REQ (EPIWEB lo necesita) |
| comunidad_linguistica | Com. Linguistica | OPC | OPC (comunidad_linguistica) | N/A | OPC |
| es_migrante | Migrante? | OPC | OPC (migrante) | N/A | OPC |
| ocupacion | Ocupacion | REQ | OPC (ocupacion_) | REQ (cbox_ocup) | REQ (EPIWEB lo necesita) |
| escolaridad | Escolaridad | REQ | OPC (escolaridad_) | REQ (cbox_escolar) | REQ (EPIWEB lo necesita) |
| pais_residencia | Pais Residencia | OPC | REQ (pais_de_residencia_) | N/A | REQ (GoData lo necesita) |
| departamento_residencia | Depto. Residencia | REQ | REQ (departamento_de_residencia_) | REQ (cbox_iddep) | REQ |
| municipio_residencia | Municipio Residencia | REQ | REQ (municipio_de_residencia_) | REQ (cbox_idmun) | REQ |
| poblado | Poblado | OPC | OPC (lugar_poblado_) | OPC (cbox_idlp) | OPC |
| direccion_exacta | Direccion | OPC | OPC (direccion_de_residencia_) | OPC (p_dir) | OPC |
| nombre_encargado | Nombre Encargado | REQ | OPC (nombre_del_tutor_) | REQ (nombre_madre) | REQ |
| parentesco_tutor | Parentesco | OPC | OPC (parentesco_) | N/A | OPC |
| tipo_id_tutor | Tipo ID Tutor | OPC | OPC | N/A | OPC |
| numero_id_tutor | No. ID Tutor | OPC | OPC | N/A | OPC |
| telefono_paciente | Tel. Paciente | OPC | OPC (telefono_) | N/A | OPC |
| telefono_encargado | Tel. Encargado | OPC | N/A | N/A | OPC |

### Tab 3: Embarazo (condicional sexo=F)

| Campo (id) | Label | IGSS Form | GoData | MSPAS EPIWEB | Recomendacion |
|-------------|-------|-----------|--------|-------------|---------------|
| esta_embarazada | Embarazada? | COND-REQ | OPC (pregnancyStatus campo estandar) | COND-REQ (rad_embarazada) | COND-REQ |
| lactando | Lactando? | OPC | N/A | OPC (rad_lactando) | OPC |
| semanas_embarazo | Semanas Embarazo | COND-REQ | N/A | OPC (txt_sem_emb) | OPC (reducir; EPIWEB no lo requiere) |
| trimestre_embarazo | Trimestre | AUTO | N/A | N/A | AUTO (derivable) |
| fecha_probable_parto | FPP | OPC | N/A | N/A | OPC |
| vacuna_embarazada | Vacuna en embarazo | OPC | N/A | N/A | OPC |

### Tab 4: Antecedentes y Vacunacion

| Campo (id) | Label | IGSS Form | GoData | MSPAS EPIWEB | Recomendacion |
|-------------|-------|-----------|--------|-------------|---------------|
| vacunado | Vacunado contra Sarampion | REQ | REQ (paciente_vacunado_) | REQ (vacunado) | REQ |
| fuente_info_vacuna | Fuente Info Vacuna | COND-REQ | OPC (fuente_de_la_informacion_) | COND-REQ (cb_fuente) | COND-REQ |
| sector_vacunacion | Sector Vacunacion | OPC | OPC (vacunacion_en_el_sector_) | N/A | OPC |
| dosis_spr | Dosis SPR | OPC | OPC (numero_de_dosis) | N/A (usa no_dosis legacy) | OPC |
| fecha_ultima_spr | Fecha Ultima SPR | OPC | OPC (fecha_de_la_ultima_dosis) | OPC | OPC |
| dosis_sr | Dosis SR | OPC | N/A | N/A | OPC |
| fecha_ultima_sr | Fecha Ultima SR | OPC | N/A | N/A | OPC |
| dosis_sprv | Dosis SPRV | OPC | OPC (numero_de_dosis_) | N/A | OPC |
| fecha_ultima_sprv | Fecha Ultima SPRV | OPC | OPC (fecha_de_la_ultima_dosis_) | N/A | OPC |
| tiene_antecedentes_medicos | Antecedentes Med.? | OPC | OPC (antecedentes_medicos_) | N/A | OPC |
| antecedente_desnutricion | Desnutricion | OPC | N/A | N/A | OPC |
| antecedente_inmunocompromiso | Inmunocompromiso | OPC | N/A | N/A | OPC |
| antecedente_enfermedad_cronica | Enf. Cronica | OPC | N/A | N/A | OPC |

### Tab 5: Datos Clinicos

| Campo (id) | Label | IGSS Form | GoData | MSPAS EPIWEB | Recomendacion |
|-------------|-------|-----------|--------|-------------|---------------|
| fecha_inicio_sintomas | Fecha Inicio Sintomas | REQ | OPC (fecha_de_inicio_de_sintomas_) | REQ (fecha_ini_sint) | REQ |
| fecha_captacion | Fecha Captacion | REQ | OPC (fecha_de_consulta) | REQ (fecha_captacion) | REQ |
| fecha_inicio_erupcion | Fecha Inicio Erupcion | REQ | REQ (fecha_de_inicio_de_exantema_rash_) | REQ (txt_fecha_erupcion) | REQ |
| sitio_inicio_erupcion | Sitio Erupcion | REQ | N/A | REQ (cbox_erupciones) | REQ |
| fecha_inicio_fiebre | Fecha Inicio Fiebre | REQ | OPC (fecha_de_inicio_de_fiebre_) | REQ (txt_fecha_fiebre) | REQ |
| temperatura_celsius | Temperatura | OPC | OPC (temp_c) | OPC | OPC |
| signo_fiebre | Fiebre | REQ | OPC (sintomas_ subcampo) | OPC (radio default) | REQ (mantener para calidad) |
| signo_exantema | Exantema | REQ | OPC | N/A (implicito) | REQ |
| signo_manchas_koplik | Manchas Koplik | REQ | OPC | N/A | OPC (reducir; no critico) |
| signo_tos | Tos | REQ | OPC | OPC (tos radio) | REQ (EPIWEB lo mapea) |
| signo_conjuntivitis | Conjuntivitis | REQ | OPC | OPC (conjuntivitis) | REQ |
| signo_coriza | Coriza | REQ | OPC | OPC (coriza) | REQ |
| signo_adenopatias | Adenopatias | REQ | OPC | OPC (adenopatias) | OPC (reducir) |
| signo_artralgia | Artralgia | REQ | OPC | OPC (artralgia) | OPC (reducir) |
| asintomatico | Asintomatico | REQ | N/A | N/A | OPC (reducir) |
| hospitalizado | Hospitalizado? | REQ | OPC (hospitalizacion_) | REQ (hospitalizacion) | REQ |
| hosp_nombre | Hospital | COND-REQ | OPC (nombre_del_hospital_) | COND-REQ (hosp_nombre) | COND-REQ |
| hosp_fecha | Fecha Hosp. | COND-REQ | OPC (fecha_de_hospitalizacion_) | COND-REQ (hosp_fecha) | COND-REQ |
| no_registro_medico | Registro Medico | COND-REQ | N/A | COND-REQ (hosp_reg_med) | COND-REQ |
| condicion_egreso | Condicion Egreso | OPC | N/A | OPC (cb_egreso_condicion) | OPC |
| fecha_egreso | Fecha Egreso | OPC | N/A | OPC | OPC |
| fecha_defuncion | Fecha Defuncion | COND-REQ | OPC (fecha_de_defuncion) | COND-REQ | COND-REQ |
| motivo_consulta | Motivo Consulta | OPC | N/A | N/A | OPC |
| tiene_complicaciones | Complicaciones? | OPC | OPC (complicaciones_) | N/A | OPC |
| comp_neumonia..comp_ceguera | Detalle complicaciones | OPC | OPC (especifique_complicaciones_) | N/A | OPC |
| aislamiento_respiratorio | Aislamiento? | OPC | OPC (aislamiento_respiratorio) | N/A | OPC |

### Tab 6: Factores de Riesgo

| Campo (id) | Label | IGSS Form | GoData | MSPAS EPIWEB | Recomendacion |
|-------------|-------|-----------|--------|-------------|---------------|
| contacto_sospechoso_7_23 | Contacto 7-23 dias | REQ | OPC (tuvo_contacto_con_un_caso_) | REQ (rad_contacto) | REQ |
| caso_sospechoso_comunidad_3m | Caso en comunidad 3m | REQ | OPC (Existe_caso_en_muni) | REQ (rad_casos) | REQ |
| viajo_7_23_previo | Viajo 7-23 dias | REQ | OPC (viajo_durante_los_7_23_dias) | REQ (rad_viajo) | REQ |
| viaje_pais | Pais Destino | OPC | OPC (pais_departamento_y_municipio) | N/A (usa txt_donde_viajo) | OPC |
| viaje_departamento | Depto. Destino | OPC | OPC (departamento) | N/A | OPC |
| viaje_municipio | Municipio Destino | OPC | OPC (municipio) | N/A | OPC |
| viaje_fecha_salida | Fecha Salida | OPC | OPC (fecha_de_salida_viaje) | N/A | OPC |
| viaje_fecha_entrada | Fecha Regreso | OPC | OPC (fecha_de_entrada_viaje) | N/A | OPC |
| familiar_viajo_exterior | Familiar Viajo? | OPC | OPC (alguna_persona_de_su_casa_) | N/A | OPC |
| contacto_enfermo_catarro | Contacto enfermo? | OPC | N/A | OPC (rad_enfermo) | OPC |
| contacto_embarazada | Contacto embarazada? | OPC | OPC (el_paciente_estuvo_en_contacto_) | OPC (rad_cont_emb) | OPC |
| fuente_posible_contagio | Fuente Contagio | OPC | OPC (fuente_posible_de_contagio1) | N/A | OPC |

### Tab 7: Acciones de Respuesta

| Campo (id) | Label | IGSS Form | GoData | MSPAS EPIWEB | Recomendacion |
|-------------|-------|-----------|--------|-------------|---------------|
| bai_realizada | BAI? | OPC | OPC (se_realizo_busqueda_activa_institucional) | N/A | OPC |
| bai_casos_sospechosos | Casos BAI | OPC | OPC (numero_de_casos_sospechosos_bai) | N/A | OPC |
| bac_realizada | BAC? | OPC | OPC (se_realizo_busqueda_activa_comunitaria) | N/A | OPC |
| bac_casos_sospechosos | Casos BAC | OPC | OPC (numero_de_casos_sospechosos_bac) | N/A | OPC |
| vacunacion_bloqueo | Vacunacion Bloqueo? | OPC | OPC (hubo_vacunacion_de_bloqueo) | N/A | OPC |
| monitoreo_rapido_vacunacion | Monitoreo Rapido? | OPC | OPC (se_realizo_monitoreo_rapido) | N/A | OPC |
| vacunacion_barrido | Vacunacion Barrido? | OPC | OPC (hubo_vacunacion_con_barrido) | N/A | OPC |
| vitamina_a_administrada | Vitamina A? | OPC | OPC (se_le_administro_vitamina_a) | N/A | OPC |
| vitamina_a_dosis | Dosis Vit. A | OPC | OPC (numero_de_dosis_de_vitamina_a) | N/A | OPC |

### Tab 8: Laboratorio

| Campo (id) | Label | IGSS Form | GoData | MSPAS EPIWEB | Recomendacion |
|-------------|-------|-----------|--------|-------------|---------------|
| recolecto_muestra | Recolecto Muestra? | REQ | N/A (lab-results separados) | REQ (pick_muestra) | REQ |
| muestra_suero | Suero? | COND-REQ | N/A (sampleType) | OPC (chk_suero) | COND-OPC (reducir) |
| muestra_suero_fecha | Fecha Suero | COND-REQ | N/A (dateSampleTaken REQ en lab) | OPC (fecha_suero) | COND-OPC |
| muestra_hisopado | Hisopado? | COND-REQ | N/A | OPC (chk_HN) | COND-OPC |
| muestra_hisopado_fecha | Fecha Hisopado | COND-REQ | N/A | OPC | COND-OPC |
| muestra_orina | Orina? | COND-REQ | N/A | OPC (chk_orina) | COND-OPC |
| muestra_orina_fecha | Fecha Orina | COND-REQ | N/A | OPC | COND-OPC |
| antigeno_prueba | Antigeno | COND-REQ | N/A (testedFor) | OPC (slc_antigeno) | COND-OPC |
| resultado_prueba | Resultado | COND-REQ | REQ (result en lab-results) | OPC (slc_resul_lab) | COND-REQ |
| fecha_recepcion_laboratorio | Fecha Recepcion Lab | OPC | OPC (dateSampleDelivered) | OPC | OPC |
| fecha_resultado_laboratorio | Fecha Resultado | OPC | OPC (dateOfResult) | OPC | OPC |
| resultado_igg_cualitativo | IgG Cualitativo | OPC | N/A | N/A | OPC (IGSS interno) |
| resultado_igg_numerico | IgG Numerico | OPC | N/A | N/A | OPC (IGSS interno) |
| resultado_igm_cualitativo | IgM Cualitativo | OPC | N/A | N/A | OPC (IGSS interno) |
| resultado_igm_numerico | IgM Numerico | OPC | N/A | N/A | OPC (IGSS interno) |
| resultado_pcr_orina | RT-PCR Orina | OPC | N/A | N/A | OPC (IGSS interno) |
| resultado_pcr_hisopado | RT-PCR Hisopado | OPC | N/A | N/A | OPC (IGSS interno) |
| lab_muestras_json | Matriz Lab 2026 | OPC | N/A | N/A | OPC (IGSS interno) |
| secuenciacion_resultado | Secuenciacion | OPC | OPC (sequence[resultId]) | N/A | OPC |
| secuenciacion_fecha | Fecha Secuenciacion | OPC | OPC (sequence[dateResult]) | N/A | OPC |

### Tab 9: Clasificacion y Datos IGSS

| Campo (id) | Label | IGSS Form | GoData | MSPAS EPIWEB | Recomendacion |
|-------------|-------|-----------|--------|-------------|---------------|
| contactos_directos | No. Contactos | OPC | N/A | N/A | OPC |
| clasificacion_caso | Clasificacion | REQ | OPC (clasificacion_final) | REQ (slc_clas_final) | REQ |
| criterio_confirmacion | Criterio Confirm. | OPC | OPC (criterio_de_confirmacion_) | OPC (slc_confirmado) | OPC |
| criterio_descarte | Criterio Descarte | OPC | OPC (criterio_para_descartar_) | OPC (slc_crit_desc) | OPC |
| fuente_infeccion | Fuente Infeccion | OPC | OPC (fuente_de_infeccion_) | OPC (slc_fuente_infect) | OPC |
| pais_importacion | Pais Importacion | OPC | OPC (pais_de_importacion) | OPC (slc_pais_origen) | OPC |
| contacto_otro_caso | Contacto otro caso? | OPC | OPC (contacto_de_otro_caso) | N/A | OPC |
| caso_analizado_por | Analizado por | OPC | OPC (caso_analizado_por) | N/A | OPC |
| fecha_clasificacion_final | Fecha Clasif. Final | OPC | OPC (fecha_de_clasificacion) | OPC (txt_fecha_final) | OPC |
| responsable_clasificacion | Resp. Clasif. | OPC | N/A | OPC (txt_nom_resp_clas) | OPC |
| condicion_final_paciente | Condicion Final | OPC | OPC (condicion_final_del_paciente) | N/A | OPC |
| observaciones | Observaciones | OPC | N/A | OPC (observaciones_clas) | OPC |
| es_empleado_igss | Empleado IGSS? | REQ | N/A | N/A | REQ (IGSS interno) |
| unidad_medica_trabaja | Unidad donde trabaja | OPC | N/A | N/A | OPC (IGSS interno) |
| puesto_desempena | Puesto | OPC | N/A | N/A | OPC (IGSS interno) |
| subgerencia_igss | Subgerencia | OPC | N/A | N/A | OPC (IGSS interno) |
| direccion_igss | Direccion IGSS | OPC | N/A | N/A | OPC (IGSS interno) |
| departamento_igss | Depto. IGSS | OPC | N/A | N/A | OPC (IGSS interno) |
| seccion_igss | Seccion IGSS | OPC | N/A | N/A | OPC (IGSS interno) |

---

## Seccion 3: Campos IGSS-especificos

Los siguientes campos **solo existen en nuestro formulario** y no tienen equivalente en GoData ni en MSPAS EPIWEB:

### 3.1 Identificacion IGSS
| Campo | Justificacion | Mantener? |
|-------|---------------|-----------|
| afiliacion | Identificador unico del paciente en IGSS, fundamental para deduplicacion y seguimiento | SI, REQ |
| diagnostico_registrado (CIE-10) | Codigo diagnostico del sistema IGSS, no existe en MSPAS/GoData | SI, REQ |
| fecha_registro_diagnostico | Fecha en que se registro el dx en IGSS | Considerar OPC |
| envio_ficha | Tracking interno de si la unidad envio la ficha fisica | Considerar OPC |

### 3.2 Datos de Empleado IGSS
| Campo | Justificacion | Mantener? |
|-------|---------------|-----------|
| es_empleado_igss | Critico para la vigilancia interna (riesgo ocupacional) | SI, REQ |
| unidad_medica_trabaja | Importante si es trabajador de salud expuesto | SI, COND-OPC |
| puesto_desempena | Relevante para riesgo ocupacional | SI, COND-OPC |
| subgerencia_igss | Organigrama IGSS (cascading 4 niveles) | SI, COND-OPC |
| direccion_igss | | SI, COND-OPC |
| departamento_igss | | SI, COND-OPC |
| seccion_igss | | SI, COND-OPC |

### 3.3 Resultados de Laboratorio IGSS
| Campo | Justificacion | Mantener? |
|-------|---------------|-----------|
| resultado_igg_cualitativo | Lab propio IGSS, mas detallado que MSPAS | SI, OPC |
| resultado_igg_numerico | Valor cuantitativo de IgG | SI, OPC |
| resultado_igm_cualitativo | Lab propio IGSS | SI, OPC |
| resultado_igm_numerico | Valor cuantitativo de IgM | SI, OPC |
| resultado_pcr_orina | RT-PCR especifico por tipo de muestra | SI, OPC |
| resultado_pcr_hisopado | RT-PCR especifico por tipo de muestra | SI, OPC |
| lab_muestras_json | Matriz detallada formato 2026 | SI, OPC |

### 3.4 Otros campos exclusivos IGSS
| Campo | Justificacion | Mantener? |
|-------|---------------|-----------|
| motivo_no_3_muestras | Control de calidad del muestreo | SI, OPC |
| secuenciacion_resultado | Genotipificacion | SI, OPC |
| secuenciacion_fecha | | SI, OPC |
| contactos_directos | Conteo de contactos para seguimiento | SI, OPC |

---

## Seccion 4: Campos que el IGSS No Tiene pero GoData/MSPAS Requiere

### 4.1 Campos requeridos en GoData que NO estan en nuestro formulario

| Campo GoData | Tipo | Estado actual IGSS | Brecha |
|-------------|------|-------------------|--------|
| **direccion_de_area_de_salud (DAS)** | Select (29 DAS) | No existe | **BRECHA CRITICA**: GoData lo requiere para asignar el caso al area geografica correcta del MSPAS |
| **distrito_municipal_de_salud (DMS)** | Select cascading | No existe | **BRECHA CRITICA**: Requerido en GoData; cascading por DAS, ~100 DMSs |
| **visualId** | Texto | No existe | GoData genera automaticamente un ID visual (ej: SAR-GT-00001). Se puede auto-generar al sincronizar |
| **dateOfReporting** | Fecha | Parcialmente cubierto por fecha_notificacion | Mapeable directo |
| **dateOfOnset** | Fecha | Cubierto por fecha_inicio_sintomas | Mapeable directo |
| **Lugares visitados y rutas** | Texto (5 sitios) | No existe | GoData tiene seccion de rastreo de movimientos del caso. OPC en GoData pero util |

### 4.2 Campos requeridos en MSPAS EPIWEB que son OPC en nuestro formulario

Estos campos son requeridos por la validacion JavaScript de EPIWEB pero nuestro form los tiene como OPC. Si queremos envio automatico a EPIWEB deben tener valor:

| Campo EPIWEB | name HTML | Estado IGSS | Impacto |
|-------------|-----------|-------------|---------|
| Signos: tos, coriza, conjuntivitis, adenopatias, artralgia | radio SI/NO | OPC en EPIWEB pero tienen default NO | BAJO: El bot puede setear "NO" si vacio |
| Tipo Vacuna (cb_vacuna) | select | Nuestro form usa SPR/SR/SPRV separados, no el campo legacy | BAJO: El field_map ya maneja la conversion |
| No. Dosis (no_dosis) | select | Nuestro form usa dosis_spr/sr/sprv separados | BAJO: El field_map ya maneja la conversion |

---

## Seccion 5: Recomendaciones para Adaptar el Formulario IGSS

### 5.1 Campos a hacer REQUERIDOS (actualmente OPC)

| Campo | Razon | Prioridad |
|-------|-------|-----------|
| pais_residencia | GoData lo requiere; defaultValue='GUATEMALA' ya existe | ALTA |

### 5.2 Campos a hacer OPCIONALES (actualmente REQ)

| Campo | Razon | Ahorro de tiempo |
|-------|-------|------------------|
| servicio_reporta | Ni GoData ni EPIWEB lo requieren | ~5 seg/caso |
| envio_ficha | Solo tracking interno IGSS, no afecta vigilancia | ~3 seg/caso |
| signo_manchas_koplik | Ni GoData ni EPIWEB lo piden; dificil de evaluar clinicamente | ~5 seg/caso |
| signo_adenopatias | Ni GoData ni EPIWEB lo requieren como obligatorio | ~3 seg/caso |
| signo_artralgia | Ni GoData ni EPIWEB lo requieren como obligatorio | ~3 seg/caso |
| asintomatico | Solo existe en nuestro form, redundante si hay signos | ~3 seg/caso |
| semanas_embarazo | EPIWEB no lo requiere (solo lo pide como OPC) | ~5 seg/caso si embarazada |
| fecha_registro_diagnostico | Solo IGSS interno | ~5 seg/caso |
| muestra_suero (como REQ) | EPIWEB usa checkboxes OPC, no radios REQ | ~3 seg/caso |
| muestra_hisopado (como REQ) | Igual | ~3 seg/caso |
| muestra_orina (como REQ) | Igual | ~3 seg/caso |

**Ahorro estimado: ~43 segundos por caso** (basado en tiempo promedio de llenado de un campo simple).

### 5.3 Campos a AGREGAR

| Campo | Destino | Tipo sugerido | Prioridad |
|-------|---------|---------------|-----------|
| das_mspas | GoData (direccion_de_area_de_salud) | Select con 29 DAS del MSPAS | ALTA |
| dms_mspas | GoData (distrito_municipal_de_salud_dms) | Select cascading por DAS | ALTA |
| visual_id_godata | GoData (visualId) | Auto-generado (ej: SAR-IGSS-NNNN) | MEDIA |
| lugares_visitados | GoData (lugares_visitados_y_rutas) | Textarea o tabla dinamica | BAJA |

**Nota sobre DAS/DMS:** El IGSS NO pertenece al sistema de DAS/DMS del MSPAS. Sin embargo, los pacientes residen en areas del MSPAS. Se puede **auto-derivar el DAS del departamento de residencia** (mapeo 1:1 excepto Guatemala que tiene 4 DAS). El DMS se puede inferir del municipio. Esto evitaria que el usuario tenga que llenarlo manualmente.

### 5.4 Campos que se pueden OCULTAR o consolidar

| Accion | Campos | Razon |
|--------|--------|-------|
| Ocultar (ya estan hidden) | tipo_vacuna, numero_dosis_spr, fecha_ultima_dosis, observaciones_vacuna | Legacy; reemplazados por SPR/SR/SPRV detallados |
| Ocultar | destino_viaje | Legacy; reemplazado por viaje_pais/depto/municipio |
| Consolidar en auto-calculo | semana_epidemiologica, trimestre_embarazo, edad_anios/meses/dias | Ya son auto-calculados; confirmar que no requieren input manual |

### 5.5 Oportunidades de Auto-inferencia

| Campo destino | Derivable desde | Logica |
|--------------|-----------------|--------|
| DAS MSPAS | departamento_residencia | Mapeo directo: Guatemala->4 DAS, resto 1:1 |
| DMS MSPAS | municipio_residencia | Mapeo via catalogo MSPAS de municipios->DMS |
| semana_epidemiologica | fecha_notificacion | Ya implementado (autoCalculate: 'epiWeek') |
| edad (anios/meses/dias) | fecha_nacimiento | Ya implementado |
| trimestre_embarazo | semanas_embarazo | Ya implementado |
| codigo_cie10 | diagnostico_registrado | Ya implementado (autoMap) |
| es_seguro_social | (siempre SI) | Ya hardcodeado |
| establecimiento_privado | (siempre NO) | Ya hardcodeado |
| visualId GoData | registro_id + prefijo | Puede auto-generarse: "SAR-IGSS-" + ID secuencial |
| dateOfReporting GoData | fecha_notificacion | Mapeo directo |
| dateOfOnset GoData | fecha_inicio_sintomas | Mapeo directo |

### 5.6 Resumen de Cambios Recomendados

| Tipo de cambio | Cantidad | Impacto |
|---------------|----------|---------|
| Campos a pasar de REQ a OPC | 11 | Reduce friccion de llenado significativamente |
| Campos a agregar | 2-4 | Permite sincronizacion completa con GoData |
| Campos auto-derivables (nuevos) | 3 | DAS, DMS, visualId — sin carga para el usuario |
| Campos a mantener exactamente igual | ~90 | Sin cambios |

### 5.7 Prioridades de Implementacion

**Fase 1 (inmediata):**
- Hacer OPC los 11 campos sobreexigidos
- Agregar auto-derivacion de DAS desde departamento_residencia
- Hacer pais_residencia REQ (defaultValue ya existe)

**Fase 2 (corto plazo):**
- Agregar campo DMS auto-derivado de municipio
- Agregar generacion automatica de visualId para GoData
- Validar que el mapeo IGSS->GoData cubre los 6 campos estandar obligatorios

**Fase 3 (mediano plazo):**
- Agregar seccion de Lugares Visitados/Rutas (5 sitios con fecha+tipo abordaje)
- Consolidar campos legacy definitivamente (remover del schema, mantener en BD)

---

## Anexo A: Campos Estandar GoData (visibleAndMandatoryFields para cases)

Estos son los campos que GoData Guatemala tiene configurados como **mandatory** a nivel de plataforma (no del cuestionario de investigacion):

| Campo GoData | Mandatory | Equivalente IGSS |
|-------------|-----------|-----------------|
| firstName | SI | nombres |
| lastName | SI | apellidos |
| gender | SI | sexo |
| dateOfOnset | SI | fecha_inicio_sintomas |
| dateOfReporting | SI | fecha_notificacion |
| visualId | SI | No existe (auto-generable) |
| middleName | NO | N/A |
| ageDob | NO | fecha_nacimiento |
| pregnancyStatus | NO (visible) | esta_embarazada |

## Anexo B: Campos REQUIRED en el Cuestionario GoData (caseInvestigationTemplate)

Solo los siguientes campos del cuestionario personalizado estan marcados como `required: true`:

| Variable GoData | Concepto |
|----------------|----------|
| fecha_de_notificacion | Fecha de notificacion |
| direccion_de_area_de_salud | DAS (29 opciones) |
| distrito_municipal_de_salud_dms (x26 variantes) | DMS por cada DAS |
| pais_de_residencia_ | Pais de residencia |
| departamento_de_residencia_ | Departamento |
| municipio_de_residencia_ (x22 variantes) | Municipio por cada depto |
| especifique_pais | Pais si es extranjero |
| antecedentes_medicos_y_de_vacunacion | Seccion header |
| paciente_vacunado_ | Si/No vacunado |
| fecha_de_inicio_de_exantema_rash_ | Fecha inicio exantema |

**Nota:** Las variantes multiples de DMS y municipio (dms1, dms2...dms26) son campos condicionales que dependen del DAS seleccionado. En la practica, el usuario solo llena 1 DMS segun el DAS elegido.
