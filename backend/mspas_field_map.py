"""
Mapeo de campos IGSS -> MSPAS EPIWEB para Sarampion/Rubeola.

Convierte valores almacenados en nuestra BD (tabla `registros`, definida en
database.py COLUMNS) a los formatos esperados por el formulario MSPAS EPIWEB
(https://cne.mspas.gob.gt/epiweb/fichas/paginas/sar/sarampion_ingresar.php).

Referencia de campos MSPAS:
    vigilancia_activa/components/igss/inventario_campos_sarampion_mspas.py

Uso tipico:
    from mspas_field_map import map_record_to_mspas, parse_date

    record = fetch_record_from_db(registro_id)
    mspas = map_record_to_mspas(record)
    # mspas['cbox_genero'] -> '1' (Masculino) o '2' (Femenino)
    # mspas['fecha_not_dd'], mspas['fecha_not_mm'], mspas['fecha_not_yyyy']
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

# =============================================================================
# DEPARTAMENTO -> CODIGO MSPAS (22 departamentos + OTROS)
# Incluye variantes con y sin tilde para matching robusto.
# =============================================================================
DEPT_CODES: dict[str, str] = {
    "GUATEMALA": "1",
    "EL PROGRESO": "2",
    "SACATEPEQUEZ": "3",
    "SACATEPÉQUEZ": "3",
    "CHIMALTENANGO": "4",
    "ESCUINTLA": "5",
    "SANTA ROSA": "6",
    "SOLOLA": "7",
    "SOLOLÁ": "7",
    "TOTONICAPAN": "8",
    "TOTONICAPÁN": "8",
    "QUETZALTENANGO": "9",
    "SUCHITEPEQUEZ": "10",
    "SUCHITEPÉQUEZ": "10",
    "RETALHULEU": "11",
    "SAN MARCOS": "12",
    "HUEHUETENANGO": "13",
    "QUICHE": "14",
    "QUICHÉ": "14",
    "BAJA VERAPAZ": "15",
    "ALTA VERAPAZ": "16",
    "EL PETEN": "17",
    "PETÉN": "17",
    "EL PETÉN": "17",
    "PETEN": "17",
    "IZABAL": "18",
    "ZACAPA": "19",
    "CHIQUIMULA": "20",
    "JALAPA": "21",
    "JUTIAPA": "22",
    "OTROS": "99",
    "(OTROS)": "99",
}

# =============================================================================
# SEXO -> CODIGO MSPAS
# MSPAS select: 1=Masculino, 2=Femenino
# =============================================================================
SEX_CODES: dict[str, str] = {
    "M": "1",
    "MASCULINO": "1",
    "HOMBRE": "1",
    "F": "2",
    "FEMENINO": "2",
    "MUJER": "2",
}

# =============================================================================
# PUEBLO/ETNIA -> CODIGO MSPAS
# MSPAS select cbox_etnia: 7 opciones
# =============================================================================
ETNIA_CODES: dict[str, str] = {
    "Maya": "1",
    "MAYA": "1",
    "Ladino / Mestizo": "2",
    "Ladino": "2",
    "LADINO": "2",
    "Mestizo": "2",
    "MESTIZO": "2",
    "LADINO / MESTIZO": "2",
    "Garifuna": "3",
    "GARIFUNA": "3",
    "Garífuna": "3",
    "GARÍFUNA": "3",
    "Xinca": "4",
    "XINCA": "4",
    "Otros": "5",
    "OTROS": "5",
    "Extranjero": "6",
    "EXTRANJERO": "6",
    "Desconocido": "7",
    "DESCONOCIDO": "7",
    "NO INDICA": "7",
    "": "7",
}

# =============================================================================
# ESCOLARIDAD -> CODIGO MSPAS
# MSPAS select cbox_escolar: 17 opciones (value 1..17)
# Nota: El orden en el HTML es descendente (17=Postgrado arriba, 1=Univ Completa abajo)
# =============================================================================
ESCOLARIDAD_CODES: dict[str, str] = {
    "Universitaria Completa": "1",
    "UNIVERSITARIA COMPLETA": "1",
    "Unversitaria Completa": "1",  # Typo comun
    "Universitaria Incompleta": "2",
    "UNIVERSITARIA INCOMPLETA": "2",
    "Diversificado Completo": "3",
    "DIVERSIFICADO COMPLETO": "3",
    "Diversificado Incompleto": "4",
    "DIVERSIFICADO INCOMPLETO": "4",
    "Secundaria Completa": "5",
    "SECUNDARIA COMPLETA": "5",
    "Secundaria Incompleta": "6",
    "SECUNDARIA INCOMPLETA": "6",
    "Primaria Completa": "7",
    "PRIMARIA COMPLETA": "7",
    "Primaria Incompleta": "8",
    "PRIMARIA INCOMPLETA": "8",
    "Ninguna": "9",
    "NINGUNA": "9",
    "Primaria": "10",
    "PRIMARIA": "10",
    "Secundaria": "11",
    "SECUNDARIA": "11",
    "Diversificado": "12",
    "DIVERSIFICADO": "12",
    "Universitario": "13",
    "UNIVERSITARIO": "13",
    "Analfabeto": "14",
    "ANALFABETO": "14",
    "Alfabeto": "15",
    "ALFABETO": "15",
    "No aplica": "16",
    "NO APLICA": "16",
    "N/A": "16",
    "Postgrado": "17",
    "POSTGRADO": "17",
}

# =============================================================================
# FUENTE DE NOTIFICACION -> CODIGO MSPAS
# MSPAS select cb_fuente_noti: 7 opciones
# =============================================================================
FUENTE_NOTI_CODES: dict[str, str] = {
    "Pública": "1",
    "PUBLICA": "1",
    "PÚBLICA": "1",
    "Publica": "1",
    "Privada": "2",
    "PRIVADA": "2",
    "Laboratorio": "3",
    "LABORATORIO": "3",
    "Comunidad": "4",
    "COMUNIDAD": "4",
    "Búsqueda Activa": "5",
    "BUSQUEDA ACTIVA": "5",
    "BÚSQUEDA ACTIVA": "5",
    "Defunción": "6",
    "DEFUNCION": "6",
    "DEFUNCIÓN": "6",
    "Otra": "7",
    "OTRA": "7",
    "Otro": "7",
    "OTRO": "7",
}

# =============================================================================
# BUSQUEDA ACTIVA -> CODIGO MSPAS
# MSPAS select slc_activa: 3 opciones
# =============================================================================
BUSQUEDA_ACTIVA_CODES: dict[str, str] = {
    "Retrospectiva en el servicio": "1",
    "RETROSPECTIVA EN EL SERVICIO": "1",
    "Comunidad": "2",
    "COMUNIDAD": "2",
    "Otras": "3",
    "OTRAS": "3",
    "Otra": "3",
}

# =============================================================================
# SITIO INICIO ERUPCION -> CODIGO MSPAS
# MSPAS select cbox_erupciones: 5 opciones
# =============================================================================
ERUPCION_CODES: dict[str, str] = {
    "Retroauricular": "1",
    "RETROAURICULAR": "1",
    "Cara": "2",
    "CARA": "2",
    "Cuello": "3",
    "CUELLO": "3",
    "Tórax": "4",
    "TORAX": "4",
    "TÓRAX": "4",
    "Torax": "4",
    "Otro": "5",
    "OTRO": "5",
    "Otra": "5",
}

# =============================================================================
# FUENTE INFORMACION VACUNA -> CODIGO MSPAS
# MSPAS select cb_fuente: 4 opciones
# =============================================================================
FUENTE_VACUNA_CODES: dict[str, str] = {
    "En carné": "1",
    "EN CARNÉ": "1",
    "Carné": "1",
    "CARNÉ": "1",
    "CARNE": "1",
    "En SIGSA 5a": "2",
    "EN SIGSA 5A": "2",
    "SIGSA 5a": "2",
    "SIGSA 5A": "2",
    "En cuadernillos": "3",
    "EN CUADERNILLOS": "3",
    "Cuadernillos": "3",
    "CUADERNILLOS": "3",
    "Cuadernillo": "3",
    "CUADERNILLO": "3",
    "Verbal": "4",
    "VERBAL": "4",
}

# =============================================================================
# TIPO VACUNA -> CODIGO MSPAS
# MSPAS select cb_vacuna: 5 opciones
# =============================================================================
VACUNA_TIPO_CODES: dict[str, str] = {
    "Antisarampinosa": "1",
    "ANTISARAMPINOSA": "1",
    "Antirubeólica": "2",
    "ANTIRUBEÓLICA": "2",
    "ANTIRUBÉOLICA": "2",
    "Antirubéolica": "2",
    "ANTIRUBEOLICA": "2",
    "SR Sarampión Rubéola": "3",
    "SR SARAMPIÓN RUBÉOLA": "3",
    "SR SARAMPION RUBEOLA": "3",
    "SR": "3",
    "SRP Sarampión Rubéola Paperas": "4",
    "SRP SARAMPIÓN RUBÉOLA PAPERAS": "4",
    "SRP SARAMPION RUBEOLA PAPERAS": "4",
    "SRP": "4",
    "No recuerda": "5",
    "NO RECUERDA": "5",
}

# =============================================================================
# NUMERO DE DOSIS -> CODIGO MSPAS
# MSPAS select no_dosis: 5 opciones
# =============================================================================
DOSIS_CODES: dict[str, str] = {
    "1 dosis": "1",
    "1": "1",
    "1 DOSIS": "1",
    "2 dosis": "2",
    "2": "2",
    "2 DOSIS": "2",
    "3 dosis": "3",
    "3": "3",
    "3 DOSIS": "3",
    "Más de 3 dosis": "4",
    "MÁS DE 3 DOSIS": "4",
    "MAS DE 3 DOSIS": "4",
    "4": "4",
    "No recuerda": "5",
    "NO RECUERDA": "5",
}

# =============================================================================
# CONDICION EGRESO -> CODIGO MSPAS
# MSPAS select cb_egreso_condicion: 3 opciones
# =============================================================================
EGRESO_CODES: dict[str, str] = {
    "Mejorado": "1",
    "MEJORADO": "1",
    "Grave": "2",
    "GRAVE": "2",
    "Muerto": "3",
    "MUERTO": "3",
    "Fallecido": "3",
    "FALLECIDO": "3",
}

# =============================================================================
# ANTIGENO -> CODIGO MSPAS
# MSPAS select slc_antigeno: 4 opciones
# =============================================================================
ANTIGENO_CODES: dict[str, str] = {
    "Sarampión": "1",
    "SARAMPIÓN": "1",
    "SARAMPION": "1",
    "Rubéola": "2",
    "RUBÉOLA": "2",
    "RUBEOLA": "2",
    "Rubeola": "2",
    "Dengue": "3",
    "DENGUE": "3",
    "Otros": "4",
    "OTROS": "4",
    "Otro": "4",
}

# =============================================================================
# RESULTADO LABORATORIO -> CODIGO MSPAS
# MSPAS select slc_resul_lab: 4 opciones
# =============================================================================
RESULTADO_CODES: dict[str, str] = {
    "Negativo": "1",
    "NEGATIVO": "1",
    "NEG": "1",
    "Positivo": "2",
    "POSITIVO": "2",
    "POS": "2",
    "Muestra Inadecuada": "3",
    "MUESTRA INADECUADA": "3",
    "Indeterminada": "4",
    "INDETERMINADA": "4",
    "IND": "4",
}

# =============================================================================
# CLASIFICACION FINAL -> CODIGO MSPAS
# MSPAS select slc_clas_final: 3 opciones
# =============================================================================
CLASIFICACION_FINAL_CODES: dict[str, str] = {
    "Sarampión": "1",
    "SARAMPIÓN": "1",
    "SARAMPION": "1",
    "Rubéola": "2",
    "RUBÉOLA": "2",
    "RUBEOLA": "2",
    "Descartado": "3",
    "DESCARTADO": "3",
}

# =============================================================================
# CONFIRMADO POR -> CODIGO MSPAS
# MSPAS select slc_confirmado (condicional: clasificacion = 1 o 2)
# =============================================================================
CONFIRMADO_POR_CODES: dict[str, str] = {
    "Laboratorio": "1",
    "LABORATORIO": "1",
    "Nexo Epidemiológico": "2",
    "NEXO EPIDEMIOLÓGICO": "2",
    "NEXO EPIDEMIOLOGICO": "2",
    "Diagnóstico Clínico": "3",
    "DIAGNÓSTICO CLÍNICO": "3",
    "DIAGNOSTICO CLINICO": "3",
}

# =============================================================================
# FUENTE DE INFECCION -> CODIGO MSPAS
# MSPAS select slc_fuente_infect (condicional: clasificacion = 1 o 2)
# =============================================================================
FUENTE_INFECCION_CODES: dict[str, str] = {
    "Importado": "1",
    "IMPORTADO": "1",
    "Relacionado con Importación": "2",
    "RELACIONADO CON IMPORTACIÓN": "2",
    "RELACIONADO CON IMPORTACION": "2",
    "Desconocido": "3",
    "DESCONOCIDO": "3",
    "Autóctono": "4",
    "AUTÓCTONO": "4",
    "AUTOCTONO": "4",
}

# =============================================================================
# CRITERIO PARA DESCARTAR -> CODIGO MSPAS
# MSPAS select slc_crit_desc (condicional: clasificacion = 3)
# =============================================================================
CRITERIO_DESCARTE_CODES: dict[str, str] = {
    "Sarampión/Rubéola IgM-Neg": "1",
    "SARAMPIÓN/RUBÉOLA IGM-NEG": "1",
    "SARAMPION/RUBEOLA IGM-NEG": "1",
    "IgM Negativo": "1",
    "Reacción Vacunal": "2",
    "REACCIÓN VACUNAL": "2",
    "REACCION VACUNAL": "2",
    "Dengue": "3",
    "DENGUE": "3",
    "Parvovirus B19": "4",
    "PARVOVIRUS B19": "4",
    "Herpes": "5",
    "HERPES": "5",
    "Reacción Alérgica": "6",
    "REACCIÓN ALÉRGICA": "6",
    "REACCION ALERGICA": "6",
    "Otro Diagnóstico": "7",
    "OTRO DIAGNÓSTICO": "7",
    "OTRO DIAGNOSTICO": "7",
}

# =============================================================================
# RADIO SI/NO -> VALORES MSPAS
# Los radio buttons en MSPAS usan value="SI" / value="NO"
# Nuestra BD puede tener variantes.
# =============================================================================
SI_NO_MAP: dict[str, str] = {
    "SI": "SI",
    "SÍ": "SI",
    "Sí": "SI",
    "Si": "SI",
    "si": "SI",
    "YES": "SI",
    "1": "SI",
    "True": "SI",
    "true": "SI",
    "NO": "NO",
    "No": "NO",
    "no": "NO",
    "0": "NO",
    "False": "NO",
    "false": "NO",
    "": "NO",
}


# =============================================================================
# OCUPACION: ESTRATEGIA DE BUSQUEDA POR TEXTO PARCIAL
# =============================================================================
# MSPAS tiene 441 ocupaciones (catalogo CIUO-08). El select cbox_ocup
# tiene demasiadas opciones para mapear exhaustivamente.
# Estrategia: usar texto parcial para buscar en el <select>.
#
# Patron en Playwright:
#   await page.selectOption('#cbox_ocup',
#       { label: texto } )  // match parcial
# O si no funciona con selectOption, iterar opciones:
#   const options = await page.$$eval('#cbox_ocup option',
#       (opts, search) => opts
#           .filter(o => o.text.toUpperCase().includes(search))
#           .map(o => o.value),
#       occupation_text.upper()
#   );
#   if (options.length > 0) await page.selectOption('#cbox_ocup', options[0]);

# Mapeo de texto comun IGSS -> termino de busqueda MSPAS
OCUPACION_SEARCH_TERMS: dict[str, str] = {
    # Salud
    "MEDICO": "MEDICO",
    "MÉDICO": "MEDICO",
    "ENFERMERA": "ENFERMERO",
    "ENFERMERO": "ENFERMERO",
    "AUXILIAR DE ENFERMERIA": "AUXILIAR DE ENFERMERIA",
    "DOCTOR": "MEDICO",
    # Administrativo
    "SECRETARIA": "SECRETARIO",
    "OFICINISTA": "OFICINISTA",
    "CONTADOR": "CONTADOR",
    "CONTADORA": "CONTADOR",
    "ADMINISTRADOR": "DIRECTOR ADMINISTR",
    # Operativo
    "OPERARIO": "OPERADOR",
    "OBRERO": "OBRERO",
    "TECNICO": "TECNICO",
    "TÉCNICO": "TECNICO",
    "MECANICO": "MECANICO",
    "MECÁNICO": "MECANICO",
    "ELECTRICISTA": "ELECTRICISTA",
    "ALBAÑIL": "ALBAÑIL",
    "ALBANIL": "ALBAÑIL",
    "CONSERJE": "CONSERJE",
    "PILOTO": "CONDUCTOR",
    "CHOFER": "CONDUCTOR",
    # Profesional
    "ABOGADO": "ABOGADO",
    "INGENIERO": "INGENIERO",
    "ARQUITECTO": "ARQUITECTO",
    "MAESTRO": "MAESTRO",
    "PROFESOR": "PROFESOR",
    "DOCENTE": "PROFESOR",
    # Comercio/Servicios
    "VENDEDOR": "VENDEDOR",
    "COCINERO": "COCINERO",
    "COCINERA": "COCINERO",
    "GUARDIA": "GUARDIA",
    "VIGILANTE": "GUARDIA",
    # Hogar
    "AMA DE CASA": "AMA DE CASA",
    "DOMESTICA": "TRABAJADOR DOMESTICO",
    "DOMÉSTICA": "TRABAJADOR DOMESTICO",
    # General
    "ESTUDIANTE": "ESTUDIANTE",
    "JUBILADO": "JUBILADO",
    "PENSIONADO": "JUBILADO",
    "DESEMPLEADO": "DESEMPLEADO",
    "MENOR": "MENOR",
    "NINGUNA": "NO APLICA",
}


def get_centro_search_text(unidad_medica: str) -> str:
    """Extract key search terms from IGSS unit name for MSPAS Centro Externo dropdown.

    MSPAS uses format like: 'IGSS Quetzaltenango, Hospital Quetzaltenango'
    Our format: 'HOSPITAL QUETZALTENANGO, QUETZALTENANGO'

    We extract the most distinctive part (usually the location name after
    removing generic prefixes like HOSPITAL/CONSULTORIO and department suffixes).

    Args:
        unidad_medica: IGSS unit name as stored in our DB.

    Returns:
        Short search text for partial matching in the MSPAS dropdown.

    Examples:
        >>> get_centro_search_text('HOSPITAL QUETZALTENANGO, QUETZALTENANGO')
        'QUETZALTENANGO'
        >>> get_centro_search_text('CONSULTORIO DE VILLA NUEVA, GUATEMALA')
        'VILLA NUEVA'
        >>> get_centro_search_text('')
        ''
    """
    if not unidad_medica:
        return ''
    text = str(unidad_medica).strip().upper()
    if not text:
        return ''
    # Strip leading "ANEXO DEL IGSS" or "IGSS" before checking unit type
    for leading in ['ANEXO DEL IGSS ', 'ANEXO IGSS ', 'IGSS ']:
        if text.startswith(leading):
            text = text[len(leading):]
            break
    # Remove common unit type prefixes
    for prefix in ['HOSPITAL GENERAL DE ENFERMEDADES ',
                   'HOSPITAL GENERAL DE ACCIDENTES ',
                   'HOSPITAL GENERAL DE ',
                   'HOSPITAL DE GINECO OBSTETRICIA ',
                   'HOSPITAL DE ',
                   'HOSPITAL ',
                   'CONSULTORIO DE ',
                   'CONSULTORIO ',
                   'CLINICA DE ',
                   'CLINICA ',
                   'UNIDAD PERIFERICA ',
                   'UNIDAD ',
                   'CENTRO DE ATENCION INTEGRAL ',
                   'CENTRO DE ATENCION ',
                   'CENTRO ']:
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    # Remove department suffix after comma (e.g. ", QUETZALTENANGO")
    if ',' in text:
        text = text.split(',')[0].strip()
    # If still too long, take just the first meaningful word(s)
    # (enough for partial matching)
    return text


def get_occupation_search_text(occupation: str) -> str:
    """Devuelve el termino de busqueda para encontrar la ocupacion en el select MSPAS.

    Si existe un mapeo directo, lo usa. Si no, devuelve el texto original
    en mayusculas (para busqueda parcial en las 441 opciones).

    Args:
        occupation: Texto de ocupacion tal como esta en la BD IGSS.

    Returns:
        Texto para buscar en el select cbox_ocup de MSPAS.
    """
    if not occupation:
        return ""
    occupation = str(occupation).strip()
    upper = occupation.upper()
    # Buscar match exacto primero
    if upper in OCUPACION_SEARCH_TERMS:
        return OCUPACION_SEARCH_TERMS[upper]
    if occupation in OCUPACION_SEARCH_TERMS:
        return OCUPACION_SEARCH_TERMS[occupation]
    # Buscar match parcial en las claves
    for key, search_term in OCUPACION_SEARCH_TERMS.items():
        if key in upper or upper in key:
            return search_term
    # Fallback: devolver el texto original limpio para busqueda directa
    return upper


# =============================================================================
# FUNCIONES DE CONVERSION
# =============================================================================

def parse_date(date_str: Optional[str]) -> tuple[str, str, str]:
    """Descompone un string de fecha en (dd, mm, yyyy).

    MSPAS espera fechas como inputs separados o en formato dd/mm/yyyy
    con datepicker jQuery. Esta funcion extrae los componentes.

    Formatos soportados:
        - YYYY-MM-DD (ISO, formato SQLite)
        - YYYY-MM-DD HH:MM:SS (ISO con hora)
        - DD/MM/YYYY (formato display Guatemala)
        - datetime.date / datetime.datetime objects

    Args:
        date_str: Fecha como string o None.

    Returns:
        Tupla (dd, mm, yyyy) como strings. ('', '', '') si no se puede parsear.

    Examples:
        >>> parse_date('2026-03-15')
        ('15', '03', '2026')
        >>> parse_date('15/03/2026')
        ('15', '03', '2026')
        >>> parse_date(None)
        ('', '', '')
    """
    if not date_str:
        return ("", "", "")

    # Handle datetime objects
    if isinstance(date_str, (date, datetime)):
        return (
            str(date_str.day).zfill(2),
            str(date_str.month).zfill(2),
            str(date_str.year),
        )

    date_str = str(date_str).strip()
    if not date_str:
        return ("", "", "")

    def _validate_date_parts(dd: str, mm: str, yyyy: str) -> tuple[str, str, str]:
        """Validate that month is 1-12 and day is 1-31. Returns ('','','') if invalid."""
        try:
            mm_int = int(mm)
            dd_int = int(dd)
            if not (1 <= mm_int <= 12 and 1 <= dd_int <= 31):
                return ('', '', '')
        except ValueError:
            return ('', '', '')
        return (dd.zfill(2), mm.zfill(2), yyyy)

    # YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    if len(date_str) >= 10 and date_str[4] == "-":
        parts = date_str[:10].split("-")
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            yyyy, mm, dd = parts
            return _validate_date_parts(dd, mm, yyyy)

    # DD/MM/YYYY
    if "/" in date_str:
        parts = date_str.split("/")
        if len(parts) == 3 and all(p.strip().isdigit() for p in parts):
            dd, mm, yyyy = [p.strip() for p in parts]
            return _validate_date_parts(dd, mm, yyyy)

    # DD-MM-YYYY (alternate separator)
    if date_str.count("-") == 2 and len(date_str) <= 10:
        parts = date_str.split("-")
        if len(parts) == 3:
            # Distinguish from YYYY-MM-DD by checking first part length
            if len(parts[0]) == 2:
                dd, mm, yyyy = parts
                return _validate_date_parts(dd, mm, yyyy)

    return ("", "", "")


def format_date_mspas(date_str: Optional[str]) -> str:
    """Formatea una fecha al formato DD/MM/YYYY esperado por datepickers MSPAS.

    Args:
        date_str: Fecha en cualquier formato soportado por parse_date.

    Returns:
        String en formato DD/MM/YYYY, o '' si no se puede parsear.

    Examples:
        >>> format_date_mspas('2026-03-15')
        '15/03/2026'
        >>> format_date_mspas(None)
        ''
    """
    dd, mm, yyyy = parse_date(date_str)
    if dd and mm and yyyy:
        return f"{dd}/{mm}/{yyyy}"
    return ""


def get_code(mapping: dict[str, str], value: Optional[str], default: str = "") -> str:
    """Busca un codigo en un diccionario de mapeo, case-insensitive con fallback.

    Args:
        mapping: Diccionario de texto -> codigo MSPAS.
        value: Valor de la BD IGSS.
        default: Valor por defecto si no se encuentra.

    Returns:
        Codigo MSPAS o default.

    Examples:
        >>> get_code(SEX_CODES, 'M')
        '1'
        >>> get_code(SEX_CODES, 'masculino')
        '1'
        >>> get_code(SEX_CODES, None)
        ''
    """
    if not value:
        return default
    value = str(value).strip()
    if not value:
        return default
    # Match exacto
    if value in mapping:
        return mapping[value]
    # Match case-insensitive
    upper = value.upper()
    for k, v in mapping.items():
        if k.upper() == upper:
            return v
    return default


def normalize_si_no(value: Optional[str]) -> str:
    """Normaliza valores booleanos al formato SI/NO de MSPAS.

    Args:
        value: Texto de la BD (SI, No, 1, True, etc.)

    Returns:
        'SI' o 'NO'
    """
    if not value:
        return "NO"
    return SI_NO_MAP.get(str(value).strip(), "NO")


# =============================================================================
# MAPEO COMPLETO: REGISTRO IGSS -> CAMPOS MSPAS
# =============================================================================
# Nomenclatura de campos MSPAS tomada de inventario_campos_sarampion_mspas.py
# Los campos de nuestra BD estan en database.py COLUMNS

def map_record_to_mspas(record: dict) -> dict:
    """Convierte un registro de la BD IGSS a valores para el formulario MSPAS EPIWEB.

    Toma un dict con claves correspondientes a las columnas de la tabla `registros`
    (ver database.py COLUMNS) y devuelve un dict con claves correspondientes a los
    name= de los inputs HTML del formulario MSPAS.

    Args:
        record: Dict con datos del registro. Claves = columnas de BD IGSS.

    Returns:
        Dict con claves = name del input MSPAS, valores = strings listos para
        inyectar en el formulario. Incluye claves auxiliares con sufijo
        _dd/_mm/_yyyy para fechas descompuestas y _search para selects dinamicos.
    """
    def g(key: str, default: str = "") -> str:
        """Extrae un valor del record, limpio y como string."""
        val = record.get(key)
        if val is None:
            return default
        return str(val).strip() or default

    mapped: dict[str, str] = {}

    # -----------------------------------------------------------------
    # TAB 1: DATOS GENERALES — Unidad Notificadora
    # -----------------------------------------------------------------
    mapped["fecha_not"] = format_date_mspas(g("fecha_notificacion"))
    dd, mm, yyyy = parse_date(g("fecha_notificacion"))
    mapped["fecha_not_dd"] = dd
    mapped["fecha_not_mm"] = mm
    mapped["fecha_not_yyyy"] = yyyy

    # cbox_centroP: select con 122 opciones de centros/unidades.
    # Necesita match parcial — la unidad IGSS no siempre coincide exactamente.
    mapped["cbox_centroP"] = g("unidad_medica")
    mapped["cbox_centroP_search"] = g("unidad_medica")

    mapped["nom_responsable"] = g("nom_responsable")
    mapped["cargo_responsable"] = g("cargo_responsable")
    mapped["tel_responsable"] = g("telefono_responsable")

    # -----------------------------------------------------------------
    # TAB 2: DATOS DEL PACIENTE
    # -----------------------------------------------------------------
    mapped["nombres"] = g("nombres")
    mapped["apellidos"] = g("apellidos")
    mapped["cbox_genero"] = get_code(SEX_CODES, g("sexo"))

    # Campos condicionales: embarazo (solo si sexo = Femenino = '2')
    mapped["rad_embarazada"] = normalize_si_no(g("esta_embarazada"))
    mapped["rad_lactando"] = normalize_si_no(g("lactando"))
    mapped["txt_sem_emb"] = g("semanas_embarazo")

    mapped["cbox_etnia"] = get_code(ETNIA_CODES, g("pueblo_etnia"))

    # Ocupacion: busqueda por texto parcial (441 opciones en MSPAS)
    mapped["cbox_ocup"] = get_occupation_search_text(g("ocupacion"))
    mapped["cbox_ocup_search"] = get_occupation_search_text(g("ocupacion"))

    mapped["cbox_escolar"] = get_code(ESCOLARIDAD_CODES, g("escolaridad"))

    # Residencia
    mapped["cbox_iddep"] = get_code(DEPT_CODES, g("departamento_residencia"))
    # Municipio y poblado: selects dinamicos cargados por AJAX tras seleccionar depto.
    # Guardamos el texto para busqueda posterior.
    mapped["cbox_idmun_search"] = g("municipio_residencia")
    mapped["cbox_idlp_search"] = g("poblado")
    mapped["p_dir"] = g("direccion_exacta")

    # Fecha de nacimiento
    mapped["fecha_nac"] = format_date_mspas(g("fecha_nacimiento"))
    dd, mm, yyyy = parse_date(g("fecha_nacimiento"))
    mapped["fecha_nac_dd"] = dd
    mapped["fecha_nac_mm"] = mm
    mapped["fecha_nac_yyyy"] = yyyy

    # Edad (auto-calculada en MSPAS pero podemos pre-llenar)
    mapped["txt_anios"] = g("edad_anios")
    mapped["txt_meses"] = g("edad_meses")
    mapped["txt_dias"] = g("edad_dias")

    mapped["nombre_madre"] = g("nombre_encargado")

    # -----------------------------------------------------------------
    # TAB 3: INFORMACION CLINICA — Conocimiento del Caso
    # -----------------------------------------------------------------
    mapped["fecha_ini_sint"] = format_date_mspas(g("fecha_inicio_sintomas"))
    dd, mm, yyyy = parse_date(g("fecha_inicio_sintomas"))
    mapped["fecha_ini_sint_dd"] = dd
    mapped["fecha_ini_sint_mm"] = mm
    mapped["fecha_ini_sint_yyyy"] = yyyy

    mapped["fecha_captacion"] = format_date_mspas(g("fecha_captacion"))
    mapped["cb_fuente_noti"] = get_code(FUENTE_NOTI_CODES, g("fuente_notificacion"))
    mapped["fuente_otros"] = g("fuente_notificacion_otra")

    mapped["fecha_domiciliaria"] = format_date_mspas(g("fecha_visita_domiciliaria"))
    mapped["fecha_investigacion"] = format_date_mspas(g("fecha_inicio_investigacion"))
    mapped["slc_activa"] = get_code(BUSQUEDA_ACTIVA_CODES, g("busqueda_activa"))
    mapped["txt_activa_otros"] = g("busqueda_activa_otra")

    # Circunstancias de Exposicion
    mapped["txt_fecha_erupcion"] = format_date_mspas(g("fecha_inicio_erupcion"))
    mapped["cbox_erupciones"] = get_code(ERUPCION_CODES, g("sitio_inicio_erupcion"))
    mapped["txt_otra_erup"] = g("sitio_inicio_erupcion_otro")
    mapped["txt_fecha_fiebre"] = format_date_mspas(g("fecha_inicio_fiebre"))
    temp = g("temperatura_celsius")
    if temp:
        temp = temp.replace(',', '.')
    mapped["txt_temperatura"] = temp

    # Signos y Sintomas (radio SI/NO)
    mapped["tos"] = normalize_si_no(g("signo_tos"))
    mapped["coriza"] = normalize_si_no(g("signo_coriza"))
    mapped["conjuntivitis"] = normalize_si_no(g("signo_conjuntivitis"))
    mapped["adenopatias"] = normalize_si_no(g("signo_adenopatias"))
    mapped["artralgia"] = normalize_si_no(g("signo_artralgia"))

    # Vacunacion
    mapped["vacunado"] = normalize_si_no(g("vacunado"))
    mapped["cb_fuente"] = get_code(FUENTE_VACUNA_CODES, g("fuente_info_vacuna"))
    mapped["cb_vacuna"] = get_code(VACUNA_TIPO_CODES, g("tipo_vacuna"))
    mapped["no_dosis"] = get_code(DOSIS_CODES, g("numero_dosis_spr"))
    mapped["fecha_ult_dosis"] = format_date_mspas(g("fecha_ultima_dosis"))
    mapped["observaciones"] = g("observaciones_vacuna")

    # Hospitalizacion y Defuncion
    mapped["hospitalizacion"] = normalize_si_no(g("hospitalizado"))
    mapped["hosp_nombre"] = g("hosp_nombre")
    mapped["hosp_fecha"] = format_date_mspas(g("hosp_fecha"))
    mapped["hosp_reg_med"] = g("no_registro_medico")
    mapped["cb_egreso_condicion"] = get_code(EGRESO_CODES, g("condicion_egreso"))
    mapped["egreso_fecha"] = format_date_mspas(g("fecha_egreso"))
    mapped["txt_fecha_defuncion"] = format_date_mspas(g("fecha_defuncion"))
    mapped["txt_medic_defuncion"] = g("medico_certifica_defuncion")

    # -----------------------------------------------------------------
    # TAB 4: FACTORES DE RIESGO
    # -----------------------------------------------------------------
    mapped["rad_contacto"] = normalize_si_no(g("contacto_sospechoso_7_23"))
    mapped["rad_casos"] = normalize_si_no(g("caso_sospechoso_comunidad_3m"))
    mapped["rad_viajo"] = normalize_si_no(g("viajo_7_23_previo"))
    mapped["txt_donde_viajo"] = g("destino_viaje")
    mapped["rad_enfermo"] = normalize_si_no(g("contacto_enfermo_catarro"))
    mapped["rad_cont_emb"] = normalize_si_no(g("contacto_embarazada"))

    # -----------------------------------------------------------------
    # TAB 5: LABORATORIO
    # -----------------------------------------------------------------
    mapped["pick_muestra"] = normalize_si_no(g("recolecto_muestra"))

    # Checkboxes de tipo de muestra + fechas
    mapped["chk_suero"] = "1" if normalize_si_no(g("muestra_suero")) == "SI" else ""
    mapped["fecha_suero"] = format_date_mspas(g("muestra_suero_fecha"))
    mapped["chk_HN"] = "1" if normalize_si_no(g("muestra_hisopado")) == "SI" else ""
    mapped["fecha_HN"] = format_date_mspas(g("muestra_hisopado_fecha"))
    mapped["chk_orina"] = "1" if normalize_si_no(g("muestra_orina")) == "SI" else ""
    mapped["fecha_orina"] = format_date_mspas(g("muestra_orina_fecha"))
    mapped["chk_otra_m"] = "1" if normalize_si_no(g("muestra_otra")) == "SI" else ""
    mapped["txt_otra_muestra"] = g("muestra_otra_descripcion")
    mapped["fecha_otra_m"] = format_date_mspas(g("muestra_otra_fecha"))

    # Resultados de laboratorio
    mapped["slc_antigeno"] = get_code(ANTIGENO_CODES, g("antigeno_prueba"))
    mapped["txt_otro_ant"] = g("antigeno_otro")
    mapped["slc_resul_lab"] = get_code(RESULTADO_CODES, g("resultado_prueba"))
    mapped["fecha_recep"] = format_date_mspas(g("fecha_recepcion_laboratorio"))
    mapped["fecha_resul_lab"] = format_date_mspas(g("fecha_resultado_laboratorio"))

    # -----------------------------------------------------------------
    # TAB 6: CLASIFICACION FINAL
    # -----------------------------------------------------------------
    mapped["slc_clas_final"] = get_code(CLASIFICACION_FINAL_CODES, g("clasificacion_caso"))
    mapped["txt_fecha_final"] = format_date_mspas(g("fecha_clasificacion_final"))
    mapped["txt_nom_resp_clas"] = g("responsable_clasificacion")
    mapped["observaciones_clas"] = g("observaciones")

    return mapped


# =============================================================================
# MAPEO INVERSO: CAMPO MSPAS -> COLUMNA BD IGSS (referencia)
# =============================================================================
# Util para documentacion y debugging. No se usa en logica de llenado.
MSPAS_TO_IGSS_COLUMN: dict[str, str] = {
    # Tab 1
    "fecha_not": "fecha_notificacion",
    "cbox_centroP": "unidad_medica",
    "nom_responsable": "nom_responsable",
    "cargo_responsable": "cargo_responsable",
    "tel_responsable": "telefono_responsable",
    # Tab 2
    "nombres": "nombres",
    "apellidos": "apellidos",
    "cbox_genero": "sexo",
    "rad_embarazada": "esta_embarazada",
    "rad_lactando": "lactando",
    "txt_sem_emb": "semanas_embarazo",
    "cbox_etnia": "pueblo_etnia",
    "cbox_ocup": "ocupacion",
    "cbox_escolar": "escolaridad",
    "cbox_iddep": "departamento_residencia",
    "cbox_idmun": "municipio_residencia",
    "cbox_idlp": "poblado",
    "p_dir": "direccion_exacta",
    "fecha_nac": "fecha_nacimiento",
    "txt_anios": "edad_anios",
    "txt_meses": "edad_meses",
    "txt_dias": "edad_dias",
    "nombre_madre": "nombre_encargado",
    # Tab 3
    "fecha_ini_sint": "fecha_inicio_sintomas",
    "fecha_captacion": "fecha_captacion",
    "cb_fuente_noti": "fuente_notificacion",
    "fuente_otros": "fuente_notificacion_otra",
    "fecha_domiciliaria": "fecha_visita_domiciliaria",
    "fecha_investigacion": "fecha_inicio_investigacion",
    "slc_activa": "busqueda_activa",
    "txt_activa_otros": "busqueda_activa_otra",
    "txt_fecha_erupcion": "fecha_inicio_erupcion",
    "cbox_erupciones": "sitio_inicio_erupcion",
    "txt_otra_erup": "sitio_inicio_erupcion_otro",
    "txt_fecha_fiebre": "fecha_inicio_fiebre",
    "txt_temperatura": "temperatura_celsius",
    "tos": "signo_tos",
    "coriza": "signo_coriza",
    "conjuntivitis": "signo_conjuntivitis",
    "adenopatias": "signo_adenopatias",
    "artralgia": "signo_artralgia",
    "vacunado": "vacunado",
    "cb_fuente": "fuente_info_vacuna",
    "cb_vacuna": "tipo_vacuna",
    "no_dosis": "numero_dosis_spr",
    "fecha_ult_dosis": "fecha_ultima_dosis",
    "observaciones": "observaciones_vacuna",
    "hospitalizacion": "hospitalizado",
    "hosp_nombre": "hosp_nombre",
    "hosp_fecha": "hosp_fecha",
    "hosp_reg_med": "no_registro_medico",
    "cb_egreso_condicion": "condicion_egreso",
    "egreso_fecha": "fecha_egreso",
    "txt_fecha_defuncion": "fecha_defuncion",
    "txt_medic_defuncion": "medico_certifica_defuncion",
    # Tab 4
    "rad_contacto": "contacto_sospechoso_7_23",
    "rad_casos": "caso_sospechoso_comunidad_3m",
    "rad_viajo": "viajo_7_23_previo",
    "txt_donde_viajo": "destino_viaje",
    "rad_enfermo": "contacto_enfermo_catarro",
    "rad_cont_emb": "contacto_embarazada",
    # Tab 5
    "pick_muestra": "recolecto_muestra",
    "chk_suero": "muestra_suero",
    "fecha_suero": "muestra_suero_fecha",
    "chk_HN": "muestra_hisopado",
    "fecha_HN": "muestra_hisopado_fecha",
    "chk_orina": "muestra_orina",
    "fecha_orina": "muestra_orina_fecha",
    "chk_otra_m": "muestra_otra",
    "txt_otra_muestra": "muestra_otra_descripcion",
    "fecha_otra_m": "muestra_otra_fecha",
    "slc_antigeno": "antigeno_prueba",
    "txt_otro_ant": "antigeno_otro",
    "slc_resul_lab": "resultado_prueba",
    "fecha_recep": "fecha_recepcion_laboratorio",
    "fecha_resul_lab": "fecha_resultado_laboratorio",
    # Tab 6
    "slc_clas_final": "clasificacion_caso",
    "txt_fecha_final": "fecha_clasificacion_final",
    "txt_nom_resp_clas": "responsable_clasificacion",
    "observaciones_clas": "observaciones",
}


# =============================================================================
# TEST / DEMO
# =============================================================================

def test_mapping():
    """Demuestra el mapeo con un registro de ejemplo representativo.

    Ejecutar: python mspas_field_map.py
    """
    sample_record = {
        # Tab 1
        "fecha_notificacion": "2026-03-15",
        "unidad_medica": "IGSS Guatemala, Hospital General de Enfermedades zona 9",
        "nom_responsable": "Dr. Juan Perez",
        "cargo_responsable": "Epidemiologo de Unidad",
        "telefono_responsable": "2412-1224",
        # Tab 2
        "nombres": "Maria Isabel",
        "apellidos": "Lopez Garcia",
        "sexo": "F",
        "esta_embarazada": "NO",
        "lactando": "NO",
        "semanas_embarazo": "",
        "pueblo_etnia": "Ladino",
        "ocupacion": "SECRETARIA",
        "escolaridad": "Diversificado Completo",
        "departamento_residencia": "GUATEMALA",
        "municipio_residencia": "Guatemala",
        "poblado": "Zona 9",
        "direccion_exacta": "12 calle 10-45 zona 9",
        "fecha_nacimiento": "1990-07-22",
        "edad_anios": "35",
        "edad_meses": "8",
        "edad_dias": "0",
        "nombre_encargado": "",
        # Tab 3
        "fecha_inicio_sintomas": "2026-03-10",
        "fecha_captacion": "2026-03-12",
        "fuente_notificacion": "Pública",
        "fuente_notificacion_otra": "",
        "fecha_visita_domiciliaria": "",
        "fecha_inicio_investigacion": "2026-03-13",
        "busqueda_activa": "Retrospectiva en el servicio",
        "busqueda_activa_otra": "",
        "fecha_inicio_erupcion": "2026-03-09",
        "sitio_inicio_erupcion": "Cara",
        "sitio_inicio_erupcion_otro": "",
        "fecha_inicio_fiebre": "2026-03-08",
        "temperatura_celsius": "38.5",
        "signo_tos": "SI",
        "signo_coriza": "SI",
        "signo_conjuntivitis": "NO",
        "signo_adenopatias": "NO",
        "signo_artralgia": "NO",
        "vacunado": "SI",
        "fuente_info_vacuna": "Verbal",
        "tipo_vacuna": "SRP",
        "numero_dosis_spr": "2",
        "fecha_ultima_dosis": "1991-07-22",
        "observaciones_vacuna": "Dosis en infancia",
        "hospitalizado": "NO",
        "hosp_nombre": "",
        "hosp_fecha": "",
        "no_registro_medico": "",
        "condicion_egreso": "",
        "fecha_egreso": "",
        "fecha_defuncion": "",
        "medico_certifica_defuncion": "",
        # Tab 4
        "contacto_sospechoso_7_23": "NO",
        "caso_sospechoso_comunidad_3m": "NO",
        "viajo_7_23_previo": "SI",
        "destino_viaje": "Ciudad de Mexico",
        "contacto_enfermo_catarro": "NO",
        "contacto_embarazada": "NO",
        # Tab 5
        "recolecto_muestra": "SI",
        "muestra_suero": "SI",
        "muestra_suero_fecha": "2026-03-12",
        "muestra_hisopado": "SI",
        "muestra_hisopado_fecha": "2026-03-12",
        "muestra_orina": "NO",
        "muestra_orina_fecha": "",
        "muestra_otra": "NO",
        "muestra_otra_descripcion": "",
        "muestra_otra_fecha": "",
        "antigeno_prueba": "Sarampión",
        "antigeno_otro": "",
        "resultado_prueba": "Negativo",
        "fecha_recepcion_laboratorio": "2026-03-13",
        "fecha_resultado_laboratorio": "2026-03-18",
        # Tab 6
        "clasificacion_caso": "Descartado",
        "fecha_clasificacion_final": "2026-03-20",
        "responsable_clasificacion": "Dr. Ana Ramirez",
        "observaciones": "Caso descartado por IgM negativa",
    }

    result = map_record_to_mspas(sample_record)

    print("=" * 70)
    print("MAPEO IGSS -> MSPAS EPIWEB: Resultado de ejemplo")
    print("=" * 70)

    # Agrupar por tab para mejor lectura
    sections = [
        ("TAB 1: Datos Generales", [
            "fecha_not", "fecha_not_dd", "fecha_not_mm", "fecha_not_yyyy",
            "cbox_centroP", "nom_responsable", "cargo_responsable", "tel_responsable",
        ]),
        ("TAB 2: Datos Paciente", [
            "nombres", "apellidos", "cbox_genero", "rad_embarazada", "rad_lactando",
            "cbox_etnia", "cbox_ocup", "cbox_escolar",
            "cbox_iddep", "cbox_idmun_search", "cbox_idlp_search", "p_dir",
            "fecha_nac", "fecha_nac_dd", "fecha_nac_mm", "fecha_nac_yyyy",
            "txt_anios", "txt_meses", "txt_dias", "nombre_madre",
        ]),
        ("TAB 3: Informacion Clinica", [
            "fecha_ini_sint", "fecha_captacion", "cb_fuente_noti", "fecha_investigacion",
            "slc_activa", "txt_fecha_erupcion", "cbox_erupciones",
            "txt_fecha_fiebre", "txt_temperatura",
            "tos", "coriza", "conjuntivitis", "adenopatias", "artralgia",
            "vacunado", "cb_fuente", "cb_vacuna", "no_dosis", "fecha_ult_dosis",
            "hospitalizacion", "cb_egreso_condicion",
        ]),
        ("TAB 4: Factores de Riesgo", [
            "rad_contacto", "rad_casos", "rad_viajo", "txt_donde_viajo",
            "rad_enfermo", "rad_cont_emb",
        ]),
        ("TAB 5: Laboratorio", [
            "pick_muestra", "chk_suero", "fecha_suero", "chk_HN", "fecha_HN",
            "chk_orina", "fecha_orina",
            "slc_antigeno", "slc_resul_lab", "fecha_recep", "fecha_resul_lab",
        ]),
        ("TAB 6: Clasificacion Final", [
            "slc_clas_final", "txt_fecha_final", "txt_nom_resp_clas", "observaciones_clas",
        ]),
    ]

    for section_name, fields in sections:
        print(f"\n--- {section_name} ---")
        for field in fields:
            val = result.get(field, "???")
            display = f'"{val}"' if val else "(vacio)"
            print(f"  {field:30s} = {display}")

    # Verificaciones
    print("\n" + "=" * 70)
    print("VERIFICACIONES:")
    print("=" * 70)
    checks = [
        ("Sexo F -> '2'", result["cbox_genero"] == "2"),
        ("Depto GUATEMALA -> '1'", result["cbox_iddep"] == "1"),
        ("Etnia Ladino -> '2'", result["cbox_etnia"] == "2"),
        ("Escolaridad Diversificado Completo -> '3'", result["cbox_escolar"] == "3"),
        ("Fuente Publica -> '1'", result["cb_fuente_noti"] == "1"),
        ("Ocupacion SECRETARIA -> SECRETARIO", result["cbox_ocup"] == "SECRETARIO"),
        ("Fecha 2026-03-15 -> 15/03/2026", result["fecha_not"] == "15/03/2026"),
        ("Fecha dd=15", result["fecha_not_dd"] == "15"),
        ("Fecha mm=03", result["fecha_not_mm"] == "03"),
        ("Fecha yyyy=2026", result["fecha_not_yyyy"] == "2026"),
        ("Vacunado SI -> SI", result["vacunado"] == "SI"),
        ("Vacuna SRP -> '4'", result["cb_vacuna"] == "4"),
        ("Dosis 2 -> '2'", result["no_dosis"] == "2"),
        ("Erupcion Cara -> '2'", result["cbox_erupciones"] == "2"),
        ("Antigeno Sarampion -> '1'", result["slc_antigeno"] == "1"),
        ("Resultado Negativo -> '1'", result["slc_resul_lab"] == "1"),
        ("Clasificacion Descartado -> '3'", result["slc_clas_final"] == "3"),
        ("Suero checkbox -> '1'", result["chk_suero"] == "1"),
        ("Orina checkbox -> vacio", result["chk_orina"] == ""),
        ("Busqueda activa Retrospectiva -> '1'", result["slc_activa"] == "1"),
        ("Fuente vacuna Verbal -> '4'", result["cb_fuente"] == "4"),
    ]

    passed = 0
    failed = 0
    for desc, ok in checks:
        status = "OK" if ok else "FALLO"
        if not ok:
            failed += 1
        else:
            passed += 1
        print(f"  [{status}] {desc}")

    print(f"\n  Resultado: {passed}/{len(checks)} verificaciones pasaron")
    if failed > 0:
        print(f"  ATENCION: {failed} verificaciones fallaron")
    else:
        print("  Todas las verificaciones pasaron correctamente")

    # Test parse_date con varios formatos
    print("\n--- Test parse_date ---")
    date_tests = [
        ("2026-03-15", ("15", "03", "2026")),
        ("2026-03-15 14:30:00", ("15", "03", "2026")),
        ("15/03/2026", ("15", "03", "2026")),
        (None, ("", "", "")),
        ("", ("", "", "")),
        ("basura", ("", "", "")),
    ]
    for input_val, expected in date_tests:
        result_date = parse_date(input_val)
        status = "OK" if result_date == expected else "FALLO"
        print(f"  [{status}] parse_date({input_val!r}) = {result_date}")

    return passed == len(checks)


if __name__ == "__main__":
    success = test_mapping()
    raise SystemExit(0 if success else 1)
