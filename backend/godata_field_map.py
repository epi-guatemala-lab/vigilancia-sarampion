"""
Mapeo de campos: BD unificada → GoData API payload.
Convierte un registro de nuestra BD SQLite al formato esperado por GoData.

GoData Measles/Rubella template tiene 28 questionnaire questions +
campos estándar del modelo Person/Case.

Referencia:
- Go.Data Metadata Overview - Measles (WHO, 2022)
- Template: WorldHealthOrganization/GoDataSource-API measles.json
"""
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CÓDIGOS DE REFERENCIA GODATA
# ═══════════════════════════════════════════════════════════

GENDER_MAP = {
    "M": "LNG_REFERENCE_DATA_CATEGORY_GENDER_MALE",
    "MASCULINO": "LNG_REFERENCE_DATA_CATEGORY_GENDER_MALE",
    "F": "LNG_REFERENCE_DATA_CATEGORY_GENDER_FEMALE",
    "FEMENINO": "LNG_REFERENCE_DATA_CATEGORY_GENDER_FEMALE",
}

CLASSIFICATION_MAP = {
    "SOSPECHOSO": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_SUSPECT",
    "PENDIENTE": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_SUSPECT",
    "CONFIRMADO SARAMPIÓN": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_CONFIRMED",
    "CONFIRMADO SARAMPION": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_CONFIRMED",
    "CONFIRMADO RUBÉOLA": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_CONFIRMED",
    "CONFIRMADO RUBEOLA": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_CONFIRMED",
    "CONFIRMADO": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_CONFIRMED",
    "CLÍNICO": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_PROBABLE",
    "CLINICO": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_PROBABLE",
    "DESCARTADO": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_NOT_A_CASE_DISCARDED",
    "NO CUMPLE DEFINICIÓN": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_NOT_A_CASE_DISCARDED",
    "NO CUMPLE DEFINICION": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_NOT_A_CASE_DISCARDED",
    "FALSO": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_NOT_A_CASE_DISCARDED",
    "ERROR DIAGNÓSTICO": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_NOT_A_CASE_DISCARDED",
    "ERROR DIAGNOSTICO": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_NOT_A_CASE_DISCARDED",
}

OUTCOME_MAP = {
    "RECUPERADO": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_RECOVERED",
    "CON SECUELAS": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_ALIVE",
    "FALLECIDO": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_DECEASED",
    "MEJORADO": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_RECOVERED",
    "MUERTO": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_DECEASED",
}

VACCINE_TYPE_MAP = {
    "SPR": "mmr",
    "SRP": "mmr",
    "SRP Sarampion Rubeola Paperas": "mmr",
    "SR": "mr",
    "SR Sarampion Rubeola": "mr",
    "SPRV": "mmrv",
    "Antisarampinosa": "measles",
    "Antirubéolica": "rubella",
}

VACCINE_DOSE_MAP = {
    "1": "one_dose",
    "1 dosis": "one_dose",
    "2": "two_doses",
    "2 dosis": "two_doses",
    "3": "three_doses",
    "3 dosis": "three_doses",
    "Mas de 3 dosis": "three_doses",
    "No recuerda": "unknown",
}

DOCUMENT_TYPE_MAP = {
    "DPI": "LNG_REFERENCE_DATA_CATEGORY_DOCUMENT_TYPE_NATIONAL_ID_CARD",
    "PASAPORTE": "LNG_REFERENCE_DATA_CATEGORY_DOCUMENT_TYPE_PASSPORT",
    "OTRO": "LNG_REFERENCE_DATA_CATEGORY_DOCUMENT_TYPE_OTHER",
}

SAMPLE_TYPE_MAP = {
    "suero_1": "LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_BLOOD_SERUM",
    "suero_2": "LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_BLOOD_SERUM",
    "orina_1": "LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_URINE",
    "hisopado_1": "LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_NASOPHARYNGEAL_SWAB",
    "otro": "LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_OTHER",
}

LAB_RESULT_MAP = {
    "0": "LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_NEGATIVE",
    "1": "LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_POSITIVE",
    "2": "LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_INADEQUATE",
    "3": "LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_INCONCLUSIVE",
    "4": "LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_UNKNOWN",
    "Negativo": "LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_NEGATIVE",
    "Positivo": "LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_POSITIVE",
    "Muestra Inadecuada": "LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_INADEQUATE",
    "Indeterminada": "LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_INCONCLUSIVE",
}

