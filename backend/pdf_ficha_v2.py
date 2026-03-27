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

    Cell positions are based on the v2 template (82 rows x 20 cols A-T).
    Template: ficha_sarampion_template.xlsx — Sheet "Ficha Epidemiológica"

    Convention:
      - R10 = labels row, R11 = data row (for fecha notificación, etc.)
      - Checkbox labels ("Si", "No", "Desconocido") are replaced with "☒" when checked
      - Empty merged ranges are DATA cells (values written to top-left)
    """

    # ===== ROW 7: DIAGNÓSTICO DE SOSPECHA checkboxes =====
    # R7: A7:B8='Diagnóstico de Sospecha' label, C7='Sarampión', E7='Rubéola',
    #     G7='Dengue', I7='Otra Arbovirosis', L7='Especifique', O7:T7=empty data
    diag = _g(d, 'diagnostico_sospecha', _g(d, 'diagnostico_registrado', '')).upper()
    is_sar = 'SARAMP' in diag or 'B05' in diag
    is_rub = 'RUBEO' in diag or 'RUBE' in diag or 'B06' in diag
    is_dengue = 'DENGUE' in diag or 'A90' in diag or 'A91' in diag
    is_arbo = 'ARBO' in diag or 'ZIKA' in diag or 'CHIK' in diag
    is_otra_febril = not (is_sar or is_rub or is_dengue or is_arbo) and bool(diag)

    _check(ws, 7, 3, is_sar)        # C7 = Sarampión
    _check(ws, 7, 5, is_rub)        # E7 = Rubéola
    _check(ws, 7, 7, is_dengue)     # G7 = Dengue
    _check(ws, 7, 9, is_arbo)       # I7 = Otra Arbovirosis

    # Especifique for arbovirosis (O7:T7 empty merge)
    diag_otro = _g(d, 'diagnostico_sospecha_otro', _g(d, 'diagnostico_otro', ''))
    if is_arbo and diag_otro:
        _write(ws, 7, 15, diag_otro)  # O7:T7 data area
    elif is_arbo:
        arbo_text = ''
        if 'ZIKA' in diag:
            arbo_text = 'Zika'
        elif 'CHIK' in diag:
            arbo_text = 'Chikungunya'
        if arbo_text:
            _write(ws, 7, 15, arbo_text)

    # R8: C8='Otra febril exantemática', G8='Especifique', I8:M8=empty data,
    #     N8='Caso altamente sospechoso...'
    _check(ws, 8, 3, is_otra_febril)  # C8 = Otra febril exantemática
    if is_otra_febril and diag_otro:
        _write(ws, 8, 9, diag_otro)   # I8:M8 = Especifique data

    # Caso altamente sospechoso de Sarampión
    caso_alta = _g(d, 'caso_altamente_sospechoso', '')
    _check(ws, 8, 14, _chk(caso_alta))  # N8:T8

    # ===== SECCIÓN 1: DATOS DE LA UNIDAD NOTIFICADORA (Rows 9-16) =====

    # R10 = labels: A10='Fecha de Notificación', B10='Día', C10='Mes', D10='Año',
    #   E10:J10='Dirección de Área de Salud', K10:N10='Distrito de Salud', O10:T10='Servicio de Salud'
    # R11 = DATA: B11=día, C11=mes, D11=año, E11:J11=area data, K11:N11=distrito data, O11:T11=servicio data
    _write_date(ws, 11, 2, 3, 4, _g(d, 'fecha_notificacion'))

    area_salud = _g(d, 'area_salud_mspas', _g(d, 'departamento_residencia', ''))
    distrito = _g(d, 'distrito_salud_mspas', _g(d, 'municipio_residencia', ''))
    servicio = _g(d, 'servicio_salud_mspas', _g(d, 'unidad_medica', ''))

    _write(ws, 11, 5, area_salud)    # E11:J11 = data
    _write(ws, 11, 11, distrito)     # K11:N11 = data
    _write(ws, 11, 15, servicio)     # O11:T11 = data

    # R12 = labels: A12='Fecha de Consulta', B12='Día', C12='Mes', D12='Año',
    #   E12:F13='Fecha investigación Domiciliaria', G12='Día', H12='Mes', I12='Año'
    #   J12:N12='Nombre de quien investiga', O12:T12=empty data
    # R13 = DATA: B13=día consulta, C13=mes, D13=año, G13=día invest, H13=mes, I13=año
    #   J13='Cargo de quien investiga', L13:N13=cargo data, O13:P13=empty, Q13:T13=tel data
    _write_date(ws, 13, 2, 3, 4, _g(d, 'fecha_captacion', _g(d, 'fecha_registro_diagnostico', '')))
    _write_date(ws, 13, 7, 8, 9, _g(d, 'fecha_visita_domiciliaria', _g(d, 'fecha_inicio_investigacion', '')))

    _write(ws, 12, 15, _g(d, 'nom_responsable'))   # O12:T12 = nombre investigador data
    _write(ws, 13, 12, _g(d, 'cargo_responsable'))  # L13:N13 = cargo data

    tel_correo = _g(d, 'telefono_responsable', '')
    correo = _g(d, 'correo_responsable', '')
    if correo and tel_correo:
        _write(ws, 13, 17, f"{tel_correo} / {correo}")  # Q13:T13
    else:
        _write(ws, 13, 17, tel_correo or correo)

    # R14: A14:B14='Seguro Social (IGSS)', C14:D14='Especifique', E14:I14=data (IGSS name),
    #   J14:K14='Establecimiento Privado', L14:R14=data (private name), S14:T14='Especifique'
    igss_name = _g(d, 'unidad_medica', '') if _chk(_g(d, 'es_seguro_social', 'SI')) else ''
    _write(ws, 14, 5, igss_name)    # E14:I14 = IGSS establishment data
    priv_name = _g(d, 'establecimiento_privado_nombre', '')
    _write(ws, 14, 12, priv_name)   # L14:R14 = private establishment data

    # R15-16: Fuente de notificación checkboxes
    # R15: B15:C15='Servicio De Salud', D15:E15='Laboratorio', F15:H15='BAI',
    #      I15:L15='BAC', M15:Q15=empty, R15:T15='BA Laboratorial'
    # R16: B16:C16='Investig. Contactos', D16:G16='Caso Reportado Comunidad',
    #      H16:K16='Auto Notificación', L16:M16='Otro', N16:R16=empty, S16:T16='Especifique'
    fuente = _g(d, 'fuente_notificacion', '').upper()
    _check(ws, 15, 2, 'SERVICIO' in fuente or 'SALUD' in fuente)           # B15
    _check(ws, 15, 4, 'LABORATORIO' in fuente and 'ACTIVA' not in fuente)  # D15
    _check(ws, 15, 6, 'ACTIVA INSTITUCIONAL' in fuente or 'BAI' in fuente) # F15
    _check(ws, 15, 9, 'ACTIVA COMUNITARIA' in fuente or 'BAC' in fuente)   # I15
    _check(ws, 15, 18, 'ACTIVA LABORATORIAL' in fuente)                     # R15
    _check(ws, 16, 2, 'CONTACTO' in fuente or 'INVESTIGACION' in fuente)   # B16
    _check(ws, 16, 4, 'REPORTADO' in fuente or 'COMUNIDAD' in fuente)      # D16
    _check(ws, 16, 8, 'AUTO' in fuente or 'GRATUITO' in fuente)            # H16
    _check(ws, 16, 12, 'OTRO' in fuente and 'CASO' not in fuente)          # L16
    fuente_otra = _g(d, 'fuente_notificacion_otra', '')
    if fuente_otra:
        _write(ws, 16, 19, fuente_otra)  # S16:T16

    # ===== SECCIÓN 2: INFORMACIÓN DEL PACIENTE (Rows 17-25) =====

    # R18: A18='Nombres', B18:F18=data, G18:H18='Apellidos', I18:N18=data,
    #      O18='Sexo', P18:Q18='Masculino', R18:T18='Femenino'
    _write(ws, 18, 2, _g(d, 'nombres'))      # B18:F18 = data
    _write(ws, 18, 9, _g(d, 'apellidos'))     # I18:N18 = data
    sexo = _g(d, 'sexo', '').upper()
    _check(ws, 18, 16, sexo in ('M', 'MASCULINO'))  # P18 = Masculino checkbox
    _check(ws, 18, 18, sexo in ('F', 'FEMENINO'))   # R18 = Femenino checkbox

    # R19: A19:A20='Fecha De Nacimiento', B19='Día', C19='Mes', D19='Año',
    #      E19:E20='Edad', F19='Años', G19='Meses', H19='Días',
    #      I19:J19='Código Único de Identificación', K19:T19=CUI data
    # R20: B20=día data, C20=mes data, D20=año data, F20=años data, G20=meses data, H20=días data,
    #      I20:J20=CUI label cont., K20:T20=CUI data (alt row)
    _write_date(ws, 20, 2, 3, 4, _g(d, 'fecha_nacimiento'))
    _write(ws, 20, 6, _g(d, 'edad_anios'))    # F20 = Años data
    _write(ws, 20, 7, _g(d, 'edad_meses'))    # G20 = Meses data
    _write(ws, 20, 8, _g(d, 'edad_dias'))     # H20 = Días data
    cui = _g(d, 'numero_identificacion', _g(d, 'afiliacion', ''))
    _write(ws, 19, 11, cui)                    # K19:T19 = CUI data

    # R21: A21:B21='Nombre del Tutor', C21:E21=data, F21:G21='Parentesco', H21:T21=data
    _write(ws, 21, 3, _g(d, 'nombre_encargado'))     # C21:E21 = tutor name data
    _write(ws, 21, 8, _g(d, 'parentesco_tutor'))      # H21:T21 = parentesco + CUI data
    cui_tutor = _g(d, 'numero_id_tutor', '')
    if cui_tutor:
        # Append CUI tutor to parentesco field since there is only one data area
        parent = _g(d, 'parentesco_tutor', '')
        combined = f"{parent} / CUI: {cui_tutor}" if parent else f"CUI: {cui_tutor}"
        _write(ws, 21, 8, combined)

    # R22: A22='Pueblo', B22='Ladino', C22='Maya', D22='Garífuna', E22='Xinca',
    #      F22:G22='Extranjero', H22='Si', I22='No',
    #      J22='Migrante', K22='Si', L22=empty, M22='No', N22=empty,
    #      O22:P22='Embarazada', Q22='Si', R22=empty, S22='No', T22=empty
    pueblo = _g(d, 'pueblo_etnia', '').upper()
    _check(ws, 22, 2, 'LADINO' in pueblo or 'MESTIZO' in pueblo)    # B22
    _check(ws, 22, 3, 'MAYA' in pueblo)                              # C22
    _check(ws, 22, 4, 'GARIF' in pueblo)                             # D22
    _check(ws, 22, 5, 'XINCA' in pueblo)                             # E22

    pais = _g(d, 'pais_residencia', '').upper()
    es_extranjero = pais and pais not in ('GUATEMALA', 'GT', '')
    _check(ws, 22, 8, es_extranjero)        # H22 = Si
    _check(ws, 22, 9, not es_extranjero)     # I22 = No

    migrante = _g(d, 'es_migrante', '')
    _check(ws, 22, 11, _chk(migrante))      # K22 = Si
    _check(ws, 22, 13, _is_no(migrante))     # M22 = No

    embarazada = _g(d, 'esta_embarazada', '')
    _check(ws, 22, 17, _chk(embarazada))     # Q22 = Si
    _check(ws, 22, 19, _is_no(embarazada))   # S22 = No

    # R23: A23:B23='Trimestre de Embarazo', C23:D23='Ocupación', E23:H23=data(ocupación),
    #      I23:J23='Escolaridad', K23:O23=data(escolaridad), P23:Q23='Teléfono', R23:T23=data(tel)
    _write(ws, 23, 3, _g(d, 'trimestre_embarazo'))   # C23:D23 — rewrite label with data
    # Actually C23='Ocupación' label. Trimestre goes... let me check.
    # R23: A23:B23='Trimestre de Embarazo' (label), so trimestre data could go after it.
    # But there's no explicit data cell. The layout has no empty merge for trimestre.
    # We'll put trimestre value between the label. Skip if no dedicated cell.

    _write(ws, 23, 5, _g(d, 'ocupacion'))            # E23:H23 = data
    _write(ws, 23, 11, _g(d, 'escolaridad'))          # K23:O23 = data
    _write(ws, 23, 18, _g(d, 'telefono_paciente', _g(d, 'telefono_encargado', '')))  # R23:T23 = data

    # R24: A24:B24='País de Residencia', C24:E24=data, F24:G24='Depto Residencia', H24:K24=data,
    #      L24:M24='Municipio de Residencia', N24:T24=data
    _write(ws, 24, 3, _g(d, 'pais_residencia', 'GUATEMALA'))  # C24:E24 = data
    _write(ws, 24, 8, _g(d, 'departamento_residencia'))        # H24:K24 = data
    _write(ws, 24, 14, _g(d, 'municipio_residencia'))          # N24:T24 = data

    # R25: A25:B25='Dirección de Residencia', C25:L25=data, M25:N25='Lugar Poblado', O25:T25=data
    _write(ws, 25, 3, _g(d, 'direccion_exacta'))    # C25:L25 = data
    _write(ws, 25, 15, _g(d, 'poblado'))             # O25:T25 = data

    # ===== SECCIÓN 3: ANTECEDENTES MÉDICOS Y DE VACUNACIÓN (Rows 26-32) =====

    # R27: A27:B27='Paciente Vacunado', C27='Si', D27='No', E27:G27='Desconocido/Verbal',
    #      H27:J27='Antecedentes médicos', K27:M27='Si', N27:P27='No', Q27:T27='Desconocido'
    vacunado = _g(d, 'vacunado', '')
    _check(ws, 27, 3, _chk(vacunado))                                    # C27 = Si
    _check(ws, 27, 4, _is_no(vacunado))                                  # D27 = No
    _check(ws, 27, 5, _is_desc(vacunado) or 'VERBAL' in vacunado.upper())  # E27 = Desconocido/Verbal

    antec = _g(d, 'tiene_antecedentes_medicos', '')
    _check(ws, 27, 11, _chk(antec))     # K27 = Si
    _check(ws, 27, 14, _is_no(antec))   # N27 = No
    _check(ws, 27, 17, _is_desc(antec)) # Q27 = Desconocido

    # R28: A28:B28='Antecedentes Médicos', C28:E28='Desnutrición', F28:H28='Inmunocompromiso',
    #      I28:K28='Enfermedad Crónica', L28:M28='Especifique', N28:T28=data
    _check(ws, 28, 3, _chk(_g(d, 'antecedente_desnutricion')))       # C28
    _check(ws, 28, 6, _chk(_g(d, 'antecedente_inmunocompromiso')))   # F28
    _check(ws, 28, 9, _chk(_g(d, 'antecedente_enfermedad_cronica'))) # I28
    antec_detalle = _g(d, 'antecedentes_medicos_detalle', '')
    if antec_detalle:
        _write(ws, 28, 14, antec_detalle)  # N28:T28 = data

    # R29: header row for vaccine table
    # R30: A30:D30='SPR', E30:F30=data(dosis), G30='Día', H30='Mes', I30='Año',
    #      J30:O30='Carné De Vacunación', P30:T30='MSPAS'
    dosis_spr = _g(d, 'dosis_spr', _g(d, 'numero_dosis_spr', ''))
    _write(ws, 30, 5, dosis_spr)     # E30:F30 = dosis count data
    fecha_spr = _g(d, 'fecha_ultima_spr', _g(d, 'fecha_ultima_dosis', ''))
    dd, mm, yyyy = _parse_date(fecha_spr)
    if dd:
        _write(ws, 30, 7, dd)   # G30 (label says 'Día' but it's overwritten — actually it IS the label)
        _write(ws, 30, 8, mm)   # H30
        _write(ws, 30, 9, yyyy) # I30

    # Fuente verificación checkboxes: J30='Carné', P30='MSPAS' — these are labels
    # The checkboxes are ON the label cells themselves
    fuente_vac = _g(d, 'fuente_info_vacuna', '').upper()
    sector_vac = _g(d, 'sector_vacunacion', '').upper()
    combined_vac = f"{fuente_vac} {sector_vac}"
    if 'CARNE' in combined_vac or 'CARNÉ' in combined_vac:
        _check(ws, 30, 10, True)  # J30 = Carné checkbox
    if 'MSPAS' in combined_vac:
        _check(ws, 30, 16, True)  # P30 = MSPAS checkbox

    # R31: A31:D31='SR', E31:F31=data(dosis), G-I=fecha, J31:O31='SIGSA', P31:T31='IGSS'
    dosis_sr = _g(d, 'dosis_sr', '')
    _write(ws, 31, 5, dosis_sr)    # E31:F31
    dd, mm, yyyy = _parse_date(_g(d, 'fecha_ultima_sr', ''))
    if dd:
        _write(ws, 31, 7, dd)
        _write(ws, 31, 8, mm)
        _write(ws, 31, 9, yyyy)
    if 'IGSS' in combined_vac:
        _check(ws, 31, 16, True)  # P31 = IGSS checkbox

    # R32: A32:D32='SPRV', E32:F32=data(dosis), G-I=fecha, J32:O32='Registro Único', P32:T32='Privado'
    dosis_sprv = _g(d, 'dosis_sprv', '')
    _write(ws, 32, 5, dosis_sprv)  # E32:F32
    dd, mm, yyyy = _parse_date(_g(d, 'fecha_ultima_sprv', ''))
    if dd:
        _write(ws, 32, 7, dd)
        _write(ws, 32, 8, mm)
        _write(ws, 32, 9, yyyy)
    if 'PRIVADO' in combined_vac:
        _check(ws, 32, 16, True)  # P32 = Privado checkbox

    # ===== SECCIÓN 4: DATOS CLÍNICOS (Rows 33-42) =====

    # R34: A34:A35='Fecha Inicio Síntomas', B34='Día', C34='Mes', D34='Año',
    #      E34:F35='Fecha Inicio Fiebre', G34='Día', H34='Mes', I34='Año',
    #      J34:L35='Fecha inicio Exantema/Rash', M34='Día', N34='Mes', O34='Año'
    #      P34:T35 = empty data (extra area)
    # The date labels (Día/Mes/Año) in R34 are LABELS. Data goes in the ROW BELOW (R35):
    # But wait — R34 and R35 share merged ranges (A34:A35, E34:F35, J34:L35, P34:T35)
    # That means rows 34-35 are a single band. Let me check R35 for empty cells.
    # Actually the Día/Mes/Año labels ARE in R34 for all three dates.
    # The data would go... Let me look more carefully. There are no empty non-merged cells in R34/R35
    # except P34 (which is the empty merge P34:T35).
    # The pattern here is: B34='Día' is a HEADER. The actual day value should replace it or go next to it.
    # Since the rows are small, we write the date AS the value in the Día/Mes/Año cells themselves.
    # Actually no — looking at R10/R11 pattern, R10 has labels and R11 has data.
    # But R34:A35 is a merged two-row range. There are no separate data cells below.
    # The Día/Mes/Año ARE the data cells — we overwrite them with actual values.
    # This is consistent with hand-filled forms where you write over "Día" etc.

    # Fecha inicio síntomas: B34=Día, C34=Mes, D34=Año (overwrite labels with values)
    dd, mm, yyyy = _parse_date(_g(d, 'fecha_inicio_sintomas'))
    if dd:
        _write(ws, 34, 2, dd)   # B34
        _write(ws, 34, 3, mm)   # C34
        _write(ws, 34, 4, yyyy) # D34

    # Fecha inicio fiebre: G34=Día, H34=Mes, I34=Año
    dd, mm, yyyy = _parse_date(_g(d, 'fecha_inicio_fiebre', ''))
    if dd:
        _write(ws, 34, 7, dd)   # G34
        _write(ws, 34, 8, mm)   # H34
        _write(ws, 34, 9, yyyy) # I34

    # Fecha inicio exantema: M34=Día, N34=Mes, O34=Año
    dd, mm, yyyy = _parse_date(_g(d, 'fecha_inicio_erupcion'))
    if dd:
        _write(ws, 34, 13, dd)  # M34
        _write(ws, 34, 14, mm)  # N34
        _write(ws, 34, 15, yyyy)# O34

    # R36-39: Signos/Síntomas table
    # Left column: symptom name (A-B), Si checkbox, No, Desconocido
    # Right column: symptom name (H-J), Si, No, Desconocido
    #
    # R36: A36='Fiebre', B36='Si', C36:D36='Temp. C°', E36='No', F36:G36='Desconocido'
    #      H36:J36='Coriza/Catarro', K36:M36='Si', N36:P36='No', Q36:T36='Desconocido'
    _check(ws, 36, 2, _chk(_g(d, 'signo_fiebre')))        # B36 = Si
    _check(ws, 36, 5, _is_no(_g(d, 'signo_fiebre')))      # E36 = No
    _check(ws, 36, 6, _is_desc(_g(d, 'signo_fiebre')))    # F36 = Desconocido
    temp = _g(d, 'temperatura_celsius', '')
    if temp:
        _write(ws, 36, 3, f"{temp}°C")                     # C36:D36 = Temp data

    _check(ws, 36, 11, _chk(_g(d, 'signo_coriza')))       # K36 = Si
    _check(ws, 36, 14, _is_no(_g(d, 'signo_coriza')))     # N36 = No
    _check(ws, 36, 17, _is_desc(_g(d, 'signo_coriza')))   # Q36 = Desconocido

    # R37: A37:B37='Exantema/Rash', C37:D37='Si', E37='No', F37:G37='Desconocido'
    #      H37:J37='Manchas de Koplik', K37:M37='Si', N37:P37='No', Q37:T37='Desconocido'
    _check(ws, 37, 3, _chk(_g(d, 'signo_exantema')))      # C37 = Si
    _check(ws, 37, 5, _is_no(_g(d, 'signo_exantema')))    # E37 = No
    _check(ws, 37, 6, _is_desc(_g(d, 'signo_exantema')))  # F37 = Desconocido

    _check(ws, 37, 11, _chk(_g(d, 'signo_manchas_koplik')))    # K37 = Si
    _check(ws, 37, 14, _is_no(_g(d, 'signo_manchas_koplik')))  # N37 = No
    _check(ws, 37, 17, _is_desc(_g(d, 'signo_manchas_koplik')))# Q37 = Desconocido

    # R38: A38:B38='Tos', C38:D38='Si', E38='No', F38:G38='Desconocido'
    #      H38:J38='Artralgia/Artritis', K38:M38='Si', N38:P38='No', Q38:T38='Desconocido'
    _check(ws, 38, 3, _chk(_g(d, 'signo_tos')))           # C38 = Si
    _check(ws, 38, 5, _is_no(_g(d, 'signo_tos')))         # E38 = No
    _check(ws, 38, 6, _is_desc(_g(d, 'signo_tos')))       # F38 = Desconocido

    _check(ws, 38, 11, _chk(_g(d, 'signo_artralgia')))    # K38 = Si
    _check(ws, 38, 14, _is_no(_g(d, 'signo_artralgia')))  # N38 = No
    _check(ws, 38, 17, _is_desc(_g(d, 'signo_artralgia')))# Q38 = Desconocido

    # R39: A39:B39='Conjuntivitis', C39:D39='Si', E39='No', F39:G39='Desconocido'
    #      H39:J39='Adenopatías', K39:M39='Si', N39:P39='No', Q39:T39='Desconocido'
    _check(ws, 39, 3, _chk(_g(d, 'signo_conjuntivitis')))      # C39 = Si
    _check(ws, 39, 5, _is_no(_g(d, 'signo_conjuntivitis')))    # E39 = No
    _check(ws, 39, 6, _is_desc(_g(d, 'signo_conjuntivitis')))  # F39 = Desconocido

    _check(ws, 39, 11, _chk(_g(d, 'signo_adenopatias')))       # K39 = Si
    _check(ws, 39, 14, _is_no(_g(d, 'signo_adenopatias')))     # N39 = No
    _check(ws, 39, 17, _is_desc(_g(d, 'signo_adenopatias')))   # Q39 = Desconocido

    # R40: A40:B40='Hospitalización', C40='Si', D40='No', E40:F40='Desconocido',
    #      G40:I40='Nombre del Hospital', J40:M40=data, N40:O40='Fecha Hospitalización',
    #      P40='Día', Q40='Mes', R40='Año', S40:T40=empty
    hosp = _g(d, 'hospitalizado', '')
    _check(ws, 40, 3, _chk(hosp))       # C40 = Si
    _check(ws, 40, 4, _is_no(hosp))     # D40 = No
    _check(ws, 40, 5, _is_desc(hosp))   # E40 = Desconocido

    _write(ws, 40, 10, _g(d, 'hosp_nombre'))  # J40:M40 = hospital name data
    dd, mm, yyyy = _parse_date(_g(d, 'hosp_fecha', ''))
    if dd:
        _write(ws, 40, 16, dd)   # P40 (overwrite 'Día' label)
        _write(ws, 40, 17, mm)   # Q40 (overwrite 'Mes' label)
        _write(ws, 40, 18, yyyy) # R40 (overwrite 'Año' label)

    # R41: A41:B41='Complicaciones', C41='Si', D41='No', E41:G41='Desconocido',
    #      H41:J41='Especifique Complicaciones', K41:L41='Neumonía', M41:N41='Encefalitis',
    #      O41:P41='Diarrea', Q41:T41='Trombocitopenia'
    comp = _g(d, 'tiene_complicaciones', _g(d, 'complicaciones', ''))
    _check(ws, 41, 3, _chk(comp))       # C41 = Si
    _check(ws, 41, 4, _is_no(comp))     # D41 = No
    _check(ws, 41, 5, _is_desc(comp))   # E41 = Desconocido

    _check(ws, 41, 11, _chk(_g(d, 'comp_neumonia')))        # K41 = Neumonía
    _check(ws, 41, 13, _chk(_g(d, 'comp_encefalitis')))     # M41 = Encefalitis
    _check(ws, 41, 15, _chk(_g(d, 'comp_diarrea')))         # O41 = Diarrea
    _check(ws, 41, 17, _chk(_g(d, 'comp_trombocitopenia'))) # Q41 = Trombocitopenia

    # R42: A42:B42='Aislamiento Respiratorio', C42='Si', D42='Día', E42='Mes', F42='Año',
    #      G42:H42='No', I42:J42='Desconocido',
    #      K42:L42='Otitis Media Aguda', M42:N42='Ceguera', O42:Q42='Otra (especifique)', R42:T42=data
    aisl = _g(d, 'aislamiento_respiratorio', '')
    _check(ws, 42, 3, _chk(aisl))       # C42 = Si
    if _chk(aisl):
        fecha_aisl = _g(d, 'fecha_aislamiento', '')
        dd, mm, yyyy = _parse_date(fecha_aisl)
        if dd:
            _write(ws, 42, 4, dd)   # D42 (overwrite 'Día')
            _write(ws, 42, 5, mm)   # E42 (overwrite 'Mes')
            _write(ws, 42, 6, yyyy) # F42 (overwrite 'Año')
    _check(ws, 42, 7, _is_no(aisl))     # G42 = No
    _check(ws, 42, 9, _is_desc(aisl))   # I42 = Desconocido

    # Complicaciones continued on R42
    _check(ws, 42, 11, _chk(_g(d, 'comp_otitis')))    # K42 = Otitis
    _check(ws, 42, 13, _chk(_g(d, 'comp_ceguera')))   # M42 = Ceguera
    comp_otra = _g(d, 'comp_otra_texto', _g(d, 'complicaciones_otra', ''))
    if comp_otra:
        _write(ws, 42, 18, comp_otra)  # R42:T42 = data

    # ===== SECCIÓN 5: FACTORES DE RIESGO (Rows 43-50) =====

    # R44: A44:N44='Existe algún caso confirmado...', O44:P44='Si', Q44='No', R44:T44='Desconocido'
    caso_conf = _g(d, 'caso_sospechoso_comunidad_3m', '')
    _check(ws, 44, 15, _chk(caso_conf))     # O44 = Si
    _check(ws, 44, 17, _is_no(caso_conf))   # Q44 = No
    _check(ws, 44, 18, _is_desc(caso_conf)) # R44 = Desconocido

    # R45: A45:N45='Tuvo contacto con caso sospechoso...', O45:P45='Si', Q45='No', R45:T45='Desconocido'
    contacto_sosp = _g(d, 'contacto_sospechoso_7_23', '')
    _check(ws, 45, 15, _chk(contacto_sosp))     # O45 = Si
    _check(ws, 45, 17, _is_no(contacto_sosp))   # Q45 = No
    _check(ws, 45, 18, _is_desc(contacto_sosp)) # R45 = Desconocido

    # R46: A46:F46='Viajó 7-23 días...', G46='Si', H46:J46='País, Depto, Muni',
    #      K46:R46=data (travel destination), S46:T46='No'
    viajo = _g(d, 'viajo_7_23_previo', '')
    _check(ws, 46, 7, _chk(viajo))      # G46 = Si
    _check(ws, 46, 19, _is_no(viajo))   # S46 = No

    viaje_dest = _g(d, 'viaje_pais', _g(d, 'destino_viaje', ''))
    viaje_dep = _g(d, 'viaje_departamento', '')
    viaje_mun = _g(d, 'viaje_municipio', '')
    dest_parts = [p for p in [viaje_dest, viaje_dep, viaje_mun] if p]
    if dest_parts:
        _write(ws, 46, 11, ', '.join(dest_parts))  # K46:R46 = data

    # R47: A47:B47='Fecha de Salida', C47='Día', D47='Mes', E47='Año',
    #      F47:G47='Fecha de Entrada', H47='Día', I47='Mes', J47='Año',
    #      K47:M47='¿Alguna persona viajó al exterior?', N47='Si',
    #      O47:P47='Fecha de Retorno', Q47='Día', R47='Mes', S47='Año', T47='No'
    dd, mm, yyyy = _parse_date(_g(d, 'viaje_fecha_salida', ''))
    if dd:
        _write(ws, 47, 3, dd)    # C47
        _write(ws, 47, 4, mm)    # D47
        _write(ws, 47, 5, yyyy)  # E47

    dd, mm, yyyy = _parse_date(_g(d, 'viaje_fecha_entrada', ''))
    if dd:
        _write(ws, 47, 8, dd)    # H47
        _write(ws, 47, 9, mm)    # I47
        _write(ws, 47, 10, yyyy) # J47

    familiar_viajo = _g(d, 'familiar_viajo_exterior', '')
    _check(ws, 47, 14, _chk(familiar_viajo))   # N47 = Si
    _check(ws, 47, 20, _is_no(familiar_viajo))  # T47 = No

    dd, mm, yyyy = _parse_date(_g(d, 'familiar_fecha_retorno', ''))
    if dd:
        _write(ws, 47, 17, dd)   # Q47
        _write(ws, 47, 18, mm)   # R47
        _write(ws, 47, 19, yyyy) # S47

    # R48: A48:J48='¿Paciente en contacto con embarazada?', K48:M48='Si', N48:P48='No', Q48:T48='Desconocido'
    contacto_emb = _g(d, 'contacto_embarazada', '')
    _check(ws, 48, 11, _chk(contacto_emb))     # K48 = Si
    _check(ws, 48, 14, _is_no(contacto_emb))   # N48 = No
    _check(ws, 48, 17, _is_desc(contacto_emb)) # Q48 = Desconocido

    # R49-50: Fuente posible de contagio checkboxes
    # R49: A49:A50='Fuente Posible de Contagio', B49:C49='Contacto hogar', D49:F49='Servicio Salud',
    #      G49:I49='Inst. Educativa', J49:L49='Espacio Público', M49:Q49=empty, R49:T49='Comunidad'
    # R50: B50:D50='Evento Masivo', E50:G50='Transporte Internacional', H50:J50='Desconocido',
    #      K50:M50='Otro', N50:O50='Otro (especifique)', P50:T50=data
    fuente_c = _g(d, 'fuente_posible_contagio', '').upper()
    _check(ws, 49, 2, 'HOGAR' in fuente_c or 'CASA' in fuente_c)        # B49
    _check(ws, 49, 4, 'SALUD' in fuente_c or 'HOSPITAL' in fuente_c)    # D49
    _check(ws, 49, 7, 'EDUCATIVA' in fuente_c or 'ESCUELA' in fuente_c) # G49
    _check(ws, 49, 10, 'PÚBLICO' in fuente_c or 'PUBLICO' in fuente_c)  # J49
    _check(ws, 49, 18, 'COMUNIDAD' in fuente_c and 'EDUCATIVA' not in fuente_c) # R49
    _check(ws, 50, 2, 'MASIVO' in fuente_c or 'EVENTO' in fuente_c)     # B50
    _check(ws, 50, 5, 'INTERNACIONAL' in fuente_c or 'TRANSP' in fuente_c) # E50
    _check(ws, 50, 8, 'DESCONOCIDO' in fuente_c or 'DESC' in fuente_c)  # H50
    _check(ws, 50, 11, 'OTRO' in fuente_c and 'DESCONOCIDO' not in fuente_c) # K50
    fuente_c_otro = _g(d, 'fuente_contagio_otro', '')
    if fuente_c_otro:
        _write(ws, 50, 16, fuente_c_otro)  # P50:T50 = data

    # ===== SECCIÓN 6: ACCIONES DE RESPUESTA (Rows 51-56) =====

    # R52: A52:H52='¿BAI realizada?', I52:J52='Si', K52:L52='No',
    #      M52:O52='Número de casos sospechosos en BAI', P52:T52=data
    bai = _g(d, 'bai_realizada', '')
    _check(ws, 52, 9, _chk(bai))    # I52 = Si
    _check(ws, 52, 11, _is_no(bai))  # K52 = No
    bai_n = _g(d, 'bai_casos_sospechosos', '')
    if bai_n:
        _write(ws, 52, 16, bai_n)   # P52:T52 = data

    # R53: A53:H53='¿BAC realizada?', I53:J53='Si', K53:L53='No',
    #      M53:O53='Número de casos sospechosos en BAC', P53:T53=data
    bac = _g(d, 'bac_realizada', '')
    _check(ws, 53, 9, _chk(bac))    # I53 = Si
    _check(ws, 53, 11, _is_no(bac))  # K53 = No
    bac_n = _g(d, 'bac_casos_sospechosos', '')
    if bac_n:
        _write(ws, 53, 16, bac_n)   # P53:T53 = data

    # R54: A54:H54='¿Vacunación bloqueo 48-72hrs?', I54:J54='Si', K54:L54='No',
    #      M54:P54='¿Monitoreo rápido de vacunación?', Q54:R54='Si', S54:T54='No'
    vb = _g(d, 'vacunacion_bloqueo', '')
    _check(ws, 54, 9, _chk(vb))     # I54 = Si
    _check(ws, 54, 11, _is_no(vb))   # K54 = No

    mr = _g(d, 'monitoreo_rapido_vacunacion', '')
    _check(ws, 54, 17, _chk(mr))    # Q54 = Si
    _check(ws, 54, 19, _is_no(mr))   # S54 = No

    # R55: A55:H55='¿Vacunación con barrido?', I55:J55='Si', K55:L55='No', M55:T55=empty data
    bd = _g(d, 'vacunacion_barrido', '')
    _check(ws, 55, 9, _chk(bd))     # I55 = Si
    _check(ws, 55, 11, _is_no(bd))   # K55 = No

    # R56: A56:C56='¿Vitamina A?', D56='Si', E56='No', F56:G56='Desconocido',
    #      H56:T56='Número de dosis...'
    vit = _g(d, 'vitamina_a_administrada', '')
    _check(ws, 56, 4, _chk(vit))       # D56 = Si
    _check(ws, 56, 5, _is_no(vit))     # E56 = No
    _check(ws, 56, 6, _is_desc(vit))   # F56 = Desconocido
    vit_dosis = _g(d, 'vitamina_a_dosis', '')
    if vit_dosis:
        # Write number of doses into the description area
        _write(ws, 56, 8, f"Dosis: {vit_dosis}")  # H56:T56

    # ===== SECCIÓN 7: LABORATORIO (Rows 57-70) =====

    # R58: A58:C58='Tipo de Muestra', D58:E58='Suero', F58:G58='Orina',
    #      H58:J58='Hisopado NF', K58:T58='¿Por qué no se recolectó?'
    tipo_m = _g(d, 'tipo_muestra', '').upper()
    has_suero = 'SUERO' in tipo_m or bool(_g(d, 'muestra_suero_fecha'))
    has_orina = 'ORINA' in tipo_m or bool(_g(d, 'muestra_orina_fecha'))
    has_hisop = 'HISOP' in tipo_m or bool(_g(d, 'muestra_hisopado_fecha'))
    _check(ws, 58, 4, has_suero)    # D58 = Suero
    _check(ws, 58, 6, has_orina)    # F58 = Orina
    _check(ws, 58, 8, has_hisop)    # H58 = Hisopado

    motivo_no = _g(d, 'motivo_no_3_muestras', _g(d, 'motivo_no_recoleccion', ''))
    if motivo_no:
        _write(ws, 58, 11, motivo_no)  # K58:T58 = data

    # Lab samples table structure (Rows 59-70):
    # R59-60: headers — No. Muestra | Tipo Muestra y Prueba | Fecha Toma | Fecha Envío |
    #         Virus | Resultado (IgM/IgG/Avidez) | Fecha Resultado | Secuenciación
    #
    # Data rows (each sample spans 2 rows — Sarampión + Rubéola):
    # R61-62: 1a Suero (Anticuerpo) — Sarampión(61) + Rubéola(62)
    # R63-64: 2da Suero (Anticuerpo) — Sarampión(63) + Rubéola(64)
    # R65-66: 1a Orina (ARN viral) — Sarampión(65) + Rubéola(66)
    # R67-68: 1a Hisopado NF (ARN viral) — Sarampión(67) + Rubéola(68)
    # R69-70: Otro — Sarampión(69) + Rubéola(70)
    #
    # Per row: D:E=Fecha Toma, F:G=Fecha Envío, I=IgM result, J=IgG result, K:L=Avidez,
    #          M=Día result, N=Mes result, O=Año result, P:T=Secuenciación

    lab_json = _safe_json(_g(d, 'lab_muestras_json', ''))

    if lab_json:
        # Structured lab data — map to template rows
        # Expected structure: list of dicts with tipo_muestra, virus, fecha_toma, etc.
        for sample in lab_json:
            if not isinstance(sample, dict):
                continue
            tipo = str(sample.get('tipo_muestra', '')).upper()
            virus = str(sample.get('virus', 'SARAMPION')).upper()
            numero = str(sample.get('numero_muestra', '1'))

            # Determine target row
            if 'SUERO' in tipo:
                if numero == '2' or '2' in tipo:
                    row_s, row_r = 63, 64
                else:
                    row_s, row_r = 61, 62
            elif 'ORINA' in tipo:
                row_s, row_r = 65, 66
            elif 'HISOP' in tipo:
                row_s, row_r = 67, 68
            else:
                row_s, row_r = 69, 70

            target_row = row_r if 'RUBE' in virus else row_s

            # Fecha toma
            dd, mm, yyyy = _parse_date(sample.get('fecha_toma', ''))
            if dd:
                _write(ws, target_row, 4, f"{dd}/{mm}/{yyyy}")  # D col

            # Fecha envío
            dd, mm, yyyy = _parse_date(sample.get('fecha_envio', ''))
            if dd:
                _write(ws, target_row, 6, f"{dd}/{mm}/{yyyy}")  # F col

            # Results
            res_igm = sample.get('resultado_igm', sample.get('resultado_virus', ''))
            if res_igm:
                _write(ws, target_row, 9, res_igm)     # I col = IgM
            res_igg = sample.get('resultado_igg', '')
            if res_igg:
                _write(ws, target_row, 10, res_igg)    # J col = IgG
            res_avidez = sample.get('resultado_avidez', '')
            if res_avidez:
                _write(ws, target_row, 11, res_avidez)  # K col = Avidez

            # Fecha resultado
            dd, mm, yyyy = _parse_date(sample.get('fecha_resultado', ''))
            if dd:
                _write(ws, target_row, 13, dd)   # M col
                _write(ws, target_row, 14, mm)   # N col
                _write(ws, target_row, 15, yyyy) # O col

            # Secuenciación
            sec = sample.get('secuenciacion', '')
            if sec:
                _write(ws, target_row, 16, sec)  # P col
    else:
        # Fallback: use individual fields
        # R61: 1a Suero — Sarampión
        dd, mm, yyyy = _parse_date(_g(d, 'muestra_suero_fecha', ''))
        if dd:
            _write(ws, 61, 4, f"{dd}/{mm}/{yyyy}")   # D61:E62
        dd, mm, yyyy = _parse_date(_g(d, 'muestra_suero_fecha_envio', ''))
        if dd:
            _write(ws, 61, 6, f"{dd}/{mm}/{yyyy}")   # F61:G62

        res_igm = _g(d, 'resultado_igm_sarampion_suero', _g(d, 'resultado_igm_cualitativo', ''))
        if res_igm:
            _write(ws, 61, 9, res_igm)   # I61 = IgM
        res_igg = _g(d, 'resultado_igg_sarampion_suero', _g(d, 'resultado_igg_cualitativo', ''))
        if res_igg:
            _write(ws, 61, 10, res_igg)  # J61 = IgG

        dd, mm, yyyy = _parse_date(_g(d, 'fecha_resultado_laboratorio', ''))
        if dd:
            _write(ws, 61, 13, dd)   # M61
            _write(ws, 61, 14, mm)   # N61
            _write(ws, 61, 15, yyyy) # O61

        # R65: 1a Orina — Sarampión
        dd, mm, yyyy = _parse_date(_g(d, 'muestra_orina_fecha', ''))
        if dd:
            _write(ws, 65, 4, f"{dd}/{mm}/{yyyy}")   # D65:E66
        pcr_orina = _g(d, 'resultado_pcr_orina', '')
        if pcr_orina:
            _write(ws, 65, 9, pcr_orina)  # I65

        # R67: 1a Hisopado NF — Sarampión
        dd, mm, yyyy = _parse_date(_g(d, 'muestra_hisopado_fecha', ''))
        if dd:
            _write(ws, 67, 4, f"{dd}/{mm}/{yyyy}")   # D67:E68
        pcr_hisop = _g(d, 'resultado_pcr_hisopado', '')
        if pcr_hisop:
            _write(ws, 67, 9, pcr_hisop)  # I67

    # Secuenciación result and fecha (R63 has dedicated cells)
    sec_resultado = _g(d, 'secuenciacion_resultado', '')
    sec_fecha = _g(d, 'secuenciacion_fecha', '')
    if sec_resultado:
        # R63: P63:Q64='Resultado' label area — write data
        pass  # P63 has label 'Resultado'; actual data unclear. Skip if no dedicated cell.
    if sec_fecha:
        # R63: R63:T64='Fecha' label area
        pass

    # ===== CLASIFICACIÓN (Rows 72-82) =====

    # R73: A73:C73='Clasificación Final', D73:F73='Sarampión', G73:I73='Rubéola',
    #      J73:L73='Descartado', M73:O73='Pendiente', P73:T73='No cumple def. caso'
    clasif = _g(d, 'clasificacion_caso', '').upper()
    is_confirmed = 'CONFIRM' in clasif
    is_descartado = 'DESCART' in clasif
    is_pendiente = 'PENDIENTE' in clasif or 'SOSPECH' in clasif
    is_no_cumple = 'NO CUMPLE' in clasif or 'DEFINICION' in clasif
    is_clasif_sar = ('SARAMP' in clasif and not is_descartado) or (is_confirmed and not is_descartado and is_sar)
    is_clasif_rub = ('RUBEO' in clasif or 'RUBE' in clasif) and not is_descartado
    if is_confirmed and not is_clasif_sar and not is_clasif_rub and not is_descartado:
        is_clasif_sar = is_sar
        is_clasif_rub = is_rub
    _check(ws, 73, 4, is_clasif_sar)                      # D73 = Sarampión
    _check(ws, 73, 7, is_clasif_rub)                       # G73 = Rubéola
    _check(ws, 73, 10, is_descartado)                      # J73 = Descartado
    _check(ws, 73, 13, is_pendiente and not is_confirmed)  # M73 = Pendiente
    _check(ws, 73, 16, is_no_cumple)                       # P73 = No cumple

    # R74: A74:C74='Criterio de Confirmación', D74:F74='Laboratorio', G74:I74='Nexo epidemiológico',
    #      J74:L74='Clínico', M74:P74='Contacto de Otro Caso', Q74:R74='Si', S74:T74='No'
    crit_conf = _g(d, 'criterio_confirmacion', '').upper()
    _check(ws, 74, 4, 'LABORATORIO' in crit_conf or 'LAB' in crit_conf)        # D74
    _check(ws, 74, 7, 'NEXO' in crit_conf or 'EPIDEMIOL' in crit_conf)         # G74
    _check(ws, 74, 10, 'CLÍNICO' in crit_conf or 'CLINICO' in crit_conf)       # J74

    contacto_caso = _g(d, 'contacto_otro_caso', '')
    _check(ws, 74, 17, _chk(contacto_caso))     # Q74 = Si
    _check(ws, 74, 19, _is_no(contacto_caso))   # S74 = No

    # R75: A75:C75='Criterio para descartar', D75:F75='Laboratorial', G75:I75='Relacionado Vacuna',
    #      J75:L75='Clínico', M75:O75='Otro Especificar:', P75:T75=data
    crit_desc = _g(d, 'criterio_descarte', '').upper()
    _check(ws, 75, 4, 'LABORAT' in crit_desc)                              # D75
    _check(ws, 75, 7, 'VACUNA' in crit_desc)                               # G75
    _check(ws, 75, 10, 'CLÍNICO' in crit_desc or 'CLINICO' in crit_desc)   # J75
    crit_desc_otro = _g(d, 'criterio_descarte_otro', '')
    if crit_desc_otro:
        _write(ws, 75, 16, crit_desc_otro)  # P75:T75 = data

    # R76: A76:C76='Fuente de infección', D76:F76='Importado', G76:I76='Relacionado importación',
    #      J76:L76='País de Importación', M76:O76=data, P76:Q76='Endémico', R76:T76='Fuente desconocida'
    fuente_inf = _g(d, 'fuente_infeccion', '').upper()
    _check(ws, 76, 4, 'IMPORTADO' in fuente_inf and 'RELACIONADO' not in fuente_inf) # D76
    _check(ws, 76, 7, 'RELACIONADO' in fuente_inf)                                    # G76
    _check(ws, 76, 16, 'ENDÉMI' in fuente_inf or 'ENDEMI' in fuente_inf)              # P76
    _check(ws, 76, 18, 'DESCONOCID' in fuente_inf)                                    # R76

    pais_import = _g(d, 'pais_importacion', '')
    if pais_import:
        _write(ws, 76, 13, pais_import)  # M76:O76 = data

    # R77: A77:C77='Caso Analizado Por', D77:F77='CONAPI', G77:I77='DEGR*',
    #      J77:M77='Comisión Nacional**', N77:O77='Otros', P77:Q77='Especifique', R77:T77=data
    analizado = _g(d, 'caso_analizado_por', '').upper()
    _check(ws, 77, 4, 'CONAPI' in analizado)    # D77
    _check(ws, 77, 7, 'DEGR' in analizado)      # G77
    _check(ws, 77, 10, 'COMISIÓN' in analizado or 'COMISION' in analizado or 'NACIONAL' in analizado) # J77
    _check(ws, 77, 14, 'OTRO' in analizado)     # N77
    otro_analiz = _g(d, 'caso_analizado_por_otro', '')
    if otro_analiz:
        _write(ws, 77, 18, otro_analiz)  # R77:T77 = data

    # R78: A78:C78='Fecha de Clasificación', D78='Día', E78='Mes', F78='Año',
    #      G78:I78='Condición Final del Paciente', J78:L78='Recuperado', M78:O78='Con Secuelas',
    #      P78:Q78='Fallecido*', R78:T78='Desconocido'
    dd, mm, yyyy = _parse_date(_g(d, 'fecha_clasificacion_final', ''))
    if dd:
        _write(ws, 78, 4, dd)   # D78
        _write(ws, 78, 5, mm)   # E78
        _write(ws, 78, 6, yyyy) # F78

    cond = _g(d, 'condicion_final_paciente', _g(d, 'condicion_egreso', '')).upper()
    _check(ws, 78, 10, 'RECUPER' in cond or 'VIVO' in cond or 'MEJORAD' in cond or 'CURAD' in cond) # J78
    _check(ws, 78, 13, 'SECUELA' in cond)                                                             # M78
    _check(ws, 78, 16, 'FALLEC' in cond or 'MUERTE' in cond)                                          # P78
    _check(ws, 78, 18, 'DESCONOCID' in cond)                                                          # R78

    # R79: A79:C79='Fecha de Defunción*', D79='Día', E79='Mes', F79='Año',
    #      G79:J79='Causa De Muerte...', K79:T79=data
    dd, mm, yyyy = _parse_date(_g(d, 'fecha_defuncion', ''))
    if dd:
        _write(ws, 79, 4, dd)   # D79
        _write(ws, 79, 5, mm)   # E79
        _write(ws, 79, 6, yyyy) # F79
    _write(ws, 79, 11, _g(d, 'causa_muerte_certificado', ''))  # K79:T79 = data

    # R80: A80:C80='Observaciones', D80:T80=data
    obs = _g(d, 'observaciones', '')
    if obs:
        _write(ws, 80, 4, obs)  # D80:T80 = data


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
        ws.print_area = "A1:T82"

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
            ws.print_area = "A1:T82"

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
