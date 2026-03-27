"""
Mapeo de campos: BD unificada → GoData Guatemala API payload.
Convierte un registro de nuestra BD SQLite al formato esperado por GoData Guatemala.

GoData Guatemala usa variables en español con underscore, valores en MAYUSCULAS,
y fechas ISO 8601 con tiempo (YYYY-MM-DDT00:00:00.000Z).

IMPORTANTE: Los valores de OPCIONES (dropdowns, multi-answer) REQUIEREN acentos
(ej: "SARAMPIÓN", "RUBÉOLA", "BÚSQUEDA ACTIVA INSTITUCIONAL").
Solo los campos de TEXTO LIBRE (nombres, direcciones) se normalizan sin acentos.

Diferencias clave vs template WHO genérico:
- Autenticación: Bearer token (access_token), NO id-based
- Variables en español con underscores y trailing underscores
- Síntomas: campo único multi-answer (que_sintomas_) con array
- Clasificación final: códigos numéricos (1=Sarampión, 2=Rubéola, etc.)
- DMS y municipio: variables cascadeadas por departamento con sufijos
- Acciones de respuesta: "1"/"2" en vez de "SI"/"NO"
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
    "CLASIFICADO": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_CONFIRMED",
    "CLÍNICO": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_PROBABLE",
    "CLINICO": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_PROBABLE",
    "DESCARTADO": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_NOT_A_CASE_DISCARDED",
    "NO CUMPLE DEFINICIÓN": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_NOT_A_CASE_DISCARDED",
    "NO CUMPLE DEFINICION": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_NOT_A_CASE_DISCARDED",
}

OUTCOME_MAP = {
    "RECUPERADO": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_RECOVERED",
    "CON SECUELAS": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_ALIVE",
    "FALLECIDO": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_DECEASED",
    "MEJORADO": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_RECOVERED",
    "MUERTO": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_DECEASED",
    # Códigos numéricos Guatemala
    "1": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_RECOVERED",
    "2": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_ALIVE",       # Con Secuelas
    "3": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_DECEASED",
    "4": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_ALIVE",       # Desconocido
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


# ═══════════════════════════════════════════════════════════
# GUATEMALA: MAPEO DE VARIABLES CASCADEADAS POR DEPARTAMENTO
# ═══════════════════════════════════════════════════════════

# DMS variable suffix por departamento
# Ej: CHIQUIMULA → "distrito_municipal_de_salud_dms_CH"
_DMS_VARIABLE_MAP = {
    "ALTA VERAPAZ": "distrito_municipal_de_salud_dms",
    "BAJA VERAPAZ": "distrito_municipal_de_salud_dms_",
    "CHIMALTENANGO": "distrito_municipal_de_salud_dms_CHI",
    "CHIQUIMULA": "distrito_municipal_de_salud_dms_CH",
    "EL PROGRESO": "distrito_municipal_de_salud_dms1",
    "ESCUINTLA": "distrito_municipal_de_salud_dms3",
    # Guatemala tiene 4 DAS — se resuelve con _resolve_guatemala_dms()
    # Default is dms4 (Central); specific sub-DAS resolved via _GUATEMALA_DMS_MAP
    "GUATEMALA": "distrito_municipal_de_salud_dms4",
    "GUATEMALA CENTRAL": "distrito_municipal_de_salud_dms4",
    "GUATEMALA NOR OCCIDENTE": "distrito_municipal_de_salud_dms5",
    "GUATEMALA NOR ORIENTE": "distrito_municipal_de_salud_dms6",
    "GUATEMALA SUR": "distrito_municipal_de_salud_dms7",
    "HUEHUETENANGO": "distrito_municipal_de_salud_dms8",
    "IXCAN": "distrito_municipal_de_salud_dms9",
    "IXIL": "distrito_municipal_de_salud_dms10",
    "IZABAL": "distrito_municipal_de_salud_dms11",
    "JALAPA": "distrito_municipal_de_salud_dms12",
    "JUTIAPA": "distrito_municipal_de_salud_dms13",
    "PETEN NORTE": "distrito_municipal_de_salud_dms14",
    "PETEN SUR OCCIDENTE": "distrito_municipal_de_salud_dms15",
    "PETEN SUR ORIENTE": "distrito_municipal_de_salud_dms16",
    "QUETZALTENANGO": "distrito_municipal_de_salud_dms17",
    "QUICHE": "distrito_municipal_de_salud_dms18",
    "RETALHULEU": "distrito_municipal_de_salud_dms19",
    "SACATEPEQUEZ": "distrito_municipal_de_salud_dms20",
    "SAN MARCOS": "distrito_municipal_de_salud_dms21",
    "SANTA ROSA": "distrito_municipal_de_salud_dms22",
    "SOLOLA": "distrito_municipal_de_salud_dms23",
    "SUCHITEPEQUEZ": "distrito_municipal_de_salud_dms24",
    "TOTONICAPAN": "distrito_municipal_de_salud_dms25",
    "ZACAPA": "distrito_municipal_de_salud_dms26",
}

# Guatemala tiene 4 DAS con diferentes DMS variables
# Each DMS municipality maps to its correct DAS variable suffix:
#   dms4 = GUATEMALA CENTRAL
#   dms5 = GUATEMALA NOR OCCIDENTE
#   dms6 = GUATEMALA NOR ORIENTE
#   dms7 = GUATEMALA SUR
_GUATEMALA_DMS_MAP = {
    # ── GUATEMALA CENTRAL (dms4) ──
    "BETHANIA": "distrito_municipal_de_salud_dms4",
    "CENTRO AMERICA": "distrito_municipal_de_salud_dms4",
    "EL AMPARO": "distrito_municipal_de_salud_dms4",
    "EL PARAISO": "distrito_municipal_de_salud_dms4",
    "JUSTO RUFINO BARRIOS": "distrito_municipal_de_salud_dms4",
    "LA FLORIDA": "distrito_municipal_de_salud_dms4",
    "LA REFORMITA": "distrito_municipal_de_salud_dms4",
    "PRIMERO DE JULIO": "distrito_municipal_de_salud_dms4",
    "ZONA 6": "distrito_municipal_de_salud_dms4",
    "ZONA 11": "distrito_municipal_de_salud_dms4",
    "ZONA 18": "distrito_municipal_de_salud_dms4",
    "ZONA 21": "distrito_municipal_de_salud_dms4",
    # ── GUATEMALA NOR OCCIDENTE (dms5) ──
    "CHUARRANCHO": "distrito_municipal_de_salud_dms5",
    "CIUDAD QUETZAL": "distrito_municipal_de_salud_dms5",
    "COMUNIDAD": "distrito_municipal_de_salud_dms5",
    "EL MILAGRO": "distrito_municipal_de_salud_dms5",
    "MIXCO": "distrito_municipal_de_salud_dms5",
    "SAN JUAN SACATEPEQUEZ": "distrito_municipal_de_salud_dms5",
    "SAN PEDRO SACATEPEQUEZ": "distrito_municipal_de_salud_dms5",
    "SAN RAYMUNDO": "distrito_municipal_de_salud_dms5",
    "SANTIAGO SACATEPEQUEZ": "distrito_municipal_de_salud_dms5",
    "LO DE COY": "distrito_municipal_de_salud_dms5",
    # ── GUATEMALA NOR ORIENTE (dms6) ──
    "CHINAUTLA": "distrito_municipal_de_salud_dms6",
    "FRAIJANES": "distrito_municipal_de_salud_dms6",
    "PALENCIA": "distrito_municipal_de_salud_dms6",
    "SAN JOSE DEL GOLFO": "distrito_municipal_de_salud_dms6",
    "SAN JOSE PINULA": "distrito_municipal_de_salud_dms6",
    "SAN PEDRO AYAMPUC": "distrito_municipal_de_salud_dms6",
    "SANTA CATARINA PINULA": "distrito_municipal_de_salud_dms6",
    "TIERRA NUEVA": "distrito_municipal_de_salud_dms6",
    # ── GUATEMALA SUR (dms7) ──
    "AMATITLAN": "distrito_municipal_de_salud_dms7",
    "BOCA DEL MONTE": "distrito_municipal_de_salud_dms7",
    "CIUDAD REAL": "distrito_municipal_de_salud_dms7",
    "EL MEZQUITAL": "distrito_municipal_de_salud_dms7",
    "PERONIA": "distrito_municipal_de_salud_dms7",
    "SAN MIGUEL PETAPA": "distrito_municipal_de_salud_dms7",
    "VILLA CANALES": "distrito_municipal_de_salud_dms7",
    "VILLA NUEVA": "distrito_municipal_de_salud_dms7",
}

# Guatemala municipio → DAS name (for direccion_de_area_de_salud option value)
# Complete mapping from GoData template: 4 DAS areas, all DMS municipalities
_GUATEMALA_MUNICIPIO_TO_DAS = {
    # ── GUATEMALA CENTRAL (DMS4) ──
    "GUATEMALA": "GUATEMALA CENTRAL",
    "BETHANIA": "GUATEMALA CENTRAL",
    "CENTRO AMERICA": "GUATEMALA CENTRAL",
    "EL AMPARO": "GUATEMALA CENTRAL",
    "EL PARAISO": "GUATEMALA CENTRAL",
    "JUSTO RUFINO BARRIOS": "GUATEMALA CENTRAL",
    "LA FLORIDA": "GUATEMALA CENTRAL",
    "LA REFORMITA": "GUATEMALA CENTRAL",
    "PRIMERO DE JULIO": "GUATEMALA CENTRAL",
    "ZONA 6": "GUATEMALA CENTRAL",
    "ZONA 11": "GUATEMALA CENTRAL",
    "ZONA 18": "GUATEMALA CENTRAL",
    "ZONA 21": "GUATEMALA CENTRAL",
    # ── GUATEMALA NOR OCCIDENTE (DMS5) ──
    "CHUARRANCHO": "GUATEMALA NOR OCCIDENTE",
    "CIUDAD QUETZAL": "GUATEMALA NOR OCCIDENTE",
    "COMUNIDAD": "GUATEMALA NOR OCCIDENTE",
    "EL MILAGRO": "GUATEMALA NOR OCCIDENTE",
    "MIXCO": "GUATEMALA NOR OCCIDENTE",
    "SAN JUAN SACATEPEQUEZ": "GUATEMALA NOR OCCIDENTE",
    "SAN PEDRO SACATEPEQUEZ": "GUATEMALA NOR OCCIDENTE",
    "SAN RAYMUNDO": "GUATEMALA NOR OCCIDENTE",
    "SANTIAGO SACATEPEQUEZ": "GUATEMALA NOR OCCIDENTE",
    "LO DE COY": "GUATEMALA NOR OCCIDENTE",
    # ── GUATEMALA NOR ORIENTE (DMS6) ──
    "CHINAUTLA": "GUATEMALA NOR ORIENTE",
    "FRAIJANES": "GUATEMALA NOR ORIENTE",
    "PALENCIA": "GUATEMALA NOR ORIENTE",
    "SAN JOSE DEL GOLFO": "GUATEMALA NOR ORIENTE",
    "SAN JOSE PINULA": "GUATEMALA NOR ORIENTE",
    "SAN PEDRO AYAMPUC": "GUATEMALA NOR ORIENTE",
    "SANTA CATARINA PINULA": "GUATEMALA NOR ORIENTE",
    "TIERRA NUEVA": "GUATEMALA NOR ORIENTE",
    # ── GUATEMALA SUR (DMS7) ──
    "AMATITLAN": "GUATEMALA SUR",
    "BOCA DEL MONTE": "GUATEMALA SUR",
    "CIUDAD REAL": "GUATEMALA SUR",
    "EL MEZQUITAL": "GUATEMALA SUR",
    "PERONIA": "GUATEMALA SUR",
    "SAN MIGUEL PETAPA": "GUATEMALA SUR",
    "VILLA CANALES": "GUATEMALA SUR",
    "VILLA NUEVA": "GUATEMALA SUR",
}

# Municipio variable suffix por departamento
_MUNICIPIO_VARIABLE_MAP = {
    "ALTA VERAPAZ": "municipio_de_residencia_",
    "BAJA VERAPAZ": "municipio_de_residencia1",
    "CHIMALTENANGO": "municipio_de_residencia2",
    "CHIQUIMULA": "municipio_de_residencia3",
    "EL PROGRESO": "municipio_de_residencia4",
    "ESCUINTLA": "municipio_de_residencia5",
    "GUATEMALA": "municipio_de_residencia6",
    "HUEHUETENANGO": "municipio_de_residencia7",
    "IZABAL": "municipio_de_residencia8",
    "JALAPA": "municipio_de_residencia9",
    "JUTIAPA": "municipio_de_residencia10",
    "PETEN": "municipio_de_residencia11",
    "PETEN NORTE": "municipio_de_residencia11",
    "PETEN SUR OCCIDENTE": "municipio_de_residencia11",
    "PETEN SUR ORIENTE": "municipio_de_residencia11",
    "QUETZALTENANGO": "municipio_de_residencia12",
    "QUICHE": "municipio_de_residencia13",
    "RETALHULEU": "municipio_de_residencia14",
    "SACATEPEQUEZ": "municipio_de_residencia15",
    "SAN MARCOS": "municipio_de_residencia16",
    "SANTA ROSA": "municipio_de_residencia17",
    "SOLOLA": "municipio_de_residencia18",
    "SUCHITEPEQUEZ": "municipio_de_residencia19",
    "TOTONICAPAN": "municipio_de_residencia20",
    "ZACAPA": "municipio_de_residencia21",
}

# Servicio de Salud suffix por departamento (matches DMS pattern)
_SERVICIO_SALUD_VARIABLE_MAP = {
    "ALTA VERAPAZ": "servicio_de_salud",
    "BAJA VERAPAZ": "servicio_de_salud_",
    "CHIMALTENANGO": "servicio_de_salud_CHI",
    "CHIQUIMULA": "servicio_de_salud_CH",
    "EL PROGRESO": "servicio_de_salud1",
    "ESCUINTLA": "servicio_de_salud3",
    "GUATEMALA": "servicio_de_salud4",
    "HUEHUETENANGO": "servicio_de_salud8",
    "IXCAN": "servicio_de_salud9",
    "IXIL": "servicio_de_salud10",
    "IZABAL": "servicio_de_salud11",
    "JALAPA": "servicio_de_salud12",
    "JUTIAPA": "servicio_de_salud13",
    "PETEN NORTE": "servicio_de_salud14",
    "PETEN SUR OCCIDENTE": "servicio_de_salud15",
    "PETEN SUR ORIENTE": "servicio_de_salud16",
    "QUETZALTENANGO": "servicio_de_salud17",
    "QUICHE": "servicio_de_salud18",
    "RETALHULEU": "servicio_de_salud19",
    "SACATEPEQUEZ": "servicio_de_salud20",
    "SAN MARCOS": "servicio_de_salud21",
    "SANTA ROSA": "servicio_de_salud22",
    "SOLOLA": "servicio_de_salud23",
    "SUCHITEPEQUEZ": "servicio_de_salud24",
    "TOTONICAPAN": "servicio_de_salud25",
    "ZACAPA": "servicio_de_salud26",
}

# Clasificación final Guatemala: códigos numéricos
_CLASIFICACION_FINAL_MAP = {
    "CONFIRMADO SARAMPIÓN": "1",
    "CONFIRMADO SARAMPION": "1",
    "SARAMPION": "1",
    "SARAMPIÓN": "1",
    "CONFIRMADO RUBÉOLA": "2",
    "CONFIRMADO RUBEOLA": "2",
    "RUBEOLA": "2",
    "RUBÉOLA": "2",
    "DESCARTADO": "3",
    "PENDIENTE": "5",
    "SOSPECHOSO": "5",
}

# Condición final Guatemala: códigos numéricos
_CONDICION_FINAL_MAP = {
    "RECUPERADO": "1",
    "CON SECUELAS": "2",
    "FALLECIDO": "3",
    "MUERTO": "3",
    "DESCONOCIDO": "4",
}

# Fuente de infección Guatemala: códigos numéricos
_FUENTE_INFECCION_MAP = {
    "IMPORTADO": "1",
    "RELACIONADO CON IMPORTACION": "2",
    "RELACIONADO CON IMPORTACIÓN": "2",
    "RELACIONADO CON LA IMPORTACION": "2",
    "ENDEMICO": "3",
    "ENDÉMICO": "3",
    "AUTOCTONO": "3",
    "AUTÓCTONO": "3",
    "FUENTE DESCONOCIDA": "4",
    "DESCONOCIDO": "4",
}

# Caso analizado por Guatemala: códigos numéricos (MULTIPLE_ANSWERS)
_CASO_ANALIZADO_MAP = {
    "CONAPI": "1",
    "DEGR": "2",
    "COMISION NACIONAL": "3",
    "COMISIÓN NACIONAL": "3",
    "OTROS": "4",
    "OTRO": "4",
}

# Criterio confirmación sarampión Guatemala
_CRITERIO_CONFIRMACION_SARAMPION_MAP = {
    "LABORATORIO": "LABSR",
    "LAB": "LABSR",
    "NEXO EPIDEMIOLOGICO": "NE",
    "NEXO EPIDEMIOLÓGICO": "NE",
    "CLINICO": "CX",
    "CLÍNICO": "CX",
    "DIAGNOSTICO CLINICO": "CX",
    "DIAGNÓSTICO CLÍNICO": "CX",
}

# Criterio confirmación rubéola Guatemala
_CRITERIO_CONFIRMACION_RUBEOLA_MAP = {
    "LABORATORIO": "LABRB",
    "LAB": "LABRB",
    "NEXO EPIDEMIOLOGICO": "NERB",
    "NEXO EPIDEMIOLÓGICO": "NERB",
    "CLINICO": "CXRB",
    "CLÍNICO": "CXRB",
}

# Criterio descarte Guatemala
_CRITERIO_DESCARTE_MAP = {
    "LABORATORIO": "LAB",
    "LABORATORIAL": "LAB",
    "IGM NEGATIVO": "LAB",
    "REACCION VACUNAL": "RVAC",
    "REACCIÓN VACUNAL": "RVAC",
    "CLINICO": "CX2",
    "CLÍNICO": "CX2",
    "OTRO": "OTRO",
    "OTRO DIAGNOSTICO": "OTRO",
    "OTRO DIAGNÓSTICO": "OTRO",
}

# Vitamina A Guatemala: 1=SI, 2=NO, 3=Desconocido
_VITAMINA_A_MAP = {
    "SI": "1",
    "SÍ": "1",
    "NO": "2",
    "DESCONOCIDO": "3",
}

# Síntomas: mapeo de nuestros campos individuales al array multi-answer de Guatemala
_SYMPTOM_LABEL_MAP = {
    "signo_fiebre": "Fiebre",
    "signo_exantema": "Exantema/ Rash",
    "signo_tos": "Tos",
    "signo_conjuntivitis": "Conjuntivitis",
    "signo_coriza": "Coriza / Catarro",
    "signo_manchas_koplik": "Manchas de Koplik",
    "signo_adenopatias": "Adenopatías",
    "signo_artralgia": "Artralgia / Artritis",
}

# Diagnóstico de sospecha
_DIAGNOSTICO_MAP = {
    "SARAMPIÓN": "SARAMPIÓN",
    "SARAMPION": "SARAMPIÓN",
    "RUBÉOLA": "RUBÉOLA",
    "RUBEOLA": "RUBÉOLA",
    "DENGUE": "DENGUE",
    "OTRA FEBRIL EXANTEMATICA": "OTRA FEBRIL EXANTEMÁTICA",
    "OTRA FEBRIL EXANTEMÁTICA": "OTRA FEBRIL EXANTEMÁTICA",
    "CASO ALTAMENTE SOSPECHOSO": "SARAMPIÓN",
}

# Fuente de notificación Guatemala (texto directo)
_FUENTE_NOTIFICACION_MAP = {
    "SERVICIO DE SALUD": "SERVICIO DE SALUD",
    "PUBLICA": "SERVICIO DE SALUD",
    "PRIVADA": "SERVICIO DE SALUD",
    "LABORATORIO": "BÚSQUEDA ACTIVA LABORATORIAL",
    "COMUNIDAD": "BÚSQUEDA ACTIVA COMUNITARIA",
    "BÚSQUEDA ACTIVA LABORATORIAL": "BÚSQUEDA ACTIVA LABORATORIAL",
    "BUSQUEDA ACTIVA LABORATORIAL": "BÚSQUEDA ACTIVA LABORATORIAL",
    "BÚSQUEDA ACTIVA COMUNITARIA": "BÚSQUEDA ACTIVA COMUNITARIA",
    "BUSQUEDA ACTIVA COMUNITARIA": "BÚSQUEDA ACTIVA COMUNITARIA",
    "BÚSQUEDA ACTIVA INSTITUCIONAL": "BÚSQUEDA ACTIVA INSTITUCIONAL",
    "BUSQUEDA ACTIVA INSTITUCIONAL": "BÚSQUEDA ACTIVA INSTITUCIONAL",
    "INVESTIGACIÓN DE CONTACTOS": "INVESTIGACIÓN DE CONTACTOS",
    "INVESTIGACION DE CONTACTOS": "INVESTIGACIÓN DE CONTACTOS",
    "DEFUNCIÓN": "DEFUNCIÓN",
    "DEFUNCION": "DEFUNCIÓN",
}

# Tipo de vacuna Guatemala (texto para multi-answer)
_TIPO_VACUNA_MAP = {
    "SPR": "SPR \u2013 Sarampión Paperas Rubéola",
    "SRP": "SPR \u2013 Sarampión Paperas Rubéola",
    "SRP SARAMPION RUBEOLA PAPERAS": "SPR \u2013 Sarampión Paperas Rubéola",
    "SR": "SR \u2013 Sarampión Rubéola",
    "SR SARAMPION RUBEOLA": "SR \u2013 Sarampión Rubéola",
    "SPRV": "SPRV \u2013 Sarampión Paperas Rubéola Varicela",
    "ANTISARAMPINOSA": "Antisarampionosa",
    "ANTIRUBÉOLICA": "Antirubeólica",
    "ANTIRUBEOLICA": "Antirubeólica",
}

# Fuente info vacunación Guatemala
_FUENTE_INFO_VACUNA_MAP = {
    "CARNÉ DE VACUNACIÓN": "CARNÉ DE VACUNACIÓN",
    "CARNE DE VACUNACION": "CARNÉ DE VACUNACIÓN",
    "EN CARNE": "CARNÉ DE VACUNACIÓN",
    "SIGSA 5A CUADERNO": "SIGSA 5a/Cuaderno",
    "EN SIGSA 5A": "SIGSA 5a/Cuaderno",
    "VERBAL": "Verbal/Historia",
}

# Fuente posible de contagio Guatemala (multi-answer)
_FUENTE_CONTAGIO_MAP = {
    "CONTACTO EN EL HOGAR": "Hogar",
    "SERVICIO DE SALUD": "Servicio de Salud",
    "COMUNIDAD": "Comunidad",
    "ESPACIO PUBLICO": "Espacio público",
    "ESPACIO PÚBLICO": "Espacio público",
    "DESCONOCIDO": "Desconocido",
    "OTRO": "Otro",
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
    """Normaliza texto libre para GoData: MAYUSCULAS sin tildes.

    Usar SOLO para campos de texto libre: nombres, direcciones, observaciones.
    Para valores de opciones/dropdowns, usar _godata_option().
    """
    if not text:
        return text
    return _strip_accents(text).upper()


def _godata_option(text: str) -> str:
    """Normaliza texto de opción para GoData: MAYÚSCULAS pero CON tildes.

    GoData Guatemala REQUIERE acentos en valores de opciones/dropdowns
    (ej: "SARAMPIÓN", "RUBÉOLA", "BÚSQUEDA ACTIVA INSTITUCIONAL").
    """
    if not text:
        return text
    return text.upper()


def _to_iso_date(date_str: str) -> Optional[str]:
    """Convierte fecha a formato ISO 8601 con tiempo: YYYY-MM-DDT00:00:00.000Z (GoData Guatemala)."""
    if not date_str:
        return None
    date_str = date_str.strip()
    # Si ya tiene el formato correcto, devolverlo
    if len(date_str) >= 24 and date_str[10] == "T" and date_str.endswith("Z"):
        return date_str
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            dt = datetime.strptime(date_str[:19] if "T" in date_str else date_str[:10], fmt)
            return dt.strftime("%Y-%m-%dT00:00:00.000Z")
        except ValueError:
            continue
    # Último intento: solo primeros 10 caracteres como YYYY-MM-DD
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return dt.strftime("%Y-%m-%dT00:00:00.000Z")
    except ValueError:
        pass
    return None


def _safe_int(val, default=0) -> int:
    """Convert to int, extracting first numeric value from text like '2 dosis'."""
    try:
        return int(val)
    except (ValueError, TypeError):
        # Try to extract a number from text (e.g. "2 dosis" → 2, "Más de 3" → 3)
        if val:
            import re
            match = re.search(r'(\d+)', str(val))
            if match:
                return int(match.group(1))
        return default


def _safe_float(val, default=None):
    """Convierte a float, devuelve None si no es posible."""
    try:
        return float(str(val).replace(",", "."))
    except (ValueError, TypeError):
        return default


def _si_no_to_godata(val: str) -> str:
    """Convierte SI/NO/DESCONOCIDO a SI/NO (Guatemala usa español)."""
    v = str(val).upper().strip()
    if v in ("SI", "SÍ", "YES", "1"):
        return "SI"
    elif v in ("NO", "0", "2"):
        return "NO"
    return "NO"


def _qa_val(value) -> list:
    """Envuelve un valor en el formato questionnaireAnswers: [{"value": X}]."""
    return [{"value": value}]


def _resolve_dms_variable(departamento: str, distrito: str = "") -> Optional[str]:
    """Resuelve la variable DMS correcta para un departamento.

    Para Guatemala, intenta determinar la DAS area basándose en el distrito.
    """
    dept = _strip_accents(departamento).upper().strip() if departamento else ""
    if not dept:
        return None

    if dept == "GUATEMALA" and distrito:
        dist_upper = _strip_accents(distrito).upper().strip()
        if dist_upper in _GUATEMALA_DMS_MAP:
            return _GUATEMALA_DMS_MAP[dist_upper]
        # Default para Guatemala si no podemos determinar la DAS
        return "distrito_municipal_de_salud_dms4"

    return _DMS_VARIABLE_MAP.get(dept)


def _resolve_municipio_variable(departamento: str) -> Optional[str]:
    """Resuelve la variable de municipio correcta para un departamento."""
    dept = _strip_accents(departamento).upper().strip() if departamento else ""
    if not dept:
        return None
    return _MUNICIPIO_VARIABLE_MAP.get(dept)


def _resolve_servicio_variable(departamento: str, municipio: str = "") -> Optional[str]:
    """Resuelve la variable de servicio de salud correcta para un departamento.

    Para Guatemala, resuelve a la sub-DAS correcta basándose en municipio.
    """
    dept = _strip_accents(departamento).upper().strip() if departamento else ""
    if not dept:
        return None
    if dept == "GUATEMALA" and municipio:
        muni_upper = municipio.upper().strip()
        das = _GUATEMALA_MUNICIPIO_TO_DAS.get(muni_upper, "GUATEMALA CENTRAL")
        # Map DAS name back to suffix: CENTRAL=4, NOR OCCIDENTE=5, NOR ORIENTE=6, SUR=7
        _GUATEMALA_DAS_SERVICIO = {
            "GUATEMALA CENTRAL": "servicio_de_salud4",
            "GUATEMALA NOR OCCIDENTE": "servicio_de_salud5",
            "GUATEMALA NOR ORIENTE": "servicio_de_salud6",
            "GUATEMALA SUR": "servicio_de_salud7",
        }
        return _GUATEMALA_DAS_SERVICIO.get(das, "servicio_de_salud4")
    return _SERVICIO_SALUD_VARIABLE_MAP.get(dept)


# ═══════════════════════════════════════════════════════════
# MAPEO PRINCIPAL: record → GoData Guatemala case payload
# ═══════════════════════════════════════════════════════════

def map_record_to_godata(record: dict) -> Dict:
    """Convierte un registro de nuestra BD al formato GoData Guatemala case.

    Produce questionnaireAnswers con variables en español, valores en MAYUSCULAS,
    fechas ISO con tiempo, y variables cascadeadas por departamento.

    Returns:
        Dict listo para POST /api/outbreaks/{id}/cases
    """
    d = record

    # ─── Campos base del modelo Person/Case ─────────────
    # Split nombres: first word = firstName, rest = middleName
    _nombres_parts = _godata_text(_get(d, "nombres")).split()
    case = {
        "firstName": _nombres_parts[0] if _nombres_parts else "",
        "middleName": " ".join(_nombres_parts[1:]) if len(_nombres_parts) > 1 else "",
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

    # Clasificación (campo estándar GoData — MUST be set for GoData filters/dashboard)
    # NOTE: All 5 existing Guatemala cases have classification=null because
    # operators only fill questionnaireAnswers.clasificacion_final but not this
    # standard field. We set BOTH to ensure proper GoData filtering.
    clasificacion = _get(d, "clasificacion_caso").upper()
    if clasificacion in CLASSIFICATION_MAP:
        case["classification"] = CLASSIFICATION_MAP[clasificacion]
    else:
        # Default to SUSPECT for unclassified cases
        case["classification"] = "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_SUSPECT"

    # Condición final / Outcome (campo estándar GoData — same issue as classification)
    condicion = _get(d, "condicion_final_paciente") or _get(d, "condicion_egreso")
    if condicion:
        cond_upper = condicion.upper()
        if cond_upper in OUTCOME_MAP:
            case["outcomeId"] = OUTCOME_MAP[cond_upper]
            if cond_upper in ("FALLECIDO", "MUERTO", "3"):
                case["dateOfOutcome"] = _to_iso_date(_get(d, "fecha_defuncion"))

    # Riesgo y estado de investigación (campos estándar GoData)
    # Sarampión es SIEMPRE alto riesgo en Guatemala
    case["riskLevel"] = "LNG_REFERENCE_DATA_CATEGORY_RISK_LEVEL_3_HIGH"
    case["investigationStatus"] = "LNG_REFERENCE_DATA_CATEGORY_INVESTIGATION_STATUS_UNDER_INVESTIGATION"

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
        address["addressLine1"] = f"{_godata_text(poblado)}, {address.get('addressLine1', '')}"
    case["addresses"] = [address]

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

    # ═════════════════════════════════════════════════════
    # QUESTIONNAIRE ANSWERS — GoData Guatemala format
    # ═════════════════════════════════════════════════════
    qa = {}

    # ─── Section headers (MARKUP fields) ────────────────
    qa["fecha_de_notificacion"] = _qa_val("Fecha de Notificacion")
    qa["informacion_del_paciente"] = _qa_val("DATOS GENERALES")
    qa["antecedentes_medicos_y_de_vacunacion"] = _qa_val("ANTECEDENTES MEDICOS Y DE VACUNACION")
    qa["datos_clinicos"] = _qa_val("DATOS CLINICOS")

    # ─── Sección 0: Diagnóstico de sospecha ─────────────
    dx_sospecha = _get(d, "diagnostico_sospecha").upper()
    dx_mapped = _DIAGNOSTICO_MAP.get(dx_sospecha)
    if dx_mapped:
        qa["diagnostico_de_sospecha_"] = _qa_val(dx_mapped)
    elif _get(d, "diagnostico_registrado").upper().startswith("B05"):
        qa["diagnostico_de_sospecha_"] = _qa_val("SARAMPIÓN")
    elif _get(d, "diagnostico_registrado").upper().startswith("B06"):
        qa["diagnostico_de_sospecha_"] = _qa_val("RUBÉOLA")
    else:
        qa["diagnostico_de_sospecha_"] = _qa_val("SARAMPIÓN")

    # Caso altamente sospechoso (sub-question of diagnostico)
    dx_raw = _get(d, "diagnostico_sospecha")
    if isinstance(dx_raw, str) and "altamente" in dx_raw.lower():
        qa["caso_altamente_sospechoso_de_sarampion"] = _qa_val("SI")

    # ─── Sección 1: Unidad Notificadora ─────────────────
    # Dirección de Área de Salud (departamento)
    dept_das = _get(d, "departamento_das") or _get(d, "departamento_residencia")
    if dept_das:
        # Bug 2: Guatemala has 4 sub-DAS areas — resolve based on municipality
        dept_upper = dept_das.upper().strip()
        if dept_upper == "GUATEMALA":
            muni_for_das = (_get(d, "municipio_residencia") or "").upper().strip()
            das_value = _GUATEMALA_MUNICIPIO_TO_DAS.get(muni_for_das, "GUATEMALA CENTRAL")
            qa["direccion_de_area_de_salud"] = _qa_val(das_value)
        else:
            qa["direccion_de_area_de_salud"] = _qa_val(_godata_option(dept_das))

    # DMS (cascadeado por departamento)
    distrito = _get(d, "distrito_salud") or _get(d, "municipio_residencia")
    if dept_das and distrito:
        dms_var = _resolve_dms_variable(dept_das, distrito)
        if dms_var:
            qa[dms_var] = _qa_val(_godata_option(distrito))

    # Servicio de Salud (cascadeado por departamento)
    servicio = _get(d, "servicio_salud_mspas") or _get(d, "unidad_medica")
    if dept_das and servicio:
        muni_for_serv = _get(d, "municipio_residencia")
        serv_var = _resolve_servicio_variable(dept_das, muni_for_serv)
        if serv_var:
            qa[serv_var] = _qa_val(_godata_option(servicio))

    # Fecha de consulta
    fecha_consulta = _to_iso_date(_get(d, "fecha_registro_diagnostico") or _get(d, "fecha_consulta"))
    if fecha_consulta:
        qa["fecha_de_consulta"] = _qa_val(fecha_consulta)

    # Fecha de investigación domiciliaria
    fecha_visita = _to_iso_date(_get(d, "fecha_visita_domiciliaria"))
    if fecha_visita:
        qa["fecha_de_investigacion_domiciliaria"] = _qa_val(fecha_visita)

    # Investigador
    investigador = _get(d, "nombre_investigador") or _get(d, "nombre_quien_investiga") or _get(d, "nom_responsable")
    if investigador:
        qa["nombre_de_quien_investiga"] = _qa_val(_godata_text(investigador))
    cargo = _get(d, "cargo_investigador") or _get(d, "cargo_quien_investiga") or _get(d, "cargo_responsable")
    if cargo:
        qa["cargo_de_quien_investiga"] = _qa_val(_godata_text(cargo))

    # Teléfono y correo del investigador
    tel_inv = (_get(d, "telefono_investigador") or _get(d, "telefono_responsable")).replace("-", "").replace(" ", "")
    if tel_inv:
        tel_val = _safe_int(tel_inv)
        qa["telefono"] = [{"value": tel_val or tel_inv}]
    correo_inv = _get(d, "correo_investigador") or _get(d, "correo_responsable")
    if correo_inv:
        qa["correo_electronico"] = _qa_val(correo_inv)
    else:
        qa["correo_electronico"] = [{}]

    # Otro establecimiento (IGSS)
    if _get(d, "es_seguro_social").upper() == "SI" or _get(d, "unidad_medica"):
        qa["otro_establecimiento"] = _qa_val("Seguro Social (IGSS)")

    # Fuente de notificación
    fuente = _get(d, "fuente_notificacion")
    if fuente:
        fuente_upper = fuente.upper()
        mapped = _FUENTE_NOTIFICACION_MAP.get(fuente_upper, _godata_option(fuente))
        qa["fuente_de_notificacion_"] = _qa_val(mapped)

    # ─── Sección 2: Información del Paciente ────────────
    # Tipo de identificación
    if tipo_id:
        qa["codigo_unico_de_identificacion_dpi_pasaporte_otro"] = _qa_val(tipo_id.upper())
    if num_id:
        num_val = _safe_int(num_id)
        qa["no_de_dpi"] = _qa_val(num_val if num_val else num_id)

    # Encargado / tutor
    encargado = _get(d, "nombre_encargado")
    if encargado:
        qa["nombre_del_tutor_"] = _qa_val("SI")
        parentesco = _get(d, "parentesco_encargado")
        if parentesco:
            qa["parentesco_"] = _qa_val(_godata_option(parentesco))
    else:
        qa["nombre_del_tutor_"] = _qa_val("NO")

    # Pueblo / etnia
    etnia = _get(d, "pueblo") or _get(d, "pueblo_etnia") or _get(d, "etnia")
    _pueblo_map = {
        "LADINO": "LADINO", "MAYA": "MAYA", "GARIFUNA": "GARÍFUNA",
        "GARÍFUNA": "GARÍFUNA", "XINCA": "XINCA", "EXTRANJERO": "EXTRANJERO",
        "DESCONOCIDO": "DESCONOCIDO",
    }
    if etnia:
        qa["pueblo"] = _qa_val(_pueblo_map.get(etnia.upper(), etnia.upper()))

    # Comunidad lingüística
    com_ling = _get(d, "comunidad_linguistica")
    if com_ling:
        qa["comunidad_linguistica"] = _qa_val(com_ling)  # Keep original case with accents

    # Extranjero / Migrante
    extranjero = _get(d, "es_extranjero").upper()
    qa["extranjero_"] = _qa_val("SI" if extranjero == "SI" else "NO")
    migrante = _get(d, "es_migrante").upper()
    qa["migrante"] = _qa_val("SI" if migrante == "SI" else "NO")

    # Ocupación y escolaridad
    ocupacion = _get(d, "ocupacion")
    if ocupacion:
        qa["ocupacion_"] = _qa_val(_godata_option(ocupacion))
    escolaridad = _get(d, "escolaridad")
    if escolaridad:
        qa["escolaridad_"] = _qa_val(_godata_option(escolaridad))

    # Teléfono del paciente
    tel_pac = _get(d, "telefono_paciente") or _get(d, "telefono_encargado")
    if tel_pac:
        tel_pac_val = _safe_int(tel_pac)
        qa["telefono_"] = _qa_val(tel_pac_val if tel_pac_val else tel_pac)

    # País/Departamento/Municipio de residencia
    pais_res = _get(d, "pais_residencia") or "GUATEMALA"
    qa["pais_de_residencia_"] = _qa_val(_godata_option(pais_res))

    dept_res = _get(d, "departamento_residencia")
    if dept_res:
        qa["departamento_de_residencia_"] = _qa_val(_godata_option(dept_res))

    muni_res = _get(d, "municipio_residencia")
    if dept_res and muni_res:
        muni_var = _resolve_municipio_variable(dept_res)
        if muni_var:
            qa[muni_var] = _qa_val(_godata_option(muni_res))

    # Dirección y lugar poblado
    direccion = _get(d, "direccion_exacta")
    if direccion:
        qa["direccion_de_residencia_"] = _qa_val(_godata_text(direccion))
    lugar_poblado = _get(d, "poblado") or _get(d, "lugar_poblado")
    if lugar_poblado:
        qa["lugar_poblado_"] = _qa_val(_godata_text(lugar_poblado))

    # ─── Sección 3: Antecedentes Médicos y Vacunación ───
    vacunado = _get(d, "vacunado").upper()
    if vacunado in ("SI", "SÍ", "YES"):
        qa["paciente_vacunado_"] = _qa_val("SI")

        # Tipo de vacuna (MULTIPLE_ANSWERS array — detect from individual dose fields)
        vaccines = []
        if _get(d, "dosis_spr") or _get(d, "numero_dosis_spr"):
            vaccines.append("SPR \u2013 Sarampión Paperas Rubéola")
        if _get(d, "dosis_sr") or _get(d, "numero_dosis_sr"):
            vaccines.append("SR \u2013 Sarampión Rubéola")
        if _get(d, "dosis_sprv"):
            vaccines.append("SPRV \u2013 Sarampión Paperas Rubéola Varicela")
        # Fallback to legacy tipo_vacuna
        if not vaccines:
            tipo_vac = _get(d, "tipo_vacuna").upper()
            vac_label = _TIPO_VACUNA_MAP.get(tipo_vac)
            if vac_label:
                vaccines.append(vac_label)
        if vaccines:
            qa["tipo_de_vacuna_recibida_"] = [{"value": vaccines}]

        # Número de dosis SPR (primary)
        n_dosis = _safe_int(_get(d, "numero_dosis_spr") or _get(d, "numero_dosis"))
        if n_dosis:
            qa["numero_de_dosis"] = _qa_val(n_dosis)

        # Número de dosis SR (separate trailing underscore key)
        dosis_sr = _get(d, "dosis_sr") or _get(d, "numero_dosis_sr")
        if dosis_sr:
            qa["numero_de_dosis_"] = [{"value": _safe_int(dosis_sr)}]

        # Fecha última dosis SPR (primary)
        fecha_ult_dosis = _to_iso_date(_get(d, "fecha_ultima_dosis") or _get(d, "fecha_ultima_spr"))
        if fecha_ult_dosis:
            qa["fecha_de_la_ultima_dosis"] = _qa_val(fecha_ult_dosis)

        # Fecha última dosis SR (separate trailing underscore key)
        fecha_sr = _to_iso_date(_get(d, "fecha_ultima_sr"))
        if fecha_sr:
            qa["fecha_de_la_ultima_dosis_"] = _qa_val(fecha_sr)

        # Fuente información vacunación
        fuente_vac = _get(d, "fuente_info_vacuna").upper()
        _fuente_vac_map = {
            "CARNÉ DE VACUNACIÓN": "CARNÉ DE VACUNACIÓN",
            "CARNE DE VACUNACION": "CARNÉ DE VACUNACIÓN",
            "EN CARNE": "CARNÉ DE VACUNACIÓN",
            "EN CARNÉ": "CARNÉ DE VACUNACIÓN",
            "SIGSA 5A CUADERNO": "SIGSA 5A CUADERNO",
            "EN SIGSA 5A": "SIGSA 5A CUADERNO",
            "SIGSA 5B OTROS GRUPOS": "SIGSA 5B OTROS GRUPOS",
            "SIGSA 5B/REGISTRO UNICO": "SIGSA 5B OTROS GRUPOS",
            "REGISTRO UNICO DE VACUNACION": "REGISTRO ÚNICO DE VACUNACIÓN",
            "REGISTRO ÚNICO DE VACUNACIÓN": "REGISTRO ÚNICO DE VACUNACIÓN",
            "VERBAL": "VERBAL",
        }
        fuente_vac_mapped = _fuente_vac_map.get(fuente_vac) or _FUENTE_INFO_VACUNA_MAP.get(fuente_vac)
        if fuente_vac_mapped:
            qa["fuente_de_la_informacion_sobre_la_vacunacion_"] = _qa_val(fuente_vac_mapped)

        # Sector de vacunación
        sector = _get(d, "sector_vacunacion").upper()
        if sector:
            qa["vacunacion_en_el_sector_"] = _qa_val(sector)
    elif vacunado in ("NO",):
        qa["paciente_vacunado_"] = _qa_val("NO")
    else:
        qa["paciente_vacunado_"] = _qa_val("NO")

    # Antecedentes médicos
    antecedentes = _get(d, "tiene_antecedentes_medicos").upper()
    if antecedentes in ("SI", "SÍ"):
        qa["antecedentes_medicos_"] = _qa_val("SI")
        # Build from specific sub-fields first, fallback to comma-separated text
        ant_list = []
        if _get(d, "antecedente_desnutricion").upper() in ("SI", "SÍ"):
            ant_list.append("DESNUTRICIÓN")
        if _get(d, "antecedente_inmunocompromiso").upper() in ("SI", "SÍ"):
            ant_list.append("INMUNOCOMPROMISO")
        if _get(d, "antecedente_enfermedad_cronica").upper() in ("SI", "SÍ"):
            ant_list.append("ENFERMEDAD CRÓNICA")
        # Fallback to comma-separated text
        if not ant_list:
            ant_especifico = _get(d, "antecedentes_medicos_detalle")
            if ant_especifico:
                ant_list = [_godata_text(x.strip()) for x in ant_especifico.split(",") if x.strip()]
        if ant_list:
            qa["especifique_ant"] = [{"value": ant_list}]
    else:
        qa["antecedentes_medicos_"] = _qa_val("NO")

    # ─── Sección 4: Datos Clínicos ──────────────────────
    # Fechas clínicas
    fecha_sintomas = _to_iso_date(_get(d, "fecha_inicio_sintomas"))
    if fecha_sintomas:
        qa["fecha_de_inicio_de_sintomas_"] = _qa_val(fecha_sintomas)

    fecha_fiebre = _to_iso_date(_get(d, "fecha_inicio_fiebre"))
    if fecha_fiebre:
        qa["fecha_de_inicio_de_fiebre_"] = _qa_val(fecha_fiebre)

    fecha_exantema = _to_iso_date(_get(d, "fecha_inicio_erupcion") or _get(d, "fecha_inicio_exantema"))
    if fecha_exantema:
        qa["fecha_de_inicio_de_exantema_rash_"] = _qa_val(fecha_exantema)

    # Síntomas: campo único multi-answer con array de labels
    sintomas_list = []
    for db_field, label in _SYMPTOM_LABEL_MAP.items():
        val = _get(d, db_field).upper()
        if val == "SI":
            sintomas_list.append(label)

    if sintomas_list:
        qa["sintomas_"] = _qa_val("SI")
        qa["que_sintomas_"] = _qa_val(sintomas_list)
    else:
        qa["sintomas_"] = _qa_val("SI")  # Siempre SI para casos sospechosos
        # Si no hay síntomas individuales, intentar campo directo
        sintomas_texto = _get(d, "sintomas_texto")
        if sintomas_texto:
            items = [x.strip() for x in sintomas_texto.split(",") if x.strip()]
            if items:
                qa["que_sintomas_"] = _qa_val(items)

    # Temperatura
    temp = _get(d, "temperatura_celsius").replace(",", ".")
    if temp:
        temp_val = _safe_float(temp)
        if temp_val is not None:
            qa["temp_c"] = _qa_val(temp_val)

    # Hospitalización
    hosp_val = _get(d, "hospitalizado").upper()
    if hosp_val == "SI":
        qa["hospitalizacion_"] = _qa_val("SI")
        hosp_nombre = _get(d, "hosp_nombre")
        if hosp_nombre:
            qa["nombre_del_hospital_"] = _qa_val(_godata_text(hosp_nombre))
        fecha_hosp = _to_iso_date(_get(d, "hosp_fecha"))
        if fecha_hosp:
            qa["fecha_de_hospitalizacion_"] = _qa_val(fecha_hosp)
    else:
        qa["hospitalizacion_"] = _qa_val("NO")

    # Complicaciones
    comps_val = _get(d, "tiene_complicaciones").upper()
    if comps_val == "SI":
        qa["complicaciones_"] = _qa_val("SI")
        comp_types = []
        comp_map = {
            "comp_neumonia": "NEUMONÍA",
            "comp_encefalitis": "ENCEFALITIS",
            "comp_diarrea": "DIARREA",
            "comp_trombocitopenia": "TROMBOCITOPENIA",
            "comp_otitis": "OTITIS MEDIA AGUDA",
            "comp_ceguera": "CEGUERA",
        }
        for field, label in comp_map.items():
            if _get(d, field).upper() == "SI":
                comp_types.append(label)
        otra = _get(d, "comp_otra_texto")
        if otra:
            comp_types.append("OTRA (ESPECIFIQUE)")
            # Also add the specific text as a separate observation if needed
            qa["especifique_otra_complicacion"] = _qa_val(_godata_text(otra))
        if comp_types:
            qa["especifique_complicaciones_"] = _qa_val(comp_types)
    else:
        qa["complicaciones_"] = _qa_val("NO")

    # Aislamiento respiratorio
    aisl = _get(d, "aislamiento_respiratorio").upper()
    if aisl == "SI":
        qa["aislamiento_respiratorio"] = _qa_val("SI")
        fecha_aisl = _to_iso_date(_get(d, "fecha_aislamiento"))
        if fecha_aisl:
            qa["fecha_de_aislamiento"] = _qa_val(fecha_aisl)
    else:
        qa["aislamiento_respiratorio"] = _qa_val("NO")

    # ─── Sección 5: Factores de Riesgo ──────────────────
    # Caso en municipio
    caso_muni = _get(d, "caso_sospechoso_comunidad_3m").upper()
    if caso_muni in ("SI", "SÍ"):
        qa["Existe_caso_en_muni"] = _qa_val("Si")
    elif caso_muni == "NO":
        qa["Existe_caso_en_muni"] = _qa_val("No")
    else:
        qa["Existe_caso_en_muni"] = _qa_val("Desconocido")

    # Contacto con caso sospechoso/confirmado
    contacto_caso = _get(d, "contacto_caso_sospechoso").upper()
    if contacto_caso in ("SI", "SÍ"):
        qa["tuvo_contacto_con_un_caso_sospechoso_o_confirmado"] = _qa_val("Si")
    elif contacto_caso == "NO":
        qa["tuvo_contacto_con_un_caso_sospechoso_o_confirmado"] = _qa_val("No")

    # Viaje 7-23 días previos
    viajo = _get(d, "viajo_7_23_previo").upper()
    if viajo in ("SI", "SÍ"):
        qa["factores_de_riesgo"] = _qa_val("Si")
        qa["viajo_durante_los_7_23_dias"] = _qa_val("Si")

        # Lugares visitados y rutas de desplazamiento
        qa["lugares_visitados_y_rutas_de_desplazamiento_del_caso"] = _qa_val("1")

        # País/destino del viaje
        viaje_pais = _get(d, "viaje_pais")
        viaje_depto = _get(d, "viaje_departamento")
        viaje_muni = _get(d, "viaje_municipio")
        destino_legacy = _get(d, "destino_viaje")

        # Resolve a destination text for displacement route fields
        destino_text = viaje_muni or viaje_depto or viaje_pais or destino_legacy
        if destino_text:
            qa["sitio_ruta_de_desplazamiento_2"] = _qa_val(_godata_text(destino_text))
            qa["direccion_del_lugar_y_rutas_de_desplazamiento_2"] = _qa_val(_godata_text(destino_text))

        if viaje_pais and viaje_pais.upper() not in ("GUATEMALA",):
            qa["pais_departamento_y_municipio"] = _qa_val("OTRO")
            qa["especifique_pais1"] = _qa_val(_godata_text(viaje_pais))
            if viaje_muni:
                qa["municipio"] = _qa_val(_godata_text(viaje_muni))
        elif viaje_depto:
            qa["pais_departamento_y_municipio"] = _qa_val(_godata_text(viaje_depto))
            if viaje_muni:
                qa["municipio"] = _qa_val(_godata_text(viaje_muni))
        elif destino_legacy:
            qa["pais_departamento_y_municipio"] = _qa_val(_godata_text(destino_legacy))

        fecha_salida = _to_iso_date(_get(d, "viaje_fecha_salida"))
        if fecha_salida:
            qa["fecha_de_salida_viaje"] = _qa_val(fecha_salida)
        fecha_entrada = _to_iso_date(_get(d, "viaje_fecha_entrada") or _get(d, "viaje_fecha_regreso"))
        if fecha_entrada:
            qa["fecha_de_entrada_viaje"] = _qa_val(fecha_entrada)
    elif viajo == "NO":
        qa["viajo_durante_los_7_23_dias"] = _qa_val("No")
        qa["lugares_visitados_y_rutas_de_desplazamiento_del_caso"] = _qa_val("2")

    # Persona de la casa viajó al exterior
    familiar_viajo = _get(d, "familiar_viajo_exterior").upper()
    if familiar_viajo in ("SI", "SÍ"):
        qa["alguna_persona_de_su_casa_ha_viajado_al_exterior"] = _qa_val("Si")
    else:
        qa["alguna_persona_de_su_casa_ha_viajado_al_exterior"] = _qa_val("No")

    # Contacto con embarazada
    contacto_emb = _get(d, "contacto_embarazada").upper()
    if contacto_emb in ("SI", "SÍ"):
        qa["el_paciente_estuvo_en_contacto_con_una_mujer_embarazada1"] = _qa_val("Si")
    else:
        qa["el_paciente_estuvo_en_contacto_con_una_mujer_embarazada1"] = _qa_val("No")

    # Fuente posible de contagio (multi-answer)
    fuente_contagio = _get(d, "fuente_posible_contagio")
    if fuente_contagio:
        contagio_upper = fuente_contagio.upper()
        mapped_contagio = _FUENTE_CONTAGIO_MAP.get(contagio_upper, _godata_option(fuente_contagio))
        qa["fuente_posible_de_contagio1"] = _qa_val([mapped_contagio])

    # ─── Sección 6: Acciones de Respuesta ───────────────
    # Nota: Guatemala usa "1" = SI, "2" = NO para sub-preguntas de acciones
    bai = _get(d, "bai_realizada").upper()
    bac = _get(d, "bac_realizada").upper()
    vac_bloqueo = _get(d, "vacunacion_bloqueo").upper()
    monitoreo = _get(d, "monitoreo_rapido_vacunacion").upper()
    vac_barrido = _get(d, "vacunacion_barrido").upper()

    has_any_action = any(v in ("SI", "SÍ") for v in [bai, bac, vac_bloqueo, monitoreo, vac_barrido])
    if has_any_action:
        qa["acciones_de_respuesta"] = _qa_val("SI")
    else:
        qa["acciones_de_respuesta"] = _qa_val("NO")

    # BAI
    if bai in ("SI", "SÍ"):
        qa["se_realizo_busqueda_activa_institucional_de_casos_bai"] = _qa_val("1")
        bai_casos = _safe_int(_get(d, "bai_casos_sospechosos"))
        if bai_casos:
            qa["numero_de_casos_sospechosos_identificados_en_bai"] = _qa_val(bai_casos)
    elif bai == "NO":
        qa["se_realizo_busqueda_activa_institucional_de_casos_bai"] = _qa_val("2")

    # BAC
    if bac in ("SI", "SÍ"):
        qa["se_realizo_busqueda_activa_comunitaria_de_casos_bac"] = _qa_val("1")
        bac_casos = _safe_int(_get(d, "bac_casos_sospechosos"))
        if bac_casos:
            qa["numero_de_casos_sospechosos_identificados_en_bac"] = _qa_val(bac_casos)
    elif bac == "NO":
        qa["se_realizo_busqueda_activa_comunitaria_de_casos_bac"] = _qa_val("2")

    # Vacunación de bloqueo
    if vac_bloqueo in ("SI", "SÍ"):
        qa["hubo_vacunacion_de_bloqueo"] = _qa_val("1")
    elif vac_bloqueo == "NO":
        qa["hubo_vacunacion_de_bloqueo"] = _qa_val("2")

    # Monitoreo rápido de vacunación
    if monitoreo in ("SI", "SÍ"):
        qa["se_realizo_monitoreo_rapido_de_vacunacion"] = _qa_val("1")
    elif monitoreo == "NO":
        qa["se_realizo_monitoreo_rapido_de_vacunacion"] = _qa_val("2")

    # Vacunación con barrido
    if vac_barrido in ("SI", "SÍ"):
        qa["hubo_vacunacion_con_barrido_documentado"] = _qa_val("1")
    elif vac_barrido == "NO":
        qa["hubo_vacunacion_con_barrido_documentado"] = _qa_val("2")

    # Placeholder: por_que_no_acciones_respuesta (empty when actions exist)
    if not has_any_action:
        qa["por_que_no_acciones_respuesta"] = [{}]
    else:
        qa["por_que_no_acciones_respuesta"] = [{}]

    # Vitamina A
    vitamina = _get(d, "vitamina_a").upper()
    vit_code = _VITAMINA_A_MAP.get(vitamina)
    if vit_code:
        qa["se_le_administro_vitamina_a"] = _qa_val(vit_code)
        if vit_code == "1":
            n_dosis_vit = _safe_int(_get(d, "vitamina_a_dosis"))
            if n_dosis_vit:
                qa["numero_de_dosis_de_vitamina_a_recibidas"] = _qa_val(n_dosis_vit)

    # ─── Sección 7: Clasificación ───────────────────────
    # Estado de clasificación
    clas_estado = _get(d, "clasificacion_caso").upper()
    if clas_estado in ("CLASIFICADO", "CONFIRMADO", "CONFIRMADO SARAMPIÓN", "CONFIRMADO SARAMPION",
                       "CONFIRMADO RUBÉOLA", "CONFIRMADO RUBEOLA", "DESCARTADO"):
        qa["clasificacion"] = _qa_val("CLASIFICADO")
        # Clasificación final solo se envía cuando está CLASIFICADO
        clas_final = _CLASIFICACION_FINAL_MAP.get(clas_estado)
        if clas_final:
            qa["clasificacion_final"] = _qa_val(clas_final)
    elif clas_estado in ("SOSPECHOSO", "PENDIENTE"):
        qa["clasificacion"] = _qa_val("2")
        clas_final = None  # No enviar clasificacion_final para pendientes
    else:
        clas_final = None

    # Criterio de confirmación (depende de sarampión vs rubéola)
    criterio_conf = _get(d, "criterio_confirmacion").upper()
    if clas_final == "1":  # Sarampión
        criterio_mapped = _CRITERIO_CONFIRMACION_SARAMPION_MAP.get(criterio_conf)
        if criterio_mapped:
            qa["criterio_de_confirmacion_sarampion"] = _qa_val(criterio_mapped)
    elif clas_final == "2":  # Rubéola
        criterio_mapped = _CRITERIO_CONFIRMACION_RUBEOLA_MAP.get(criterio_conf)
        if criterio_mapped:
            qa["criterio_de_confirmacion_rubeola"] = _qa_val(criterio_mapped)
    elif clas_final == "3":  # Descartado
        criterio_desc = _get(d, "criterio_descarte").upper()
        criterio_desc_mapped = _CRITERIO_DESCARTE_MAP.get(criterio_desc)
        if criterio_desc_mapped:
            qa["criterio_de_descarte"] = _qa_val(criterio_desc_mapped)

    # Contacto de otro caso
    contacto_otro = _get(d, "contacto_otro_caso").upper()
    if contacto_otro in ("SI", "SÍ"):
        qa["contacto_de_otro_caso"] = _qa_val("SI")
    else:
        qa["contacto_de_otro_caso"] = _qa_val("NO")

    # Fuente de infección (código numérico)
    fuente_inf = _get(d, "fuente_infeccion").upper()
    fuente_inf_code = _FUENTE_INFECCION_MAP.get(fuente_inf)
    if fuente_inf_code:
        qa["fuente_de_infeccion_de_los_casos_confirmados"] = _qa_val(fuente_inf_code)
        # Si importado, incluir país
        if fuente_inf_code == "1":
            pais_imp = _get(d, "pais_importacion")
            if pais_imp:
                qa["importado_pais_de_importacion"] = _qa_val(_godata_text(pais_imp))

    # Caso analizado por (multi-answer con códigos numéricos)
    analizado = _get(d, "caso_analizado_por").upper()
    if analizado:
        # Puede ser múltiple separado por comas
        items = [x.strip() for x in analizado.split(",") if x.strip()]
        codes = []
        for item in items:
            code = _CASO_ANALIZADO_MAP.get(item)
            if code:
                codes.append(code)
            elif item in ("1", "2", "3", "4"):
                codes.append(item)
        if codes:
            qa["caso_analizado_por"] = _qa_val(codes)

    # Fecha de clasificación
    fecha_clas = _to_iso_date(_get(d, "fecha_clasificacion_final") or _get(d, "fecha_clasificacion"))
    if fecha_clas:
        qa["fecha_de_clasificacion"] = _qa_val(fecha_clas)

    # Condición final del paciente (código numérico)
    condicion_final = _get(d, "condicion_final_paciente") or _get(d, "condicion_egreso")
    if condicion_final:
        cond_upper = condicion_final.upper()
        cond_code = _CONDICION_FINAL_MAP.get(cond_upper)
        if cond_code:
            qa["condicion_final_del_paciente"] = _qa_val(cond_code)
        elif cond_upper in ("1", "2", "3", "4"):
            qa["condicion_final_del_paciente"] = _qa_val(cond_upper)

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


# ═══════════════════════════════════════════════════════════
# VALIDACIÓN PRE-ENVÍO
# ═══════════════════════════════════════════════════════════

def validate_godata_payload(payload: dict) -> List[str]:
    """Valida un payload GoData antes de enviarlo. Retorna lista de advertencias.

    GoData tiene CERO validación server-side (acepta cualquier payload),
    por lo que la validación debe ser client-side.

    Args:
        payload: Dict generado por map_record_to_godata()

    Returns:
        Lista de strings con advertencias. Lista vacía = payload válido.
    """
    warnings = []

    # Campos obligatorios del modelo GoData (visibleAndMandatory en outbreak config)
    if not payload.get("firstName"):
        warnings.append("firstName vacio — se requiere nombre del paciente")
    if not payload.get("lastName"):
        warnings.append("lastName vacio — se requiere apellido del paciente")
    if not payload.get("dateOfReporting"):
        warnings.append("dateOfReporting vacio — se requiere fecha de notificacion")
    if not payload.get("dateOfOnset"):
        warnings.append("dateOfOnset vacio — se requiere fecha de inicio de sintomas")
    if not payload.get("gender"):
        warnings.append("gender vacio — se requiere sexo del paciente")

    # Campos estándar GoData que deben estar seteados
    classification = payload.get("classification", "")
    if not classification:
        warnings.append("classification vacio — GoData no podra filtrar/clasificar este caso")

    # Validar formato de fechas (deben ser YYYY-MM-DDT00:00:00.000Z)
    _DATE_FIELDS = ("dateOfReporting", "dateOfOnset", "dob", "dateOfOutcome")
    for field in _DATE_FIELDS:
        val = payload.get(field)
        if val and (not isinstance(val, str) or len(val) < 24 or "T" not in val or not val.endswith("Z")):
            warnings.append(f"{field} formato invalido: '{val}' — esperado YYYY-MM-DDT00:00:00.000Z")

    # Validar questionnaireAnswers
    qa = payload.get("questionnaireAnswers", {})
    if not qa:
        warnings.append("questionnaireAnswers vacio — no hay datos del cuestionario")
    else:
        # Detectar secciones vacías que no deberían enviarse solas
        empty_sections = [k for k, v in qa.items() if v == [{}] or v == [{"value": ""}]]
        if empty_sections:
            warnings.append(f"Secciones QA con valor vacio: {empty_sections}")

        # Campos requeridos en el cuestionario Guatemala
        if "fecha_de_inicio_de_exantema_rash_" not in qa:
            warnings.append("QA: fecha_de_inicio_de_exantema_rash_ faltante (requerido en template Guatemala)")
        if "paciente_vacunado_" not in qa:
            warnings.append("QA: paciente_vacunado_ faltante (requerido en template Guatemala)")
        if "direccion_de_area_de_salud" not in qa:
            warnings.append("QA: direccion_de_area_de_salud faltante (requerido en template Guatemala)")

    # Validar age
    age = payload.get("age", {})
    if age:
        years = age.get("years", 0)
        if isinstance(years, int) and years > 120:
            warnings.append(f"age.years={years} — posible dato invalido (>120 anios)")

    return warnings
