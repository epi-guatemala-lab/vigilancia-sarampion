"""
PDF Generator for MSPAS Sarampion/Rubeola Form — Excel Template Version.

Opens the official MSPAS 2026 Excel template (.xlsx), fills in patient data,
and converts to PDF via LibreOffice.  Produces a pixel-perfect 1-page replica
because the template already contains all borders, fonts, colors, and merged cells.

Public API:
    generar_ficha_v2_pdf(data: dict) -> bytes
    generar_fichas_v2_bulk(records: list, merge: bool = True) -> bytes
"""
import copy
import io
import json
import logging
import os
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime

import openpyxl
from openpyxl.drawing.image import Image as XlImage

logger = logging.getLogger(__name__)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
TEMPLATE_PATH = os.path.join(ASSETS_DIR, "ficha_sarampion_template.xlsx")
LOGO_PATH = os.path.join(ASSETS_DIR, "sello_mspas.png")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _g(data: dict, key: str, default: str = "") -> str:
    """Safe get from data dict; treats None/NaN/NULL as empty."""
    val = data.get(key)
    if val is None:
        return default
    s = str(val).strip()
    if s.upper() in ("NONE", "NULL", "NAN", ""):
        return default
    return s


def _parse_date(date_str):
    """Parse a date string and return (DD, MM, YYYY) as strings."""
    if not date_str:
        return ("", "", "")
    date_str = str(date_str).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%d-%m-%Y"):
        try:
            dt = datetime.strptime(date_str[:10], fmt)
            return (f"{dt.day:02d}", f"{dt.month:02d}", str(dt.year))
        except (ValueError, TypeError):
            continue
    return ("", "", "")


def _chk(value) -> bool:
    """Check if a value is truthy / 'SI'."""
    if value is None:
        return False
    return str(value).strip().upper() in ("SI", "SÍ", "S", "1", "TRUE", "X", "YES")


def _is_no(value) -> bool:
    if value is None:
        return False
    return str(value).strip().upper() in ("NO", "N", "0", "FALSE")


def _is_desc(value) -> bool:
    if value is None:
        return False
    return str(value).strip().upper() in ("DESCONOCIDO", "DESC", "D", "UNKNOWN")


def _safe_json(val):
    if not val:
        return []
    if isinstance(val, (list, dict)):
        return val
    try:
        return json.loads(val)
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Cell writing helpers
# ---------------------------------------------------------------------------

def _write(ws, row, col, value):
    """Write a value to a cell, preserving existing formatting.
    If the cell is part of a merged range (not top-left), skip silently.
    """
    from openpyxl.cell.cell import MergedCell
    cell = ws.cell(row=row, column=col)
    if isinstance(cell, MergedCell):
        # Find the top-left cell of this merge and skip — caller should
        # target the correct cell. Log a warning for debugging.
        logger.warning("Attempted write to merged cell R%d:C%d, skipping", row, col)
        return
    cell.value = value


def _check(ws, row, col, condition):
    """Replace ☐ with ☒ if condition is True. Leave unchanged otherwise."""
    if condition:
        from openpyxl.cell.cell import MergedCell
        cell = ws.cell(row=row, column=col)
        if isinstance(cell, MergedCell):
            logger.warning("Attempted check on merged cell R%d:C%d, skipping", row, col)
            return
        cell.value = "☒"


def _write_date(ws, row, col_d, col_m, col_y, date_str):
    """Write DD, MM, YYYY into three separate cells for a date field."""
    dd, mm, yyyy = _parse_date(date_str)
    if dd:
        _write(ws, row, col_d, dd)
        _write(ws, row, col_m, mm)
        _write(ws, row, col_y, yyyy)


def _check_si_no_desc(ws, row, col_si, col_no, col_desc, value):
    """Check the appropriate SI/NO/Desc checkbox based on value."""
    _check(ws, row, col_si, _chk(value))
    _check(ws, row, col_no, _is_no(value))
    _check(ws, row, col_desc, _is_desc(value))


def _check_si_no(ws, row, col_si, col_no, value):
    """Check SI or NO checkbox."""
    _check(ws, row, col_si, _chk(value))
    _check(ws, row, col_no, _is_no(value))


# ---------------------------------------------------------------------------
# Symptom helper (Si/No/Desc in columns E/F/G or Q/R/S)
# ---------------------------------------------------------------------------

def _write_symptom(ws, row, col_si, col_no, col_desc, value):
    """Write a symptom checkbox row: SI / NO / Desc."""
    if value is None or str(value).strip() == "":
        return
    v = str(value).strip().upper()
    if v in ("SI", "SÍ", "S", "1", "TRUE", "X", "YES"):
        _write(ws, row, col_si, "☒")
    elif v in ("NO", "N", "0", "FALSE"):
        _write(ws, row, col_no, "☒")
    elif v in ("DESCONOCIDO", "DESC", "D", "UNKNOWN"):
        _write(ws, row, col_desc, "☒")


# ---------------------------------------------------------------------------
# Fill template with data
# ---------------------------------------------------------------------------