TEST_TYPE_MAP = {
    "igm": "igm_eia_capture",
    "igg": "igg_eia_capture",
    "pcr": "PCR",
}

DETECTED_BY_MAP = {
    "Servicio de Salud": "Spontaneous consultation",
    "Publica": "Spontaneous consultation",
    "Privada": "Spontaneous consultation",
    "Laboratorio": "Laboratory",
    "Búsqueda Activa Laboratorial": "Laboratory",
    "Comunidad": "Community report",
    "Búsqueda Activa Comunitaria": "Community case search",
    "Búsqueda Activa Institucional": "Institutional search",
    "Investigación de Contactos": "Contact investigation",
    "Defunción": "Spontaneous consultation",
}

SETTING_INFECTED_MAP = {
    "Contacto en el hogar": "Household",
    "Servicio de Salud": "Health center",
    "Comunidad": "Community",
    "Espacio Público": "Community",
    "Desconocido": "Unknown",
    "Otro": "Others",
}

CONFIRMATION_BASIS_MAP = {
    "Laboratorio": "Laboratory",
    "Nexo Epidemiológico": "Epidemiological Link",
    "Nexo epidemiologico": "Epidemiological Link",
    "Diagnóstico Clínico": "Clinical",
    "Clinico": "Clinical",
    "Clínico": "Clinical",
}

DISCARD_BASIS_MAP = {
    "Laboratorial": "IgM-neg",
    "IgM Negativo": "IgM-neg",
    "Reacción Vacunal": "Vaccine reaction",
    "Dengue": "Dengue",
    "Parvovirus B19": "Parvovirus B19",
    "Herpes 6": "Herpes 6",
    "Reacción Alérgica": "Allergic reaction",
    "Otro Diagnóstico": "Other",
    "Clínico": "Other",
}

SOURCE_INFECTION_MAP = {
    "Importado": "Imported",
    "Relacionado con Importación": "Import-Related",
    "Relacionado con la importacion": "Import-Related",
    "Endémico": "Endemic",
    "Endemico": "Endemic",
    "Autóctono": "Endemic",
    "Autoctono": "Endemic",
    "Desconocido": "Unknown",
    "Fuente desconocida": "Unknown",
}

SI_NO_UNKNOWN_MAP = {
    "SI": "YES",
    "NO": "NO",
    "DESCONOCIDO": "UNKNOWN",
    "": "UNKNOWN",
}


# ═══════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════

def _get(d: dict, key: str, default: str = "") -> str:
    """Obtiene valor de dict, normalizado."""
    val = d.get(key)
    if val is None:
        return default
    return str(val).strip()


def _strip_accents(text: str) -> str:
    """Elimina tildes/acentos de texto. GoData requiere texto sin acentos."""
    import unicodedata
    if not text:
        return text
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def _godata_text(text: str) -> str:
    """Normaliza texto para GoData: MAYÚSCULAS sin tildes."""
    if not text:
        return text
    return _strip_accents(text).upper()