def _fill_template(ws, d: dict):
    """Fill the 'Ficha Epidemiológica' worksheet with patient data.

    Cell positions are based on the actual template analysis:
      - Labels are in their known cells (NOT touched)
      - Data goes into empty cells or checkbox cells
    """

    # ===== ROW 6: DIAGNÓSTICO DE SOSPECHA checkboxes =====
    diag = _g(d, 'diagnostico_sospecha', _g(d, 'diagnostico_registrado', '')).upper()
    is_sar = 'SARAMP' in diag or 'B05' in diag
    is_rub = 'RUBEO' in diag or 'RUBE' in diag or 'B06' in diag
    is_dengue = 'DENGUE' in diag or 'A90' in diag or 'A91' in diag
    is_arbo = 'ARBO' in diag or 'ZIKA' in diag or 'CHIK' in diag
    is_otra_febril = not (is_sar or is_rub or is_dengue or is_arbo) and bool(diag)

    _check(ws, 6, 1, is_sar)       # ☐ Sarampión → A6
    _check(ws, 6, 4, is_rub)       # ☐ Rubéola → D6
    _check(ws, 6, 7, is_dengue)    # ☐ Dengue → G6
    _check(ws, 6, 10, is_arbo)     # ☐ Otra Arbovirosis → J6
    _check(ws, 6, 15, is_otra_febril)  # ☐ Otra febril → O6

    # Especifique for arbovirosis / otra febril
    diag_otro = _g(d, 'diagnostico_sospecha_otro', _g(d, 'diagnostico_otro', ''))
    if is_arbo and diag_otro:
        _write(ws, 6, 20, diag_otro)  # T6 (merged T6:X6)
    elif is_otra_febril and diag_otro:
        _write(ws, 6, 20, diag_otro)

    # ===== ROW 7: Caso altamente sospechoso =====
    caso_alta = _g(d, 'caso_altamente_sospechoso', '')
    _check(ws, 7, 1, _chk(caso_alta))  # only if explicitly flagged  # A7

    # ===== SECCIÓN 1: DATOS DE LA UNIDAD NOTIFICADORA (Rows 9-14) =====

    # Row 9: Fecha Notificación + Área + Distrito + Servicio
    _write_date(ws, 9, 5, 7, 9, _g(d, 'fecha_notificacion'))
    # D9='Día' label, E9=data, F9='Mes' label, G9=data, H9='Año' label, I9=data
    # Actually looking at merged ranges: A9:C9='Fecha de Notificación',
    # D9='Día', E9=empty(data), F9='Mes', G9=empty(data), H9='Año', I9=empty(data)
    # J9:L9='Dirección de Área...' etc.
    # Wait - the template says R9:C4='Día', R9:C6='Mes', R9:C8='Año'
    # That means D9=Día, F9=Mes, H9=Año → data goes in E9, G9, I9
    _write_date(ws, 9, 5, 7, 9, _g(d, 'fecha_notificacion'))

    area_salud = _g(d, 'area_salud_mspas', _g(d, 'departamento_residencia', ''))
    distrito = _g(d, 'distrito_salud_mspas', _g(d, 'municipio_residencia', ''))
    servicio = _g(d, 'servicio_salud_mspas', _g(d, 'unidad_medica', ''))

    # J9:L9 = 'Dirección de Área de Salud' label → M9:O9 = data
    _write(ws, 9, 13, area_salud)
    # P9:Q9 = 'Distrito de Salud' label → R9:T9 = data
    _write(ws, 9, 18, distrito)
    # U9:V9 = 'Servicio de Salud' label → W9:X9 = data
    _write(ws, 9, 23, servicio)

    # Row 10: Fecha Consulta + Fecha investigación Domiciliaria
    _write_date(ws, 10, 5, 7, 9, _g(d, 'fecha_captacion', _g(d, 'fecha_registro_diagnostico', '')))
    _write_date(ws, 10, 15, 17, 19, _g(d, 'fecha_visita_domiciliaria', _g(d, 'fecha_inicio_investigacion', '')))
    # T10:X10 = could be extra data area

    # Row 11: Nombre investigador, Cargo, Teléfono/correo
    _write(ws, 11, 4, _g(d, 'nom_responsable'))       # D11:K11 merged = data
    _write(ws, 11, 14, _g(d, 'cargo_responsable'))     # N11:Q11 merged = data
    tel_correo = _g(d, 'telefono_responsable', '')
    correo = _g(d, 'correo_responsable', '')
    if correo and tel_correo:
        _write(ws, 11, 21, f"{tel_correo} / {correo}")  # U11:X11
    else:
        _write(ws, 11, 21, tel_correo or correo)

    # Row 12: Seguro Social / Establecimiento Privado
    igss_name = _g(d, 'unidad_medica', '') if _chk(_g(d, 'es_seguro_social', 'SI')) else ''
    _write(ws, 12, 5, igss_name)  # E12:L12 merged = data
    priv_name = _g(d, 'establecimiento_privado_nombre', '')
    _write(ws, 12, 17, priv_name)  # Q12:X12 merged = data

    # Row 13-14: Fuente de notificación checkboxes
    fuente = _g(d, 'fuente_notificacion', '').upper()
    _check(ws, 13, 5, 'SERVICIO' in fuente or 'SALUD' in fuente)
    _check(ws, 13, 8, 'LABORATORIO' in fuente and 'ACTIVA' not in fuente)
    _check(ws, 13, 11, 'ACTIVA INSTITUCIONAL' in fuente or 'BAI' in fuente)
    _check(ws, 13, 16, 'ACTIVA COMUNITARIA' in fuente or 'BAC' in fuente)
    _check(ws, 13, 19, 'ACTIVA LABORATORIAL' in fuente)
    _check(ws, 14, 5, 'CONTACTO' in fuente or 'INVESTIGACION' in fuente)
    _check(ws, 14, 9, 'REPORTADO' in fuente or 'COMUNIDAD' in fuente)
    _check(ws, 14, 14, 'AUTO' in fuente or 'GRATUITO' in fuente)
    _check(ws, 14, 19, 'OTRO' in fuente and 'CASO' not in fuente)
    fuente_otra = _g(d, 'fuente_notificacion_otra', '')
    if fuente_otra:
        _write(ws, 14, 22, fuente_otra)  # V14:X14

    # ===== SECCIÓN 2: INFORMACIÓN DEL PACIENTE (Rows 16-22) =====

    # Row 16: Nombres, Apellidos, Sexo
    _write(ws, 16, 3, _g(d, 'nombres'))        # C16:H16
    _write(ws, 16, 11, _g(d, 'apellidos'))      # K16:Q16
    sexo = _g(d, 'sexo', '').upper()
    _check(ws, 16, 20, sexo in ('M', 'MASCULINO'))   # T16 ☐ M
    _check(ws, 16, 22, sexo in ('F', 'FEMENINO'))     # V16 ☐ F

    # Row 17: Fecha Nacimiento + Edad + CUI
    _write_date(ws, 17, 5, 7, 9, _g(d, 'fecha_nacimiento'))
    _write(ws, 17, 12, _g(d, 'edad_anios'))    # L17 = Años data
    _write(ws, 17, 14, _g(d, 'edad_meses'))    # N17 = Meses data
    _write(ws, 17, 16, _g(d, 'edad_dias'))     # P17 = Días data
    cui = _g(d, 'numero_identificacion', _g(d, 'afiliacion', ''))
    _write(ws, 17, 20, cui)                    # T17:X17

    # Row 18: Nombre Tutor, Parentesco, CUI tutor
    _write(ws, 18, 4, _g(d, 'nombre_encargado'))       # D18:J18
    _write(ws, 18, 13, _g(d, 'parentesco_tutor'))       # M18:P18
    _write(ws, 18, 20, _g(d, 'numero_id_tutor'))        # T18:X18

    # Row 19: Pueblo/Etnia + Extranjero + Migrante + Embarazada
    pueblo = _g(d, 'pueblo_etnia', '').upper()
    _check(ws, 19, 3, 'LADINO' in pueblo or 'MESTIZO' in pueblo)    # C19
    _check(ws, 19, 5, 'MAYA' in pueblo)                              # E19
    _check(ws, 19, 7, 'GARIF' in pueblo)                             # G19
    _check(ws, 19, 9, 'XINCA' in pueblo)                             # I19

    # Extranjero: K19='Extranjero', L19='☐ Si', M19='☐ No'
    pais = _g(d, 'pais_residencia', '').upper()
    es_extranjero = pais and pais not in ('GUATEMALA', 'GT', '')
    if es_extranjero:
        ws.cell(row=19, column=12).value = "☒ Si"
    else:
        ws.cell(row=19, column=13).value = "☒ No"

    # Migrante: N19='Migrante', O19='☐ Si', P19='☐ No'
    migrante = _g(d, 'es_migrante', '')
    if _chk(migrante):
        ws.cell(row=19, column=15).value = "☒ Si"
    elif _is_no(migrante):
        ws.cell(row=19, column=16).value = "☒ No"

    # Embarazada: Q19:R19='Embarazada', S19='☐ Si', T19='☐ No'
    embarazada = _g(d, 'esta_embarazada', '')
    if _chk(embarazada):
        ws.cell(row=19, column=19).value = "☒ Si"
    elif _is_no(embarazada):
        ws.cell(row=19, column=20).value = "☒ No"

    # Row 20: Trimestre embarazo, Ocupación, Escolaridad, Teléfono
    _write(ws, 20, 4, _g(d, 'trimestre_embarazo'))      # D20:E20
    _write(ws, 20, 8, _g(d, 'ocupacion'))                # H20:K20
    _write(ws, 20, 14, _g(d, 'escolaridad'))             # N20:Q20
    _write(ws, 20, 20, _g(d, 'telefono_paciente', _g(d, 'telefono_encargado', '')))  # T20:X20

    # Row 21: País residencia, Departamento, Municipio
    _write(ws, 21, 5, _g(d, 'pais_residencia', 'GUATEMALA'))   # E21:H21
    _write(ws, 21, 12, _g(d, 'departamento_residencia'))        # L21:P21
    _write(ws, 21, 20, _g(d, 'municipio_residencia'))           # T21:X21

    # Row 22: Dirección, Lugar Poblado
    _write(ws, 22, 4, _g(d, 'direccion_exacta'))         # D22:O22
    _write(ws, 22, 19, _g(d, 'poblado'))                  # S22:X22

    # ===== SECCIÓN 3: ANTECEDENTES (Rows 24-29) =====

    # Row 24: Paciente Vacunado + Antecedentes médicos
    vacunado = _g(d, 'vacunado', '')
    if _chk(vacunado):
        ws.cell(row=24, column=5).value = "☒ Si"
    elif _is_no(vacunado):
        ws.cell(row=24, column=6).value = "☒ No"
    elif _is_desc(vacunado) or 'VERBAL' in vacunado.upper():
        ws.cell(row=24, column=7).value = "☒ Desconocido/Verbal"

    antec = _g(d, 'tiene_antecedentes_medicos', '')
    if _chk(antec):
        ws.cell(row=24, column=14).value = "☒ Si"
    elif _is_no(antec):
        ws.cell(row=24, column=15).value = "☒ No"
    elif _is_desc(antec):
        ws.cell(row=24, column=16).value = "☒ Desconocido"

    antec_detalle = _g(d, 'antecedentes_medicos_detalle', '')
    if antec_detalle:
        _write(ws, 24, 21, antec_detalle)  # U24:X24

    # Row 25: Antecedentes checkboxes
    _check(ws, 25, 4, _chk(_g(d, 'antecedente_desnutricion')))
    _check(ws, 25, 8, _chk(_g(d, 'antecedente_inmunocompromiso')))
    _check(ws, 25, 13, _chk(_g(d, 'antecedente_enfermedad_cronica')))

    # Rows 27-29: Vaccine doses — SPR, SR, SPRV
    # Each row: G=dosis count, J=Día, K=Mes, L=Año of last dose
    # Fuente verificación: Q=MSPAS checkbox, S=SIGSA/other, V=IGSS checkbox
    dosis_spr = _g(d, 'dosis_spr', _g(d, 'numero_dosis_spr', ''))
    _write(ws, 27, 7, dosis_spr)
    fecha_spr = _g(d, 'fecha_ultima_spr', _g(d, 'fecha_ultima_dosis', ''))
    dd, mm, yyyy = _parse_date(fecha_spr)
    if dd:
        _write(ws, 27, 10, dd)
        _write(ws, 27, 11, mm)
        _write(ws, 27, 12, yyyy)

    # Fuente verificación for SPR
    fuente_vac = _g(d, 'fuente_info_vacuna', '').upper()
    sector_vac = _g(d, 'sector_vacunacion', '').upper()
    combined_vac = f"{fuente_vac} {sector_vac}"
    if 'MSPAS' in combined_vac or 'SIGSA' in combined_vac:
        _write(ws, 27, 17, "☒")
    if 'IGSS' in combined_vac or 'PRIVADO' in combined_vac:
        _write(ws, 27, 22, "☒")

    dosis_sr = _g(d, 'dosis_sr', '')
    _write(ws, 28, 7, dosis_sr)
    dd, mm, yyyy = _parse_date(_g(d, 'fecha_ultima_sr', ''))
    if dd:
        _write(ws, 28, 10, dd)
        _write(ws, 28, 11, mm)
        _write(ws, 28, 12, yyyy)

    dosis_sprv = _g(d, 'dosis_sprv', '')
    _write(ws, 29, 7, dosis_sprv)
    dd, mm, yyyy = _parse_date(_g(d, 'fecha_ultima_sprv', ''))
    if dd:
        _write(ws, 29, 10, dd)
        _write(ws, 29, 11, mm)
        _write(ws, 29, 12, yyyy)

    # ===== SECCIÓN 4: DATOS CLÍNICOS (Rows 31-41) =====

    # Row 31: Fecha inicio síntomas + Fecha inicio fiebre
    # A31:D31='Fecha de Inicio de Síntomas', E31='Día', F31=data, G31='Mes', H31=data, I31='Año', J31=data
    _write_date(ws, 31, 6, 8, 10, _g(d, 'fecha_inicio_sintomas'))
    # K31:N31='Fecha de Inicio de Fiebre', O31='Día', P31=data, Q31='Mes', R31=data, S31='Año', T31=data
    _write_date(ws, 31, 16, 18, 20, _g(d, 'fecha_inicio_fiebre', ''))

    # Row 32: Fecha inicio Exantema
    _write_date(ws, 32, 7, 9, 11, _g(d, 'fecha_inicio_erupcion'))

    # Rows 33-37: Síntomas table
    # Left side (cols E/F/G = Si/No/Desc): Fiebre(34), Exantema(35), Tos(36), Conjuntivitis(37)
    # Right side (cols Q/R/S = Si/No/Desc): Coriza(34), Koplik(35), Artralgia(36), Adenopatías(37)
    _write_symptom(ws, 34, 5, 6, 7, _g(d, 'signo_fiebre'))
    temp = _g(d, 'temperatura_celsius', '')
    if temp:
        # Write temperature in the data area I34:L34 (col 9 is top-left of merge)
        _write(ws, 34, 9, f"{temp}°C")

    _write_symptom(ws, 35, 5, 6, 7, _g(d, 'signo_exantema'))
    _write_symptom(ws, 36, 5, 6, 7, _g(d, 'signo_tos'))
    _write_symptom(ws, 37, 5, 6, 7, _g(d, 'signo_conjuntivitis'))

    _write_symptom(ws, 34, 17, 18, 19, _g(d, 'signo_coriza'))
    _write_symptom(ws, 35, 17, 18, 19, _g(d, 'signo_manchas_koplik'))
    _write_symptom(ws, 36, 17, 18, 19, _g(d, 'signo_artralgia'))
    _write_symptom(ws, 37, 17, 18, 19, _g(d, 'signo_adenopatias'))

    # Row 38: Hospitalización
    hosp = _g(d, 'hospitalizado', '')
    if _chk(hosp):
        ws.cell(row=38, column=4).value = "☒ Si"
    elif _is_no(hosp):
        ws.cell(row=38, column=5).value = "☒ No"
    elif _is_desc(hosp):
        ws.cell(row=38, column=6).value = "☒ Desc."

    _write(ws, 38, 11, _g(d, 'hosp_nombre'))  # K38:P38
    # Fecha hospitalización: Q38:T38 label, U38='Día', V38=data, W38='Mes', X38=data
    dd, mm, yyyy = _parse_date(_g(d, 'hosp_fecha', ''))
    if dd:
        _write(ws, 38, 22, dd)   # after 'Día' at U38
        _write(ws, 38, 24, mm)   # after 'Mes' at W38
    # Año goes on next line if needed — template might not have space

    # Row 39: Complicaciones
    comp = _g(d, 'tiene_complicaciones', _g(d, 'complicaciones', ''))
    if _chk(comp):
        ws.cell(row=39, column=4).value = "☒ Si"
    elif _is_no(comp):
        ws.cell(row=39, column=5).value = "☒ No"
    elif _is_desc(comp):
        ws.cell(row=39, column=6).value = "☒ Desc."

    # Row 40: Complicaciones detail checkboxes
    _check(ws, 40, 4, _chk(_g(d, 'comp_neumonia')))
    _check(ws, 40, 7, _chk(_g(d, 'comp_encefalitis')))
    _check(ws, 40, 10, _chk(_g(d, 'comp_diarrea')))
    _check(ws, 40, 13, _chk(_g(d, 'comp_trombocitopenia')))
    _check(ws, 40, 16, _chk(_g(d, 'comp_otitis')))
    _check(ws, 40, 19, _chk(_g(d, 'comp_ceguera')))
    comp_otra = _g(d, 'comp_otra_texto', _g(d, 'complicaciones_otra', ''))
    if comp_otra:
        _check(ws, 40, 22, True)
        # W40:X40 is merged with label 'Otra' — no separate text cell on this row
        # Write comp text into the merged area next to the label if possible

    # Row 41: Aislamiento Respiratorio
    aisl = _g(d, 'aislamiento_respiratorio', '')
    if _chk(aisl):
        ws.cell(row=41, column=5).value = "☒ Si (fecha)"
        fecha_aisl = _g(d, 'fecha_aislamiento', '')
        if fecha_aisl:
            dd, mm, yyyy = _parse_date(fecha_aisl)
            if dd:
                _write(ws, 41, 7, f"{dd}/{mm}/{yyyy}")  # G41:J41 formatted
    elif _is_no(aisl):
        ws.cell(row=41, column=11).value = "☒ No"
    elif _is_desc(aisl):
        ws.cell(row=41, column=13).value = "☒ Desconocido"

    # ===== SECCIÓN 5: FACTORES DE RIESGO (Rows 43-48) =====

    # Row 43: Caso confirmado + Contacto sospechoso
    caso_conf = _g(d, 'caso_sospechoso_comunidad_3m', '')
    if _chk(caso_conf):
        ws.cell(row=43, column=7).value = "☒ Si"
    elif _is_no(caso_conf):
        ws.cell(row=43, column=8).value = "☒ No"
    elif _is_desc(caso_conf):
        ws.cell(row=43, column=9).value = "☒ Desc."

    contacto_sosp = _g(d, 'contacto_sospechoso_7_23', '')
    if _chk(contacto_sosp):
        ws.cell(row=43, column=18).value = "☒ Si"
    elif _is_no(contacto_sosp):
        ws.cell(row=43, column=19).value = "☒ No"
    elif _is_desc(contacto_sosp):
        ws.cell(row=43, column=20).value = "☒ Desc."

    # Row 44: Viajó + País/Depto/Municipio
    viajo = _g(d, 'viajo_7_23_previo', '')
    if _chk(viajo):
        ws.cell(row=44, column=7).value = "☒ Si"
    elif _is_no(viajo):
        ws.cell(row=44, column=8).value = "☒ No"

    _write(ws, 44, 11, _g(d, 'viaje_pais', _g(d, 'destino_viaje', '')))    # K44:M44
    _write(ws, 44, 16, _g(d, 'viaje_departamento', ''))                      # P44:R44
    _write(ws, 44, 21, _g(d, 'viaje_municipio', ''))                          # U44:X44

    # Row 45: Fecha Salida + Fecha Entrada
    _write_date(ws, 45, 5, 7, 9, _g(d, 'viaje_fecha_salida', ''))
    _write_date(ws, 45, 13, 15, 17, _g(d, 'viaje_fecha_entrada', ''))

    # Row 46: Fecha Retorno (viaje exterior) + Contacto embarazada
    _write_date(ws, 46, 4, 6, 8, _g(d, 'familiar_fecha_retorno', ''))

    contacto_emb = _g(d, 'contacto_embarazada', '')
    if _chk(contacto_emb):
        ws.cell(row=46, column=15).value = "☒ Si"
    elif _is_no(contacto_emb):
        ws.cell(row=46, column=16).value = "☒ No"
    elif _is_desc(contacto_emb):
        ws.cell(row=46, column=17).value = "☒ Desc."

    # Rows 47-48: Fuente de contagio checkboxes
    fuente_c = _g(d, 'fuente_posible_contagio', '').upper()
    _check(ws, 47, 4, 'HOGAR' in fuente_c or 'CASA' in fuente_c)
    _check(ws, 47, 7, 'SALUD' in fuente_c or 'HOSPITAL' in fuente_c)
    _check(ws, 47, 10, 'EDUCATIVA' in fuente_c or 'ESCUELA' in fuente_c)
    _check(ws, 47, 13, 'PÚBLICO' in fuente_c or 'PUBLICO' in fuente_c)
    _check(ws, 47, 16, 'COMUNIDAD' in fuente_c and 'EDUCATIVA' not in fuente_c)
    _check(ws, 47, 19, 'MASIVO' in fuente_c or 'EVENTO' in fuente_c)
    _check(ws, 47, 22, 'INTERNACIONAL' in fuente_c or 'TRANSP' in fuente_c)
    _check(ws, 48, 4, 'DESCONOCIDO' in fuente_c or 'DESC' in fuente_c)
    _check(ws, 48, 8, 'OTRO' in fuente_c and 'DESCONOCIDO' not in fuente_c)
    fuente_c_otro = _g(d, 'fuente_contagio_otro', '')
    if fuente_c_otro:
        _write(ws, 48, 12, fuente_c_otro)  # L48:X48

    # ===== SECCIÓN 6: ACCIONES DE RESPUESTA (Rows 50-52) =====

    # Row 50: BAI + BAC
    bai = _g(d, 'bai_realizada', '')
    if _chk(bai):
        ws.cell(row=50, column=3).value = "☒ Si"
    elif _is_no(bai):
        ws.cell(row=50, column=4).value = "☒ No"
    bai_n = _g(d, 'bai_casos_sospechosos', '')
    if bai_n:
        _write(ws, 50, 8, bai_n)  # H50:I50

    bac = _g(d, 'bac_realizada', '')
    if _chk(bac):
        ws.cell(row=50, column=12).value = "☒ Si"
    elif _is_no(bac):
        ws.cell(row=50, column=13).value = "☒ No"
    bac_n = _g(d, 'bac_casos_sospechosos', '')
    if bac_n:
        _write(ws, 50, 17, bac_n)  # Q50:R50 — actually should be near col 14-16

    # Row 51: Vacunación bloqueo, Monitoreo rápido, Barrido
    vb = _g(d, 'vacunacion_bloqueo', '')
    if _chk(vb):
        ws.cell(row=51, column=7).value = "☒ Si"
    elif _is_no(vb):
        ws.cell(row=51, column=8).value = "☒ No"

    mr = _g(d, 'monitoreo_rapido_vacunacion', '')
    if _chk(mr):
        ws.cell(row=51, column=14).value = "☒ Si"
    elif _is_no(mr):
        ws.cell(row=51, column=15).value = "☒ No"

    bd = _g(d, 'vacunacion_barrido', '')
    if _chk(bd):
        ws.cell(row=51, column=19).value = "☒ Si"
    elif _is_no(bd):
        ws.cell(row=51, column=20).value = "☒ No"

    # Row 52: Vitamina A
    vit = _g(d, 'vitamina_a_administrada', '')
    if _chk(vit):
        ws.cell(row=52, column=4).value = "☒ Si"
    elif _is_no(vit):
        ws.cell(row=52, column=5).value = "☒ No"
    elif _is_desc(vit):
        ws.cell(row=52, column=6).value = "☒ Desc."
    vit_dosis = _g(d, 'vitamina_a_dosis', '')
    if vit_dosis:
        _write(ws, 52, 11, vit_dosis)  # K52:L52

    # ===== SECCIÓN 7: LABORATORIO (Rows 54-62) =====

    # Row 54: Tipo de muestra checkboxes
    tipo_m = _g(d, 'tipo_muestra', '').upper()
    has_suero = 'SUERO' in tipo_m or bool(_g(d, 'muestra_suero_fecha'))
    has_orina = 'ORINA' in tipo_m or bool(_g(d, 'muestra_orina_fecha'))
    has_hisop = 'HISOP' in tipo_m or bool(_g(d, 'muestra_hisopado_fecha'))
    _check(ws, 54, 4, has_suero)
    _check(ws, 54, 7, has_orina)
    _check(ws, 54, 10, has_hisop)

    # Row 55: ¿Por qué no se recolectó?
    motivo_no = _g(d, 'motivo_no_3_muestras', _g(d, 'motivo_no_recoleccion', ''))
    if motivo_no:
        _write(ws, 55, 9, motivo_no)  # I55:X55

    # Rows 57-61: Lab samples table
    # Each row: G:I = Fecha Toma, J:L = Fecha Envío, M:O = Resultado Virus/IgM,
    #           P:R = Resultado IgG/Avidez, S:U = Fecha Resultado, V:X = Secuenciación

    # Try lab_muestras_json first (structured data)
    lab_json = _safe_json(_g(d, 'lab_muestras_json', ''))

    if lab_json:
        # lab_muestras_json is a list of sample dicts
        for i, sample in enumerate(lab_json[:5]):
            row_num = 57 + i
            if isinstance(sample, dict):
                fecha_toma = sample.get('fecha_toma', '')
                dd, mm, yyyy = _parse_date(fecha_toma)
                if dd:
                    _write(ws, row_num, 7, f"{dd}/{mm}/{yyyy}")
                fecha_envio = sample.get('fecha_envio', '')
                dd, mm, yyyy = _parse_date(fecha_envio)
                if dd:
                    _write(ws, row_num, 10, f"{dd}/{mm}/{yyyy}")
                res_virus = sample.get('resultado_virus', sample.get('resultado_igm', ''))
                _write(ws, row_num, 13, res_virus)
                res_igg = sample.get('resultado_igg', sample.get('resultado_avidez', ''))
                _write(ws, row_num, 16, res_igg)
                fecha_res = sample.get('fecha_resultado', '')
                dd, mm, yyyy = _parse_date(fecha_res)
                if dd:
                    _write(ws, row_num, 19, f"{dd}/{mm}/{yyyy}")
                sec = sample.get('secuenciacion', '')
                _write(ws, row_num, 22, sec)
    else:
        # Fallback: use individual fields
        # Row 57: 1a Suero
        dd, mm, yyyy = _parse_date(_g(d, 'muestra_suero_fecha', ''))
        if dd:
            _write(ws, 57, 7, f"{dd}/{mm}/{yyyy}")
        res_igm = _g(d, 'resultado_igm_sarampion_suero', _g(d, 'resultado_igm_cualitativo', ''))
        if res_igm:
            _write(ws, 57, 13, res_igm)
        res_igg = _g(d, 'resultado_igg_sarampion_suero', _g(d, 'resultado_igg_cualitativo', ''))
        if res_igg:
            _write(ws, 57, 16, res_igg)
        dd, mm, yyyy = _parse_date(_g(d, 'fecha_resultado_laboratorio', ''))
        if dd:
            _write(ws, 57, 19, f"{dd}/{mm}/{yyyy}")

        # Row 59: 1a Orina
        dd, mm, yyyy = _parse_date(_g(d, 'muestra_orina_fecha', ''))
        if dd:
            _write(ws, 59, 7, f"{dd}/{mm}/{yyyy}")
        pcr_orina = _g(d, 'resultado_pcr_orina', '')
        if pcr_orina:
            _write(ws, 59, 13, pcr_orina)

        # Row 60: 1a Hisopado NF
        dd, mm, yyyy = _parse_date(_g(d, 'muestra_hisopado_fecha', ''))
        if dd:
            _write(ws, 60, 7, f"{dd}/{mm}/{yyyy}")
        pcr_hisop = _g(d, 'resultado_pcr_hisopado', '')
        if pcr_hisop:
            _write(ws, 60, 13, pcr_hisop)

    # ===== CLASIFICACIÓN (Rows 64-72) =====

    # Row 64: Clasificación Final
    clasif = _g(d, 'clasificacion_caso', '').upper()
    # 'CONFIRMADO' alone means confirmed sarampion (the primary diagnosis)
    is_confirmed = 'CONFIRM' in clasif
    is_descartado = 'DESCART' in clasif
    is_pendiente = 'PENDIENTE' in clasif or 'SOSPECH' in clasif
    is_no_cumple = 'NO CUMPLE' in clasif or 'DEFINICION' in clasif
    is_clasif_sar = ('SARAMP' in clasif and not is_descartado) or (is_confirmed and not is_descartado and is_sar)
    is_clasif_rub = ('RUBEO' in clasif or 'RUBE' in clasif) and not is_descartado
    # If confirmed but no specific disease mentioned, assume primary diagnosis
    if is_confirmed and not is_clasif_sar and not is_clasif_rub and not is_descartado:
        is_clasif_sar = is_sar
        is_clasif_rub = is_rub
    _check(ws, 64, 4, is_clasif_sar)
    _check(ws, 64, 7, is_clasif_rub)
    _check(ws, 64, 10, is_descartado)
    _check(ws, 64, 14, is_pendiente and not is_confirmed)
    _check(ws, 64, 17, is_no_cumple)

    # Row 65: Criterio de confirmación
    crit_conf = _g(d, 'criterio_confirmacion', '').upper()
    _check(ws, 65, 5, 'LABORATORIO' in crit_conf or 'LAB' in crit_conf)
    _check(ws, 65, 9, 'NEXO' in crit_conf or 'EPIDEMIOL' in crit_conf)
    _check(ws, 65, 14, 'CLÍNICO' in crit_conf or 'CLINICO' in crit_conf)

    contacto_caso = _g(d, 'contacto_otro_caso', '')
    if _chk(contacto_caso):
        ws.cell(row=65, column=21).value = "☒ Si"
    elif _is_no(contacto_caso):
        ws.cell(row=65, column=22).value = "☒ No"

    # Row 66: Criterio para descartar
    crit_desc = _g(d, 'criterio_descarte', '').upper()
    _check(ws, 66, 5, 'LABORAT' in crit_desc)
    _check(ws, 66, 9, 'VACUNA' in crit_desc)
    _check(ws, 66, 14, 'CLÍNICO' in crit_desc or 'CLINICO' in crit_desc)
    _check(ws, 66, 18, 'OTRO' in crit_desc)

    # Row 67: Fuente de infección
    fuente_inf = _g(d, 'fuente_infeccion', '').upper()
    _check(ws, 67, 4, 'IMPORTADO' in fuente_inf and 'RELACIONADO' not in fuente_inf)
    _check(ws, 67, 8, 'RELACIONADO' in fuente_inf)
    _check(ws, 67, 14, 'ENDÉMI' in fuente_inf or 'ENDEMI' in fuente_inf)
    _check(ws, 67, 18, 'DESCONOCID' in fuente_inf)

    # Row 68: País de importación
    _write(ws, 68, 5, _g(d, 'pais_importacion', ''))  # E68:L68

    # Row 69: Caso Analizado Por
    analizado = _g(d, 'caso_analizado_por', '').upper()
    _check(ws, 69, 5, 'CONAPI' in analizado)
    _check(ws, 69, 8, 'DEGR' in analizado)
    _check(ws, 69, 14, 'COMISIÓN' in analizado or 'COMISION' in analizado or 'NACIONAL' in analizado)
    _check(ws, 69, 19, 'OTRO' in analizado)
    otro_analiz = _g(d, 'caso_analizado_por_otro', '')
    if otro_analiz:
        _write(ws, 69, 22, otro_analiz)  # V69:X69

    # Row 70: Fecha de clasificación
    _write_date(ws, 70, 6, 8, 10, _g(d, 'fecha_clasificacion_final', ''))

    # Row 71: Condición Final
    cond = _g(d, 'condicion_final_paciente', _g(d, 'condicion_egreso', '')).upper()
    _check(ws, 71, 4, 'RECUPER' in cond or 'VIVO' in cond or 'MEJORAD' in cond or 'CURAD' in cond)
    _check(ws, 71, 8, 'SECUELA' in cond)
    _check(ws, 71, 12, 'FALLEC' in cond or 'MUERTE' in cond)
    _check(ws, 71, 16, 'DESCONOCID' in cond)

    # Row 72: Fecha defunción + Causa muerte
    _write_date(ws, 72, 5, 7, 9, _g(d, 'fecha_defuncion', ''))
    _write(ws, 72, 14, _g(d, 'causa_muerte_certificado', ''))  # N72:X72

    # Row 73-74: Observaciones
    obs = _g(d, 'observaciones', '')
    if obs:
        _write(ws, 74, 1, obs)  # A74:X74


# ---------------------------------------------------------------------------
# Excel → PDF conversion via LibreOffice
# ---------------------------------------------------------------------------

def _xlsx_to_pdf(xlsx_path: str) -> bytes:
    """Convert an .xlsx file to PDF using LibreOffice in headless mode."""
    out_dir = os.path.dirname(xlsx_path)

    cmd = [
        "libreoffice",
        "--headless",
        "--calc",
        "--convert-to", "pdf",
        "--outdir", out_dir,
        xlsx_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, "HOME": "/tmp"},
        )
        if result.returncode != 0:
            logger.error("LibreOffice conversion failed: %s", result.stderr)
            raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")
    except FileNotFoundError:
        # LibreOffice not installed — try soffice
        cmd[0] = "soffice"
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, "HOME": "/tmp"},
        )
        if result.returncode != 0:
            raise RuntimeError(f"soffice conversion failed: {result.stderr}")

    pdf_path = xlsx_path.rsplit(".", 1)[0] + ".pdf"
    if not os.path.exists(pdf_path):
        raise RuntimeError(f"PDF not generated at {pdf_path}. stdout={result.stdout}")

    with open(pdf_path, "rb") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generar_ficha_v2_pdf(data: dict) -> bytes:
    """Generate a single PDF ficha from patient data using the Excel template.

    Args:
        data: dict with patient fields (from database record)

    Returns:
        PDF file contents as bytes
    """
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")

    with tempfile.TemporaryDirectory(prefix="ficha_v2_") as tmpdir:
        # Copy template
        registro_id = _g(data, 'registro_id', 'unknown')
        safe_id = registro_id.replace('/', '_').replace('\\', '_')[:50]
        xlsx_path = os.path.join(tmpdir, f"ficha_{safe_id}.xlsx")
        shutil.copy2(TEMPLATE_PATH, xlsx_path)

        # Open and fill
        wb = openpyxl.load_workbook(xlsx_path)
        ws = wb["Ficha Epidemiológica"]

        # Logo MSPAS: se incluye directamente en el template Excel
        # (no se inyecta por código para evitar solapar el título)

        _fill_template(ws, data)

        # Ensure print settings force 1-page output
        ws.page_setup.orientation = "portrait"
        ws.page_setup.paperSize = 1  # Letter
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 1
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.scale = None  # Let fitToPage control sizing
        ws.print_area = "A1:X75"

        wb.save(xlsx_path)

        # Convert to PDF
        pdf_bytes = _xlsx_to_pdf(xlsx_path)

    return pdf_bytes