def _to_iso_date(date_str: str) -> Optional[str]:
    """Convierte fecha a formato YYYY-MM-DD (GoData)."""
    if not date_str:
        return None
    date_str = date_str.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(date_str[:10] if len(date_str) > 10 else date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _safe_int(val, default=0) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def _si_no_to_godata(val: str) -> str:
    """Convierte SI/NO/DESCONOCIDO a YES/NO/UNKNOWN."""
    return SI_NO_UNKNOWN_MAP.get(str(val).upper().strip(), "UNKNOWN")


# ═══════════════════════════════════════════════════════════
# MAPEO PRINCIPAL: record → GoData case payload
# ═══════════════════════════════════════════════════════════

def map_record_to_godata(record: dict) -> Dict:
    """Convierte un registro de nuestra BD al formato GoData case.

    Returns:
        Dict listo para POST /api/outbreaks/{id}/cases
    """
    d = record

    # ─── Campos base del modelo Person/Case ─────────────
    # GoData requiere: MAYÚSCULAS, sin tildes, fechas YYYY-MM-DD
    case = {
        "firstName": _godata_text(_get(d, "nombres")),
        "lastName": _godata_text(_get(d, "apellidos")),
        "gender": GENDER_MAP.get(_get(d, "sexo").upper(), ""),
        "dob": _to_iso_date(_get(d, "fecha_nacimiento")),
        "age": {
            "years": _safe_int(_get(d, "edad_anios")),
            "months": _safe_int(_get(d, "edad_meses")),
        },
        "occupation": _godata_text(_get(d, "ocupacion")),
        "visualId": _get(d, "registro_id"),
        "dateOfReporting": _to_iso_date(_get(d, "fecha_notificacion")),
        "isDateOfReportingApproximate": False,
        "dateOfOnset": _to_iso_date(_get(d, "fecha_inicio_sintomas")),
    }

    # Clasificación
    clasificacion = _get(d, "clasificacion_caso").upper()
    if clasificacion in CLASSIFICATION_MAP:
        case["classification"] = CLASSIFICATION_MAP[clasificacion]

    # Condición final / Outcome
    condicion = _get(d, "condicion_final_paciente") or _get(d, "condicion_egreso")
    if condicion and condicion.upper() in OUTCOME_MAP:
        case["outcomeId"] = OUTCOME_MAP[condicion.upper()]
        if condicion.upper() in ("FALLECIDO", "MUERTO"):
            case["dateOfOutcome"] = _to_iso_date(_get(d, "fecha_defuncion"))

    # Embarazo
    embarazada = _get(d, "esta_embarazada").upper()
    if embarazada == "SI":
        case["pregnancyStatus"] = "LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_YES_TRIMESTER_UNKNOWN"
        trimestre = _get(d, "trimestre_embarazo")
        if trimestre == "1":
            case["pregnancyStatus"] = "LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_YES_FIRST_TRIMESTER"
        elif trimestre == "2":
            case["pregnancyStatus"] = "LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_YES_SECOND_TRIMESTER"
        elif trimestre == "3":
            case["pregnancyStatus"] = "LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_YES_THIRD_TRIMESTER"
    elif embarazada == "NO":
        case["pregnancyStatus"] = "LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_NOT_PREGNANT"

    # ─── Documentos de identidad ────────────────────────
    documents = []
    tipo_id = _get(d, "tipo_identificacion")
    num_id = _get(d, "numero_identificacion")
    if num_id:
        documents.append({
            "type": DOCUMENT_TYPE_MAP.get(tipo_id.upper(), "LNG_REFERENCE_DATA_CATEGORY_DOCUMENT_TYPE_OTHER"),
            "number": num_id,
        })
    afiliacion = _get(d, "afiliacion")
    if afiliacion:
        documents.append({
            "type": "LNG_REFERENCE_DATA_CATEGORY_DOCUMENT_TYPE_OTHER",
            "number": f"IGSS-{afiliacion}",
        })
    if documents:
        case["documents"] = documents

    # ─── Dirección ──────────────────────────────────────
    address = {
        "typeId": "LNG_REFERENCE_DATA_CATEGORY_ADDRESS_TYPE_USUAL_PLACE_OF_RESIDENCE",
        "country": _godata_text(_get(d, "pais_residencia") or "GUATEMALA"),
        "city": _godata_text(_get(d, "municipio_residencia")),
        "addressLine1": _godata_text(_get(d, "direccion_exacta")),
        "phoneNumber": _get(d, "telefono_paciente") or _get(d, "telefono_encargado"),
    }
    depto = _get(d, "departamento_residencia")
    if depto:
        address["addressLine2"] = _godata_text(depto)
    poblado = _get(d, "poblado")
    if poblado:
        address["addressLine1"] = f"{poblado}, {address.get('addressLine1', '')}"
    case["addresses"] = [address]

    # ─── Vacunas ────────────────────────────────────────
    vaccines = []
    for prefix, vtype in [("spr", "mmr"), ("sr", "mr"), ("sprv", "mmrv")]:
        dosis = _get(d, f"dosis_{prefix}")
        fecha = _get(d, f"fecha_ultima_{prefix}")
        if dosis:
            vaccines.append({
                "vaccine": vtype,
                "date": _to_iso_date(fecha),
                "status": VACCINE_DOSE_MAP.get(dosis, "unknown"),
            })
    # Fallback: campos legacy
    if not vaccines and _get(d, "vacunado").upper() == "SI":
        tipo = _get(d, "tipo_vacuna")
        vtype = VACCINE_TYPE_MAP.get(tipo, "mmr")
        dosis_legacy = _get(d, "numero_dosis_spr")
        vaccines.append({
            "vaccine": vtype,
            "date": _to_iso_date(_get(d, "fecha_ultima_dosis")),
            "status": VACCINE_DOSE_MAP.get(dosis_legacy, "unknown"),
        })
    if vaccines:
        case["vaccinesReceived"] = vaccines

    # ─── Hospitalización ────────────────────────────────
    date_ranges = []
    hosp = _get(d, "hospitalizado").upper()
    if hosp == "SI":
        date_ranges.append({
            "typeId": "LNG_REFERENCE_DATA_CATEGORY_PERSON_DATE_TYPE_HOSPITALIZATION",
            "centerName": _get(d, "hosp_nombre"),
            "startDate": _to_iso_date(_get(d, "hosp_fecha")),
            "endDate": _to_iso_date(_get(d, "fecha_egreso")),
        })
    aislamiento = _get(d, "aislamiento_respiratorio").upper()
    if aislamiento == "SI":
        date_ranges.append({
            "typeId": "LNG_REFERENCE_DATA_CATEGORY_PERSON_DATE_TYPE_ISOLATION",
            "startDate": _to_iso_date(_get(d, "fecha_aislamiento")),
        })
    if date_ranges:
        case["dateRanges"] = date_ranges

    # ─── Questionnaire Answers (28 preguntas measles) ──
    qa = {}

    # Q1: initial_diagnosis
    dx_sospecha = _get(d, "diagnostico_sospecha")
    dx_map = {
        "Sarampión": "MEASLES", "Rubéola": "RUBELLA", "Dengue": "DENGUE",
        "Otra Arbovirosis": "OTHER_NON_RASH", "Otra febril exantemática": "OTHER_RASH",
        "Caso altamente sospechoso": "MEASLES",
    }
    if dx_sospecha and dx_sospecha in dx_map:
        qa["initial_diagnosis"] = [{"value": dx_map[dx_sospecha]}]
    elif _get(d, "diagnostico_registrado").startswith("B05"):
        qa["initial_diagnosis"] = [{"value": "MEASLES"}]
    elif _get(d, "diagnostico_registrado").startswith("B06"):
        qa["initial_diagnosis"] = [{"value": "RUBELLA"}]

    # Q2: provider_type
    if _get(d, "establecimiento_privado").upper() == "SI":
        qa["provider_type"] = [{"value": "Private"}]
    elif _get(d, "es_seguro_social").upper() == "SI" or _get(d, "unidad_medica"):
        qa["provider_type"] = [{"value": "Other"}]
    else:
        qa["provider_type"] = [{"value": "Public"}]

    # Q3: detected_by
    fuente = _get(d, "fuente_notificacion")
    if fuente and fuente in DETECTED_BY_MAP:
        qa["detected_by"] = [{"value": DETECTED_BY_MAP[fuente]}]

    # Q4-Q5: consultation/homevisit dates
    fecha_consulta = _to_iso_date(_get(d, "fecha_registro_diagnostico"))
    if fecha_consulta:
        qa["consultation_date"] = [{"value": fecha_consulta}]
    fecha_visita = _to_iso_date(_get(d, "fecha_visita_domiciliaria"))
    if fecha_visita:
        qa["homevisit_date"] = [{"value": fecha_visita}]

    # Q6: hcs_name
    unidad = _get(d, "unidad_medica") or _get(d, "servicio_salud_mspas")
    if unidad:
        qa["hcs_name"] = [{"value": _godata_text(unidad)}]

    # Q8: locality_type (Urban/Periurban/Rural — no tenemos, skip)

    # Q10: HH_Next_of_kin
    encargado = _get(d, "nombre_encargado")
    if encargado:
        qa["HH_Next_of_kin"] = [{"value": _godata_text(encargado)}]

    # Q11: vaccination_status
    vacunado = _get(d, "vacunado").upper()
    vac_map = {"SI": "YES", "NO": "NO", "DESCONOCIDO": "UNKNOWN", "DESCONOCIDO/VERBAL": "UNKNOWN"}
    if vacunado in vac_map:
        vac_answer = {"value": vac_map[vacunado]}
        fuente_vac = _get(d, "fuente_info_vacuna")
        if fuente_vac:
            fuente_godata_map = {
                "Carné de Vacunación": "Card", "En carne": "Card",
                "SIGSA 5a Cuaderno": "SIGSA", "En SIGSA 5a": "SIGSA",
                "Verbal": "Verbal",
            }
            if fuente_vac in fuente_godata_map:
                vac_answer["vaccination_source"] = [{"value": fuente_godata_map[fuente_vac]}]
        qa["vaccination_status"] = [vac_answer]

    # Q13: signs_and_symptoms
    symptoms_answer = {"value": "UNKNOWN"}
    any_symptom = False
    symptom_fields = [
        ("signo_fiebre", "symp_fever"),
        ("signo_exantema", "symp_rash"),
        ("signo_tos", "symp_cough"),
        ("signo_conjuntivitis", "symp_conjunctivitis"),
        ("signo_coriza", "symp_coryza"),
        ("signo_manchas_koplik", "symp_koplik_spots"),
        ("signo_adenopatias", "symp_lymphadenopathy"),
        ("signo_artralgia", "symp_arthralgia"),
    ]
    for db_field, godata_field in symptom_fields:
        val = _get(d, db_field).upper()
        if not val:
            continue  # Campo vacío: no incluir
        godata_val = _si_no_to_godata(val)
        symptoms_answer[godata_field] = [{"value": godata_val}]
        if godata_val == "YES":
            any_symptom = True

    # Agregar fechas de síntomas como sub-campos
    fever_onset = _to_iso_date(_get(d, "fecha_inicio_fiebre"))
    if fever_onset:
        symptoms_answer["fever_onset"] = [{"value": fever_onset}]
    rash_onset = _to_iso_date(_get(d, "fecha_inicio_erupcion"))
    if rash_onset:
        symptoms_answer["rash_onset"] = [{"value": rash_onset}]
    temp = _get(d, "temperatura_celsius").replace(",", ".")
    if temp:
        symptoms_answer["fever_temp"] = [{"value": temp}]

    if any_symptom:
        symptoms_answer["value"] = "YES"
    elif any(_get(d, f) for f, _ in symptom_fields) and all(_get(d, f).upper() == "NO" for f, _ in symptom_fields if _get(d, f)):
        symptoms_answer["value"] = "NO"
    qa["signs_and_symptoms"] = [symptoms_answer]

    # Q14: Complications (not in standard GoData measles template but useful)
    comps_val = _get(d, "tiene_complicaciones").upper()
    if comps_val == "SI":
        comp_types = []
        comp_map = {
            "comp_neumonia": "Neumonia", "comp_encefalitis": "Encefalitis",
            "comp_diarrea": "Diarrea", "comp_trombocitopenia": "Trombocitopenia",
            "comp_otitis": "Otitis Media", "comp_ceguera": "Ceguera",
        }
        for field, label in comp_map.items():
            if _get(d, field).upper() == "SI":
                comp_types.append(label)
        otra = _get(d, "comp_otra_texto")
        if otra:
            comp_types.append(otra)
        if comp_types:
            qa["complications"] = [{"value": ", ".join(comp_types)}]

    # Q15: active_searches
    bai = _get(d, "bai_realizada").upper()
    bac = _get(d, "bac_realizada").upper()
    if bai == "SI" or bac == "SI":
        search_answer = {"value": "YES"}
        total_sospechosos = _safe_int(_get(d, "bai_casos_sospechosos")) + _safe_int(_get(d, "bac_casos_sospechosos"))
        if total_sospechosos > 0:
            search_answer["suspected_cases_detected"] = [{"value": total_sospechosos}]
        qa["active_searches"] = [search_answer]
    elif bai == "NO" and bac == "NO":
        qa["active_searches"] = [{"value": "NO"}]

    # Q16: contact_pregnant_woman
    contacto_emb = _get(d, "contacto_embarazada").upper()
    if contacto_emb:
        qa["contact_pregnant_woman"] = [{"value": _si_no_to_godata(contacto_emb)}]

    # Q17: additional_cases
    caso_comunidad = _get(d, "caso_sospechoso_comunidad_3m").upper()
    if caso_comunidad:
        qa["additional_cases"] = [{"value": _si_no_to_godata(caso_comunidad)}]

    # Q18: expo_travel
    viajo = _get(d, "viajo_7_23_previo").upper()
    if viajo:
        travel_answer = {"value": _si_no_to_godata(viajo)}
        if viajo == "SI":
            destino_parts = []
            for f in ["viaje_municipio", "viaje_departamento", "viaje_pais"]:
                v = _get(d, f)
                if v:
                    destino_parts.append(v)
            if not destino_parts:
                destino_legacy = _get(d, "destino_viaje")
                if destino_legacy:
                    destino_parts = [destino_legacy]
            if destino_parts:
                travel_answer["city_country"] = [{"value": _godata_text(", ".join(destino_parts))}]
            fecha_salida = _to_iso_date(_get(d, "viaje_fecha_salida"))
            if fecha_salida:
                travel_answer["departure_date"] = [{"value": fecha_salida}]
        qa["expo_travel"] = [travel_answer]

    # Q19: Setting_where_infected
    fuente_contagio = _get(d, "fuente_posible_contagio")
    if fuente_contagio and fuente_contagio in SETTING_INFECTED_MAP:
        qa["Setting_where_infected"] = [{"value": SETTING_INFECTED_MAP[fuente_contagio]}]

    # Q21: ring_vaccination
    vac_bloqueo = _get(d, "vacunacion_bloqueo").upper()
    if vac_bloqueo:
        qa["ring_vaccination"] = [{"value": _si_no_to_godata(vac_bloqueo)}]

    # Q22: rapid_coverage_monitoring
    monitoreo = _get(d, "monitoreo_rapido_vacunacion").upper()
    if monitoreo:
        qa["rapid_coverage_monitoring"] = [{"value": _si_no_to_godata(monitoreo)}]

    # Q23: final_classification
    clas = _get(d, "clasificacion_caso").upper()
    final_clas_map = {
        "CONFIRMADO SARAMPIÓN": "Measles", "CONFIRMADO SARAMPION": "Measles",
        "CONFIRMADO RUBÉOLA": "Rubella", "CONFIRMADO RUBEOLA": "Rubella",
        "DESCARTADO": "Discarded",
    }
    if clas in final_clas_map:
        qa["final_classification"] = [{"value": final_clas_map[clas]}]

    # Q24: basis_for_confirmation
    criterio_conf = _get(d, "criterio_confirmacion")
    if criterio_conf and criterio_conf in CONFIRMATION_BASIS_MAP:
        qa["basis_for_confirmation"] = [{"value": CONFIRMATION_BASIS_MAP[criterio_conf]}]

    # Q25: basis_for_discarding
    criterio_desc = _get(d, "criterio_descarte")
    if criterio_desc and criterio_desc in DISCARD_BASIS_MAP:
        qa["basis_for_discarding"] = [{"value": DISCARD_BASIS_MAP[criterio_desc]}]

    # Q26: source_of_infection
    fuente_inf = _get(d, "fuente_infeccion")
    if fuente_inf and fuente_inf in SOURCE_INFECTION_MAP:
        src_answer = {"value": SOURCE_INFECTION_MAP[fuente_inf]}
        pais_imp = _get(d, "pais_importacion")
        if pais_imp:
            src_answer["country"] = [{"value": _godata_text(pais_imp)}]
        qa["source_of_infection"] = [src_answer]

    # Q27: classified_by
    analizado = _get(d, "caso_analizado_por")
    if analizado:
        qa["classified_by"] = [{"value": _godata_text(analizado)}]

    # Q28: final_classification_date
    fecha_clas = _to_iso_date(_get(d, "fecha_clasificacion_final"))
    if fecha_clas:
        qa["final_classification_date"] = [{"value": fecha_clas}]

    # Causa de muerte
    causa_muerte = _get(d, "causa_muerte_certificado")
    if causa_muerte:
        qa["cause_of_death"] = [{"value": _godata_text(causa_muerte)}]

    case["questionnaireAnswers"] = qa
    return case


# ═══════════════════════════════════════════════════════════
# MAPEO LABORATORIO: lab_muestras_json → GoData lab-results
# ═══════════════════════════════════════════════════════════

def map_lab_samples_to_godata(record: dict) -> List[Dict]:
    """Convierte lab_muestras_json a lista de payloads para GoData lab-results endpoint.

    Cada entrada del JSON puede generar múltiples lab-results (uno por virus/test).

    Returns:
        Lista de dicts listos para POST /api/outbreaks/{id}/cases/{fk}/lab-results
    """
    lab_json_str = _get(record, "lab_muestras_json")
    if not lab_json_str:
        return _map_legacy_lab(record)

    try:
        samples = json.loads(lab_json_str)
    except (json.JSONDecodeError, TypeError):
        logger.warning("lab_muestras_json no es JSON válido")
        return _map_legacy_lab(record)

    if not isinstance(samples, list):
        return _map_legacy_lab(record)

    results = []
    for sample in samples:
        slot = sample.get("slot", "")
        sample_type = SAMPLE_TYPE_MAP.get(slot, "LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_OTHER")
        fecha_toma = _to_iso_date(sample.get("fecha_toma", ""))
        fecha_envio = _to_iso_date(sample.get("fecha_envio", ""))
        fecha_resultado = _to_iso_date(sample.get("fecha_resultado", ""))

        # Generar un result por cada test con resultado
        test_fields = [
            ("sarampion_igm", "igm_eia_capture", "MEASLES"),
            ("sarampion_igg", "igg_eia_capture", "MEASLES"),
            ("rubeola_igm", "igm_eia_capture", "RUBELLA"),
            ("rubeola_igg", "igg_eia_capture", "RUBELLA"),
        ]
        for field, test_type, tested_for in test_fields:
            val = sample.get(field, "")
            if val and val in LAB_RESULT_MAP:
                results.append({
                    "sampleIdentifier": sample.get("numero_muestra", ""),
                    "sampleType": sample_type,
                    "dateSampleTaken": fecha_toma,
                    "dateSampleDelivered": fecha_envio,
                    "testType": test_type,
                    "testedFor": tested_for,
                    "result": LAB_RESULT_MAP[val],
                    "dateOfResult": fecha_resultado,
                })

    return results


def _map_legacy_lab(record: dict) -> List[Dict]:
    """Mapea campos de lab legacy (flat) cuando no hay lab_muestras_json."""
    results = []
    d = record

    if _get(d, "recolecto_muestra").upper() != "SI":
        return results

    antigeno = _get(d, "antigeno_prueba")
    tested_for = "MEASLES" if antigeno == "Sarampion" else "RUBELLA" if antigeno == "Rubeola" else "MEASLES"
    resultado = _get(d, "resultado_prueba")

    if resultado and resultado in LAB_RESULT_MAP:
        # Suero
        if _get(d, "muestra_suero").upper() == "SI":
            results.append({
                "sampleType": "LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_BLOOD_SERUM",
                "dateSampleTaken": _to_iso_date(_get(d, "muestra_suero_fecha")),
                "dateSampleDelivered": _to_iso_date(_get(d, "fecha_recepcion_laboratorio")),
                "testType": "igm_eia_capture",
                "testedFor": tested_for,
                "result": LAB_RESULT_MAP[resultado],
                "dateOfResult": _to_iso_date(_get(d, "fecha_resultado_laboratorio")),
            })

        # Hisopado
        if _get(d, "muestra_hisopado").upper() == "SI":
            results.append({
                "sampleType": "LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_NASOPHARYNGEAL_SWAB",
                "dateSampleTaken": _to_iso_date(_get(d, "muestra_hisopado_fecha")),
                "testType": "PCR",
                "testedFor": tested_for,
                "result": LAB_RESULT_MAP.get(_get(d, "resultado_pcr_hisopado"), LAB_RESULT_MAP.get(resultado, "")),
                "dateOfResult": _to_iso_date(_get(d, "fecha_resultado_laboratorio")),
            })

        # Orina
        if _get(d, "muestra_orina").upper() == "SI":
            results.append({
                "sampleType": "LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_URINE",
                "dateSampleTaken": _to_iso_date(_get(d, "muestra_orina_fecha")),
                "testType": "PCR",
                "testedFor": tested_for,
                "result": LAB_RESULT_MAP.get(_get(d, "resultado_pcr_orina"), LAB_RESULT_MAP.get(resultado, "")),
                "dateOfResult": _to_iso_date(_get(d, "fecha_resultado_laboratorio")),
            })

    return results