def generar_fichas_v2_bulk(records: list, merge: bool = True) -> bytes:
    """Generate PDFs for multiple records.

    Args:
        records: list of dicts with patient data
        merge: if True, return a single merged PDF; if False, return a ZIP of individual PDFs

    Returns:
        PDF bytes (if merge=True) or ZIP bytes (if merge=False)
    """
    if not records:
        raise ValueError("No records provided")

    if len(records) == 1:
        return generar_ficha_v2_pdf(records[0])

    with tempfile.TemporaryDirectory(prefix="fichas_v2_bulk_") as tmpdir:
        pdf_files = []

        for i, rec in enumerate(records):
            registro_id = _g(rec, 'registro_id', f'rec_{i}')
            safe_id = registro_id.replace('/', '_').replace('\\', '_')[:50]
            xlsx_path = os.path.join(tmpdir, f"ficha_{i:04d}_{safe_id}.xlsx")
            shutil.copy2(TEMPLATE_PATH, xlsx_path)

            wb = openpyxl.load_workbook(xlsx_path)
            ws = wb["Ficha Epidemiológica"]

            # Logo MSPAS: incluido en el template Excel

            _fill_template(ws, rec)

            # Ensure 1-page output
            ws.page_setup.orientation = "portrait"
            ws.page_setup.paperSize = 1
            ws.page_setup.fitToWidth = 1
            ws.page_setup.fitToHeight = 1
            ws.sheet_properties.pageSetUpPr.fitToPage = True
            ws.page_setup.scale = None
            ws.print_area = "A1:X75"

            wb.save(xlsx_path)

            pdf_bytes = _xlsx_to_pdf(xlsx_path)
            pdf_path = os.path.join(tmpdir, f"ficha_{i:04d}_{safe_id}.pdf")
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            pdf_files.append(pdf_path)

        if merge:
            # Merge PDFs using PyPDF2 or pikepdf if available, otherwise
            # fall back to simple concatenation via a writer
            try:
                from pypdf import PdfReader, PdfWriter
                writer = PdfWriter()
                for pf in pdf_files:
                    reader = PdfReader(pf)
                    for page in reader.pages:
                        writer.add_page(page)
                buf = io.BytesIO()
                writer.write(buf)
                return buf.getvalue()
            except ImportError:
                pass

            try:
                from PyPDF2 import PdfReader, PdfWriter
                writer = PdfWriter()
                for pf in pdf_files:
                    reader = PdfReader(pf)
                    for page in reader.pages:
                        writer.add_page(page)
                buf = io.BytesIO()
                writer.write(buf)
                return buf.getvalue()
            except ImportError:
                pass

            # Last resort: return first PDF only (lossy)
            logger.warning("No PDF merger available; returning only first PDF")
            with open(pdf_files[0], "rb") as f:
                return f.read()
        else:
            # Return ZIP
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for pf in pdf_files:
                    zf.write(pf, os.path.basename(pf))
            return buf.getvalue()


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_data = {
        'registro_id': 'TEST-2026-001',
        'diagnostico_sospecha': 'SARAMPIÓN',
        'diagnostico_registrado': 'SARAMPIÓN',
        'fecha_notificacion': '2026-03-15',
        'area_salud_mspas': 'GUATEMALA CENTRAL',
        'distrito_salud_mspas': 'GUATEMALA',
        'servicio_salud_mspas': 'IGSS ZONA 9',
        'fecha_captacion': '2026-03-14',
        'fecha_visita_domiciliaria': '2026-03-16',
        'nom_responsable': 'Dr. Juan Pérez',
        'cargo_responsable': 'Médico Epidemiólogo',
        'telefono_responsable': '5555-1234',
        'correo_responsable': 'jperez@igss.gob.gt',
        'es_seguro_social': 'SI',
        'unidad_medica': 'Hospital General de Enfermedades IGSS',
        'fuente_notificacion': 'Servicio De Salud',
        'nombres': 'María Isabel',
        'apellidos': 'García López',
        'sexo': 'F',
        'fecha_nacimiento': '1995-06-15',
        'edad_anios': '30',
        'edad_meses': '9',
        'numero_identificacion': '1234567890101',
        'afiliacion': '12345678',
        'pueblo_etnia': 'Ladino',
        'pais_residencia': 'Guatemala',
        'departamento_residencia': 'Guatemala',
        'municipio_residencia': 'Guatemala',
        'direccion_exacta': '5a. Avenida 12-34, Zona 1',
        'poblado': 'Ciudad de Guatemala',
        'ocupacion': 'Enfermera',
        'escolaridad': 'Universitaria',
        'telefono_paciente': '5555-5678',
        'esta_embarazada': 'NO',
        'vacunado': 'SI',
        'dosis_spr': '2',
        'fecha_ultima_spr': '2010-03-15',
        'fuente_info_vacuna': 'MSPAS',
        'tiene_antecedentes_medicos': 'NO',
        'fecha_inicio_sintomas': '2026-03-10',
        'fecha_inicio_fiebre': '2026-03-10',
        'fecha_inicio_erupcion': '2026-03-12',
        'signo_fiebre': 'SI',
        'temperatura_celsius': '38.5',
        'signo_exantema': 'SI',
        'signo_tos': 'SI',
        'signo_conjuntivitis': 'SI',
        'signo_coriza': 'SI',
        'signo_manchas_koplik': 'NO',
        'signo_artralgia': 'NO',
        'signo_adenopatias': 'SI',
        'hospitalizado': 'SI',
        'hosp_nombre': 'Hospital General de Enfermedades IGSS',
        'hosp_fecha': '2026-03-14',
        'tiene_complicaciones': 'NO',
        'aislamiento_respiratorio': 'SI',
        'fecha_aislamiento': '2026-03-14',
        'caso_sospechoso_comunidad_3m': 'NO',
        'contacto_sospechoso_7_23': 'SI',
        'viajo_7_23_previo': 'NO',
        'contacto_embarazada': 'NO',
        'fuente_posible_contagio': 'Serv. Salud',
        'bai_realizada': 'SI',
        'bai_casos_sospechosos': '3',
        'bac_realizada': 'NO',
        'vacunacion_bloqueo': 'SI',
        'monitoreo_rapido_vacunacion': 'SI',
        'vacunacion_barrido': 'NO',
        'vitamina_a_administrada': 'SI',
        'vitamina_a_dosis': '1',
        'muestra_suero': 'SI',
        'muestra_suero_fecha': '2026-03-15',
        'muestra_hisopado': 'SI',
        'muestra_hisopado_fecha': '2026-03-15',
        'muestra_orina': 'SI',
        'muestra_orina_fecha': '2026-03-16',
        'resultado_igm_cualitativo': 'POSITIVO',
        'resultado_igg_cualitativo': 'NEGATIVO',
        'resultado_pcr_hisopado': 'POSITIVO',
        'resultado_pcr_orina': 'NEGATIVO',
        'fecha_resultado_laboratorio': '2026-03-18',
        'clasificacion_caso': 'SARAMPIÓN CONFIRMADO',
        'criterio_confirmacion': 'Laboratorio',
        'contacto_otro_caso': 'SI',
        'fuente_infeccion': 'Importado',
        'pais_importacion': 'Honduras',
        'caso_analizado_por': 'CONAPI',
        'fecha_clasificacion_final': '2026-03-20',
        'condicion_final_paciente': 'Recuperado',
        'observaciones': 'Caso importado de Honduras. Contacto con caso confirmado en San Pedro Sula.',
    }

    print("Generating test PDF with full data...")
    pdf_bytes = generar_ficha_v2_pdf(test_data)
    out_path = "/tmp/ficha_v2_test_full.pdf"
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"  Written to {out_path} ({len(pdf_bytes)} bytes)")

    print("Generating test PDF with empty data...")
    pdf_bytes_empty = generar_ficha_v2_pdf({'registro_id': 'EMPTY-TEST'})
    out_path_empty = "/tmp/ficha_v2_test_empty.pdf"
    with open(out_path_empty, "wb") as f:
        f.write(pdf_bytes_empty)
    print(f"  Written to {out_path_empty} ({len(pdf_bytes_empty)} bytes)")

    print("Done.")
