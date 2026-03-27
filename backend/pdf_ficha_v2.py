"""
PDF Generator for MSPAS Sarampion/Rubeola Form — Excel Template Version.
Uses Excel template + LibreOffice headless for pixel-perfect output.

The template is the official MSPAS 2026 form in Excel format.
We fill in cell values with patient data, then convert to PDF.

Cell placement strategy:
  - Template has LABEL cells (pre-filled) and DATA cells (empty).
  - We NEVER overwrite label cells — only write into empty cells.
  - For merged ranges, write to the top-left cell.
  - Checkbox fields: write "X" in the empty cell next to the matching option.

Public API:
    generar_ficha_v2_pdf(data: dict) -> bytes
    generar_fichas_v2_bulk(records: list, merge: bool = True) -> bytes
"""
import io
import json
import os
import shutil
import subprocess
import tempfile
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), "assets", "ficha_sarampion_template.xlsx"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _g(data: dict, key: str, default: str = "") -> str:
    """Get value from data dict, safely converting to stripped string."""
    val = data.get(key)
    if val is None:
        return default
    s = str(val).strip()
    if s.upper() in ("NONE", "NULL", "NAN"):
        return default
    return s


def _parse_date(date_str: str) -> tuple[str, str, str]:
    """Parse date string and return (dia, mes, anio) as zero-padded strings."""
    if not date_str:
        return ("", "", "")
    date_str = str(date_str).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%d-%m-%Y"):
        try:
            dt = datetime.strptime(date_str[:10], fmt)
            return (f"{dt.day:02d}", f"{dt.month:02d}", str(dt.year))
        except ValueError:
            continue
    return ("", "", "")


def _chk(value) -> bool:
    """Return True if value represents an affirmative/yes."""
    if value is None:
        return False
    s = str(value).strip().upper()
    return s in ("SI", "SÍ", "S", "1", "TRUE", "X", "YES")


def _is_no(value) -> bool:
    """Return True if value is explicitly 'No'."""
    if value is None:
        return False
    return str(value).strip().upper() in ("NO", "N", "0", "FALSE")


def _is_desc(value) -> bool:
    """Return True if value is 'Desconocido'."""
    if value is None:
        return False
    return str(value).strip().upper() in ("DESCONOCIDO", "DESC", "D", "UNKNOWN")


def _safe_json_loads(val):
    """Parse JSON string safely, return list or original value."""
    if not val:
        return []
    if isinstance(val, (list, dict)):
        return val
    try:
        return json.loads(val)
    except (json.JSONDecodeError, TypeError):
        return []


# ---------------------------------------------------------------------------
# Excel cell constants — derived from template analysis
# ---------------------------------------------------------------------------
# Template: Hoja1, A1:P209, 14 main columns (A-N), col O-P unused
# Column index: A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8,
#               I=9, J=10, K=11, L=12, M=13, N=14
#
# Pattern: Labels are in pre-filled cells; data goes in EMPTY cells.
# For Section I rows 11-13, labels fill A:H and I:N — data must be
# appended after the label text in the same cell (no separate data cell).
# For Section II, R19 has label, R20 col A has EMPTY merged cell for name.
# Checkboxes: each option has a label cell and an adjacent EMPTY cell for "X".


def _fill_hoja1(ws, data: dict):
    """Fill Hoja1 of the Excel template with patient data.

    Only writes into EMPTY cells or appends to label cells where
    there is no separate data entry cell.
    """
    # Shorthand
    g = lambda key, default="": _g(data, key, default)

    # ===================================================================
    # HEADER: Diagnostico de sospecha (Row 6-8)
    # ===================================================================
    # R6: C3=EMPTY(checkbox Sarampion), C7=EMPTY(Rubeola), C10=EMPTY(Altamente sosp.)
    # R7: C3=EMPTY(Sarampion+Dengue checkbox), C10=EMPTY(specify)
    # R8: C3=EMPTY(Sarampion+Otra checkbox), C11=EMPTY(specify)

    diag = g("diagnostico_sospecha", g("diagnostico_registrado"))
    du = diag.upper() if diag else ""

    if "DENGUE" in du or "ARBOVIR" in du:
        ws.cell(row=7, column=3).value = "X"
        ws.cell(row=7, column=10).value = g("diagnostico_sospecha_otro", g("diagnostico_otro"))
    elif "OTRA" in du or "FEBRIL" in du:
        ws.cell(row=8, column=3).value = "X"
        ws.cell(row=8, column=11).value = g("diagnostico_sospecha_otro", g("diagnostico_otro"))
    elif "RUBEOLA" in du or "RUBÉOLA" in du:
        ws.cell(row=6, column=7).value = "X"
    elif "ALTAMENTE" in du:
        ws.cell(row=6, column=10).value = "X"
    else:
        # Default: Sarampion
        ws.cell(row=6, column=3).value = "X"

    # Also check secondary diagnoses
    if ("RUBEOLA" in du or "RUBÉOLA" in du) and "SARAMPION" in du:
        ws.cell(row=6, column=3).value = "X"
        ws.cell(row=6, column=7).value = "X"

    # ===================================================================
    # SECTION I: Informacion de la institucion (Row 10-17)
    # ===================================================================
    # R11: A11:H11=label "DDRISS:", I11:N11=label "Nombre investigador:"
    # No separate data cells — we must append to the label cells.

    # DDRISS — append to A11 label
    ddriss = g("area_salud_mspas", g("unidad_medica"))
    if ddriss:
        label = ws.cell(row=11, column=1).value or ""
        ws.cell(row=11, column=1).value = f"{label} {ddriss}"

    # Nombre investigador — append to I11
    invest = g("nom_responsable")
    if invest:
        label = ws.cell(row=11, column=9).value or ""
        ws.cell(row=11, column=9).value = f"{label} {invest}"

    # DMS — append to A12
    distrito = g("distrito_salud_mspas")
    if distrito:
        label = ws.cell(row=12, column=1).value or ""
        ws.cell(row=12, column=1).value = f"{label} {distrito}"

    # Cargo investigador — append to I12
    cargo = g("cargo_responsable")
    if cargo:
        label = ws.cell(row=12, column=9).value or ""
        ws.cell(row=12, column=9).value = f"{label} {cargo}"

    # Institucion — append to A13
    institucion = g("servicio_salud_mspas", g("unidad_medica", g("centro_externo")))
    if institucion:
        label = ws.cell(row=13, column=1).value or ""
        ws.cell(row=13, column=1).value = f"{label} {institucion}"

    # Telefono/correo investigador — append to I13
    tel = g("telefono_responsable")
    correo = g("correo_responsable")
    contacto = " / ".join(p for p in [tel, correo] if p)
    if contacto:
        label = ws.cell(row=13, column=9).value or ""
        ws.cell(row=13, column=9).value = f"{label} {contacto}"

    # R14: C9="Fecha de consulta:" [I14:J14], C11=EMPTY [K14:L14], C13="Fecha notificación:", C14=EMPTY
    d, m, y = _parse_date(g("fecha_registro_diagnostico", g("fecha_captacion")))
    if d:
        ws.cell(row=14, column=11).value = f"{d}/{m}/{y}"

    d, m, y = _parse_date(g("fecha_notificacion"))
    if d:
        ws.cell(row=14, column=14).value = f"{d}/{m}/{y}"

    # R15: Tipo institucion checkboxes
    # C1="IGSS" C2="Privado" C3="Publica" C5="Otra, especifique"
    # C4=EMPTY (for marking Otra), C7=EMPTY (for Otra text)
    es_igss = g("es_seguro_social")
    es_privado = g("establecimiento_privado")
    tipo_inst = g("unidad_medica", "").upper()

    # We mark with "X" by prepending to the existing label
    if _chk(es_igss) or "IGSS" in tipo_inst:
        ws.cell(row=15, column=1).value = "X IGSS"
    elif _chk(es_privado):
        ws.cell(row=15, column=2).value = "X Privado"
    elif "PUBLIC" in tipo_inst or "MSPAS" in tipo_inst:
        ws.cell(row=15, column=3).value = "X Pública"
    else:
        # Default IGSS since this is IGSS system
        ws.cell(row=15, column=1).value = "X IGSS"

    # R15: Fecha investigacion — append to I15
    d, m, y = _parse_date(g("fecha_inicio_investigacion", g("fecha_visita_domiciliaria")))
    if d:
        label = ws.cell(row=15, column=9).value or ""
        ws.cell(row=15, column=9).value = f"{label} {d}/{m}/{y}"

    # R16-17: Fuente de notificacion — mark with "X" prefix on matching label
    fuente = g("fuente_notificacion", "").upper()
    if "SERVICIO" in fuente or "SALUD" in fuente:
        ws.cell(row=17, column=1).value = "  X       Servicio de salud"
    if "INVESTIGACION" in fuente or "CONTACTO" in fuente:
        ws.cell(row=16, column=3).value = "X Investigación de contactos"
    if "LABORATORIO" in fuente:
        ws.cell(row=16, column=7).value = "X Laboratorio"
    if "ACTIVA" in fuente and "INSTITUCIONAL" in fuente:
        ws.cell(row=16, column=9).value = "X Búsqueda activa institucional"
    if "ACTIVA" in fuente and "COMUNITARIA" in fuente:
        ws.cell(row=16, column=13).value = "X Búsqueda activa comunitaria"
    if "COMUNIDAD" in fuente:
        ws.cell(row=17, column=3).value = "X Caso reportado por la comunidad"
    if "AUTO" in fuente or "GRATUITO" in fuente:
        ws.cell(row=17, column=7).value = "X Autonotificación por número gratuito"
    otra_fuente = g("fuente_notificacion_otra")
    if "OTRO" in fuente or otra_fuente:
        ws.cell(row=17, column=11).value = f"X Otro: {otra_fuente}"

    # ===================================================================
    # SECTION II: Informacion del paciente (Row 18-29)
    # ===================================================================

    # R19: A19:H19=label, I19:J19=label, K19:N19=label with checkboxes inline
    # R20: A20:H20=EMPTY (patient name goes here!)
    nombre_completo = g("nombre_apellido")
    if not nombre_completo:
        nombres = g("nombres")
        apellidos = g("apellidos")
        nombre_completo = f"{nombres} {apellidos}".strip()
    ws.cell(row=20, column=1).value = nombre_completo

    # Sexo — R19 K11:N19 has "Masculino        Femenino       Migrantes"
    # We need to mark with X. Since it's one merged cell, rewrite with marks.
    sexo = g("sexo", "").upper()
    migrante = _chk(g("es_migrante"))
    m_mark = " X" if sexo in ("M", "MASCULINO", "HOMBRE") else "  "
    f_mark = " X" if sexo in ("F", "FEMENINO", "MUJER") else "  "
    mig_mark = " X" if migrante else "  "
    ws.cell(row=19, column=11).value = f"Masculino{m_mark}   Femenino{f_mark}   Migrantes{mig_mark}"

    # R20: Embarazada — I-N area
    # C9=label "Embarazada: Si No", C10-12=EMPTY, C13=label "Trimestre", C14=EMPTY
    embarazada = g("esta_embarazada")
    if _chk(embarazada):
        ws.cell(row=20, column=9).value = "Embarazada:    X Si                No"
    elif _is_no(embarazada):
        ws.cell(row=20, column=9).value = "Embarazada:         Si           X No"

    trimestre = g("trimestre_embarazo", g("semanas_embarazo"))
    if trimestre:
        ws.cell(row=20, column=14).value = trimestre

    # R21: Tipo identificacion
    # A21:B21=label "Tipo de identificacion:", C3="CUI", C4-5=EMPTY, C6="CUI madre/padre", C7-8=EMPTY
    # I21:N21=label "Pais de residencia:"
    tipo_id = g("tipo_identificacion", "").upper()
    num_id = g("numero_identificacion", g("afiliacion"))

    if "PASAPORTE" in tipo_id:
        ws.cell(row=22, column=1).value = "          X    Pasaporte"
    elif "MADRE" in tipo_id or "PADRE" in tipo_id:
        ws.cell(row=21, column=7).value = "X"
        ws.cell(row=21, column=8).value = num_id
    elif "OTRO" in tipo_id:
        ws.cell(row=22, column=3).value = f"X Otro: {g('tipo_identificacion')}"
    else:
        # Default: CUI — mark C4 with X
        ws.cell(row=21, column=4).value = "X"
        ws.cell(row=21, column=5).value = num_id

    # Pais residencia — append to I21 label
    pais = g("pais_residencia", "Guatemala")
    if pais:
        label = ws.cell(row=21, column=9).value or ""
        ws.cell(row=21, column=9).value = f"{label} {pais}"

    # R22: Departamento — append to I22
    depto = g("departamento_residencia")
    if depto:
        label = ws.cell(row=22, column=9).value or ""
        ws.cell(row=22, column=9).value = f"{label} {depto}"

    # R23: No. identificacion — append to A23; Municipio — append to I23
    if num_id:
        label = ws.cell(row=23, column=1).value or ""
        ws.cell(row=23, column=1).value = f"{label} {num_id}"

    muni = g("municipio_residencia")
    if muni:
        label = ws.cell(row=23, column=9).value or ""
        ws.cell(row=23, column=9).value = f"{label} {muni}"

    # R24: Fecha nacimiento — append to A24; Lugar poblado — append to I24
    d_nac, m_nac, y_nac = _parse_date(g("fecha_nacimiento"))
    if d_nac:
        label = ws.cell(row=24, column=1).value or ""
        ws.cell(row=24, column=1).value = f"{label} {d_nac}/{m_nac}/{y_nac}"

    poblado = g("poblado")
    if poblado:
        label = ws.cell(row=24, column=9).value or ""
        ws.cell(row=24, column=9).value = f"{label} {poblado}"

    # R25-26: Date parts and age — use R26 EMPTY cells for values
    # R25 has labels: C1="Dia", C2="Mes", C3="Año", C6="Años", C7="Meses", C8="Dias"
    # R26 has EMPTY cells at C1, C2, C3, C5, C6, C7, C8 for values
    ws.cell(row=26, column=1).value = d_nac
    ws.cell(row=26, column=2).value = m_nac
    ws.cell(row=26, column=3).value = y_nac

    edad_a = g("edad_anios")
    edad_m = g("edad_meses")
    edad_d = g("edad_dias")
    if edad_a:
        ws.cell(row=26, column=6).value = edad_a
    if edad_m:
        ws.cell(row=26, column=7).value = edad_m
    if edad_d:
        ws.cell(row=26, column=8).value = edad_d

    # R26 C9: EMPTY merged I26:N26 — address value
    direccion = g("direccion_exacta")
    if direccion:
        ws.cell(row=26, column=9).value = direccion

    # R27: Pueblo pertenencia — C2=EMPTY (for "X" mark)
    etnia = g("pueblo_etnia", "").upper()
    if "MAYA" in etnia:
        ws.cell(row=27, column=2).value = "X"
    elif "XINCA" in etnia:
        ws.cell(row=27, column=5).value = "X Xinca"
    elif "GARIFUNA" in etnia or "GARÍFUNA" in etnia:
        ws.cell(row=27, column=6).value = "X Garifuna"
    elif "LADINO" in etnia or "MESTIZO" in etnia:
        ws.cell(row=27, column=7).value = "X Ladino/Mestizo"

    # Nombre encargado — append to I27
    encargado = g("nombre_encargado")
    if encargado:
        label = ws.cell(row=27, column=9).value or ""
        ws.cell(row=27, column=9).value = f"{label} {encargado}"

    # R28: Comunidad linguistica — append to A28; J28:N28=EMPTY for secondary data
    com_ling = g("comunidad_linguistica")
    if com_ling:
        label = ws.cell(row=28, column=1).value or ""
        ws.cell(row=28, column=1).value = f"{label}: {com_ling}"

    # R29: Ocupacion (append A29), Escolaridad (append E29), Telefono (append I29)
    ocupacion = g("ocupacion")
    if ocupacion:
        label = ws.cell(row=29, column=1).value or ""
        ws.cell(row=29, column=1).value = f"{label}: {ocupacion}"

    escolaridad = g("escolaridad")
    if escolaridad:
        label = ws.cell(row=29, column=5).value or ""
        ws.cell(row=29, column=5).value = f"{label} {escolaridad}"

    tel_pac = g("telefono_paciente", g("telefono_encargado"))
    if tel_pac:
        label = ws.cell(row=29, column=9).value or ""
        ws.cell(row=29, column=9).value = f"{label} {tel_pac}"

    # ===================================================================
    # SECTION III: Antecedentes medicos y vacunacion (Row 30-41)
    # ===================================================================

    # R31: Single merged cell A31:N31 with inline Si/No/Desconocido
    vacunado = g("vacunado")
    if _chk(vacunado):
        ws.cell(row=31, column=1).value = (
            "¿El paciente está vacunado?          X Si"
            "                             No"
            "                              Desconocido"
        )
    elif _is_no(vacunado):
        ws.cell(row=31, column=1).value = (
            "¿El paciente está vacunado?             Si"
            "                          X No"
            "                              Desconocido"
        )
    elif _is_desc(vacunado):
        ws.cell(row=31, column=1).value = (
            "¿El paciente está vacunado?             Si"
            "                             No"
            "                           X Desconocido"
        )

    # R33: SPR vaccine — F33:H34=EMPTY(dosis), I-K have date labels
    # R33 C6=EMPTY (numero dosis SPR)
    dosis_spr = g("dosis_spr", g("numero_dosis_spr"))
    if dosis_spr:
        ws.cell(row=33, column=6).value = dosis_spr

    # Date fields for SPR: R34 C9=EMPTY, C10=EMPTY, C11=EMPTY
    d, m, y = _parse_date(g("fecha_ultima_spr", g("fecha_ultima_dosis")))
    if d:
        ws.cell(row=34, column=9).value = d
        ws.cell(row=34, column=10).value = m
        ws.cell(row=34, column=11).value = y

    # Fuente info vacunacion — labels in R33-R38 column 12, we mark by prepending X
    fuente_vac = g("fuente_info_vacuna", "").upper()
    if "CARN" in fuente_vac:
        ws.cell(row=33, column=12).value = "X  Carné de vacunación"
    elif "5A" in fuente_vac or "SIGSA" in fuente_vac:
        ws.cell(row=34, column=12).value = "X  SIGSA 5a cuaderno"
    elif "5B" in fuente_vac:
        ws.cell(row=35, column=12).value = "X  SIGSA 5B otros grupos"
    elif "REGISTRO" in fuente_vac or "UNICO" in fuente_vac or "ÚNICO" in fuente_vac:
        ws.cell(row=36, column=12).value = "X  Registro único de vacunación"
    elif "VERBAL" in fuente_vac:
        ws.cell(row=37, column=12).value = "X  Verbal"

    # R35: SR vaccine — F35:H36=EMPTY(dosis)
    dosis_sr = g("dosis_sr")
    if dosis_sr:
        ws.cell(row=35, column=6).value = dosis_sr

    d, m, y = _parse_date(g("fecha_ultima_sr"))
    if d:
        # SR date uses same merged range I34:K39
        # Since these are merged cells with SPR, we use different approach
        # Actually I34:I39, J34:J39, K34:K39 are each single merged cells!
        # So they share one value. We can only show one date.
        # If SPR date was set, don't overwrite. Otherwise set it.
        if not ws.cell(row=34, column=9).value:
            ws.cell(row=34, column=9).value = d
            ws.cell(row=34, column=10).value = m
            ws.cell(row=34, column=11).value = y

    # R37: SPRV vaccine — F37:H39=EMPTY(dosis)
    dosis_sprv = g("dosis_sprv")
    if dosis_sprv:
        ws.cell(row=37, column=6).value = dosis_sprv

    d, m, y = _parse_date(g("fecha_ultima_sprv"))
    if d:
        if not ws.cell(row=34, column=9).value:
            ws.cell(row=34, column=9).value = d
            ws.cell(row=34, column=10).value = m
            ws.cell(row=34, column=11).value = y

    # R38-39: Sector vacunacion — labels at R39 C12="IGSS" C13="Publico" C14="Privado"
    sector = g("sector_vacunacion", "").upper()
    if "IGSS" in sector:
        ws.cell(row=39, column=12).value = "X IGSS"
    elif "PUBLIC" in sector:
        ws.cell(row=39, column=13).value = "X Público"
    elif "PRIVAD" in sector:
        ws.cell(row=39, column=14).value = "X Privado"

    # R40-41: Antecedentes medicos
    # R40: C2-3=EMPTY, C4="desnutricion", C5-7=EMPTY, C8="inmunocompromiso", C9-14=EMPTY
    # R41: C1=EMPTY, C2="enfermedad cronica", C3-7=EMPTY, C8="Desconocido", C9=EMPTY, C10="No"
    # Checkboxes: put "X" in the EMPTY cell before each option

    if _chk(g("antecedente_desnutricion")):
        ws.cell(row=40, column=3).value = "X"  # before C4 "desnutricion"
    if _chk(g("antecedente_inmunocompromiso")):
        ws.cell(row=40, column=7).value = "X"  # before C8 "inmunocompromiso"
    if _chk(g("antecedente_enfermedad_cronica")):
        ws.cell(row=41, column=1).value = "X"  # before C2 "enfermedad cronica"
        detalle = g("antecedentes_medicos_detalle")
        if detalle:
            ws.cell(row=41, column=3).value = detalle

    tiene_ant = g("tiene_antecedentes_medicos")
    if _is_desc(tiene_ant):
        ws.cell(row=41, column=9).value = "X"  # before C8? Actually next to Desconocido
    elif _is_no(tiene_ant):
        # "No" is at C10 — mark C9
        ws.cell(row=41, column=9).value = "X"

    # ===================================================================
    # SECTION IV: Datos clinicos (Row 42-57)
    # ===================================================================
    # Pattern for symptom rows:
    # Label row (e.g. R43 "Fiebre?") and value row (R44 "Si"/"No"/"Desconocido")
    # The "Si/No/Desconocido" are labels at specific columns.
    # We put "X" in the empty cell C2 (before "Si" label at C1) or modify label.

    # --- Fiebre (R43-44) ---
    # R44: C1="    Si"(label), C2=EMPTY(X mark), C3="No"(label), C4="Desconocido"(label)
    # Right side: C7="Si", C8="No", C9="Desconocido", C10=EMPTY
    fiebre = g("signo_fiebre")
    if _chk(fiebre):
        ws.cell(row=44, column=2).value = "X"
    elif _is_no(fiebre):
        ws.cell(row=44, column=3).value = "X No"
    elif _is_desc(fiebre):
        ws.cell(row=44, column=4).value = "X Desconocido"

    # Coriza (R43-44 right side) — overwrite labels with X prefix
    coriza = g("signo_coriza")
    if _chk(coriza):
        ws.cell(row=44, column=7).value = "X Si"
    elif _is_no(coriza):
        ws.cell(row=44, column=8).value = "X No"
    elif _is_desc(coriza):
        ws.cell(row=44, column=9).value = "X Desconocido"

    # Fecha inicio sintomas — R43 C14 has template "      /      /"
    d, m, y = _parse_date(g("fecha_inicio_sintomas"))
    if d:
        ws.cell(row=43, column=14).value = f"  {d}  /  {m}  / {y}"

    # --- Exantema/rash (R45-46) ---
    exantema = g("signo_exantema")
    if _chk(exantema):
        ws.cell(row=46, column=2).value = "X"
    elif _is_no(exantema):
        ws.cell(row=46, column=3).value = "X No"
    elif _is_desc(exantema):
        ws.cell(row=46, column=4).value = "X Desconocido"

    # Manchas Koplik (R45-46 right) — C7="Si", C8="No", C9="Desconocido", C10=EMPTY
    koplik = g("signo_manchas_koplik")
    if _chk(koplik):
        ws.cell(row=46, column=7).value = "X Si"
    elif _is_no(koplik):
        ws.cell(row=46, column=8).value = "X No"
    elif _is_desc(koplik):
        ws.cell(row=46, column=9).value = "X Desconocido"

    # Fecha inicio fiebre — R45 C14 template "      /      /"
    d, m, y = _parse_date(g("fecha_inicio_fiebre"))
    if d:
        ws.cell(row=45, column=14).value = f"  {d}  /  {m}  / {y}"

    # --- Tos (R47-48) ---
    tos = g("signo_tos")
    if _chk(tos):
        ws.cell(row=48, column=2).value = "X"
    elif _is_no(tos):
        ws.cell(row=48, column=3).value = "X No"
    elif _is_desc(tos):
        ws.cell(row=48, column=4).value = "X Desconocido"

    # Artralgia (R47-48 right)
    artralgia = g("signo_artralgia")
    if _chk(artralgia):
        ws.cell(row=48, column=7).value = "X Si"
    elif _is_no(artralgia):
        ws.cell(row=48, column=8).value = "X No"
    elif _is_desc(artralgia):
        ws.cell(row=48, column=9).value = "X Desconocido"

    # Fecha inicio exantema — R48 C14 template "      /      /"
    d, m, y = _parse_date(g("fecha_inicio_erupcion"))
    if d:
        ws.cell(row=48, column=14).value = f"  {d}  /  {m}  / {y}"

    # --- Conjuntivitis (R49-50) ---
    conjunt = g("signo_conjuntivitis")
    if _chk(conjunt):
        ws.cell(row=50, column=2).value = "X"
    elif _is_no(conjunt):
        ws.cell(row=50, column=3).value = "X No"
    elif _is_desc(conjunt):
        ws.cell(row=50, column=4).value = "X Desconocido"

    # Adenopatias (R49-50 right)
    adeno = g("signo_adenopatias")
    if _chk(adeno):
        ws.cell(row=50, column=7).value = "X Si"
    elif _is_no(adeno):
        ws.cell(row=50, column=8).value = "X No"
    elif _is_desc(adeno):
        ws.cell(row=50, column=9).value = "X Desconocido"

    # Sitio inicio exantema (R50 C12-14 area, EMPTY cells)
    sitio = g("sitio_inicio_erupcion", g("sitio_inicio_erupcion_otro"))
    if sitio:
        ws.cell(row=50, column=12).value = sitio

    # --- Hospitalizacion (R51-53) ---
    # R52: C1="    Si", C2="No", C3="Desconocido", C4=EMPTY, C5="Nombre Hospital:", ...
    hosp = g("hospitalizado")
    if _chk(hosp):
        ws.cell(row=52, column=1).value = "  X Si"
    elif _is_no(hosp):
        ws.cell(row=52, column=2).value = "X No"
    elif _is_desc(hosp):
        ws.cell(row=52, column=3).value = "X Desconocido"

    # R52: C5="Nombre del Hospital:", C6-C8=EMPTY(hospital name)
    hosp_nombre = g("hosp_nombre")
    if hosp_nombre:
        ws.cell(row=52, column=6).value = hosp_nombre

    # R52: C9="Fecha hospitalizacion:", C12="      /      /"(date template)
    d, m, y = _parse_date(g("hosp_fecha"))
    if d:
        ws.cell(row=52, column=12).value = f"  {d}  /  {m}  / {y}"

    # --- Complicaciones (R54-55) ---
    # R54: C1="Complicaciones", C2=EMPTY, C3="Si          No"(combined label), C4=EMPTY,
    #       C5="Desconocido"(label, with E54:F54 merge)
    # C7="Que complicaciones?", C8=EMPTY, C9=EMPTY, C10="Neumonia", C11=EMPTY,
    # C12="Encefalitis", C13="Diarrea", C14="Trombocitopenia"
    tiene_comp = g("tiene_complicaciones", g("complicaciones"))
    if _chk(tiene_comp):
        ws.cell(row=54, column=3).value = "X Si          No"
    elif _is_no(tiene_comp):
        ws.cell(row=54, column=3).value = "Si       X No"
    elif _is_desc(tiene_comp):
        ws.cell(row=54, column=5).value = "X Desconocido"

    # Individual complications — mark with "X" prefix on label cells
    if _chk(g("comp_neumonia")):
        ws.cell(row=54, column=10).value = "X Neumonía"
    if _chk(g("comp_encefalitis")):
        ws.cell(row=54, column=12).value = "X Encefalitis"
    if _chk(g("comp_diarrea")):
        ws.cell(row=54, column=13).value = "X Diarrea"
    if _chk(g("comp_trombocitopenia")):
        ws.cell(row=54, column=14).value = "X Trombocitopenia"

    # R55: C1="Otitis media aguda", C3="Ceguera", C5="Otro, especifique:"
    if _chk(g("comp_otitis")):
        ws.cell(row=55, column=1).value = "  X    Otitis media aguda"
    if _chk(g("comp_ceguera")):
        ws.cell(row=55, column=3).value = "  X    Ceguera"
    comp_otra = g("comp_otra_texto", g("complicaciones_otra"))
    if comp_otra:
        ws.cell(row=55, column=5).value = f"X Otro: {comp_otra}"

    # --- Aislamiento respiratorio (R56-57) ---
    # R56: C1="Aislamiento resp.", C2=EMPTY, C3="    Si"(label), C4=EMPTY(X mark),
    #       C5=" No"(label), C6="Desconocido"(label), C7=EMPTY
    #       C8="Fecha inicio aislamiento:", C12="      /      /"(date template)
    aisla = g("aislamiento_respiratorio")
    if _chk(aisla):
        ws.cell(row=56, column=4).value = "X"
    elif _is_no(aisla):
        ws.cell(row=56, column=5).value = "X No"
    elif _is_desc(aisla):
        ws.cell(row=56, column=6).value = "X Desconocido"

    d, m, y = _parse_date(g("fecha_aislamiento"))
    if d:
        ws.cell(row=56, column=12).value = f"  {d}  /  {m}  / {y}"

    # ===================================================================
    # SECTION V: Factores de riesgo (Row 58-66)
    # ===================================================================

    # R59: Case confirmed in community — C12="Si", C13="No", C14="Desconocido"
    # The empty cells for marks are C2-C11 area or we prefix the label
    caso_com = g("caso_sospechoso_comunidad_3m")
    if _chk(caso_com):
        ws.cell(row=59, column=12).value = "  X Si"
    elif _is_no(caso_com):
        ws.cell(row=59, column=13).value = "X No"
    elif _is_desc(caso_com):
        ws.cell(row=59, column=14).value = "X Desconocido"

    # R60: Contact with suspected case 7-23 days
    contacto = g("contacto_sospechoso_7_23")
    if _chk(contacto):
        ws.cell(row=60, column=12).value = "  X Si"
    elif _is_no(contacto):
        ws.cell(row=60, column=13).value = "X No"
    elif _is_desc(contacto):
        ws.cell(row=60, column=14).value = "X Desconocido"

    # R61: Traveled 7-23 days prior — C12="Si", C13="No"
    viajo = g("viajo_7_23_previo")
    if _chk(viajo):
        ws.cell(row=61, column=12).value = "  X Si"
    elif _is_no(viajo):
        ws.cell(row=61, column=13).value = "X No"

    # R62: Travel destination (whole row is mostly EMPTY for free text)
    destino = g("destino_viaje")
    viaje_pais = g("viaje_pais")
    viaje_depto = g("viaje_departamento")
    viaje_muni = g("viaje_municipio")
    destino_full = destino
    if viaje_pais or viaje_depto or viaje_muni:
        parts = [p for p in [viaje_pais, viaje_depto, viaje_muni] if p]
        destino_full = ", ".join(parts) if parts else destino
    if destino_full:
        ws.cell(row=62, column=2).value = destino_full

    # R63: Travel dates — C12="/  /"(salida), C14="/  /"(entrada)
    d, m, y = _parse_date(g("viaje_fecha_salida"))
    if d:
        ws.cell(row=63, column=12).value = f"{d}/{m}/{y}"
    d, m, y = _parse_date(g("viaje_fecha_entrada"))
    if d:
        ws.cell(row=63, column=14).value = f"{d}/{m}/{y}"

    # R65: Family member traveled abroad — C8="Si", C9="No"
    fam_viajo = g("familiar_viajo_exterior")
    if _chk(fam_viajo):
        ws.cell(row=65, column=8).value = "X Si"
    elif _is_no(fam_viajo):
        ws.cell(row=65, column=9).value = "X No"

    d, m, y = _parse_date(g("familiar_fecha_retorno"))
    if d:
        ws.cell(row=65, column=14).value = f"{d}/{m}/{y}"

    # R66: Contact with pregnant woman — C8="Si", C9="No", C10="Desconocido"
    cont_emb = g("contacto_embarazada")
    if _chk(cont_emb):
        ws.cell(row=66, column=8).value = "X Si"
    elif _is_no(cont_emb):
        ws.cell(row=66, column=9).value = "X No"
    elif _is_desc(cont_emb):
        ws.cell(row=66, column=10).value = "X Desconocido"

    # ===================================================================
    # SECTION VI: Medidas de respuesta (Row 67-76)
    # ===================================================================

    # R68: BAI — C7="Si", C8="No"
    bai = g("bai_realizada")
    if _chk(bai):
        ws.cell(row=68, column=7).value = "  X Si"
    elif _is_no(bai):
        ws.cell(row=68, column=8).value = "X No"
    bai_n = g("bai_casos_sospechosos")
    if bai_n:
        ws.cell(row=68, column=10).value = bai_n

    # R69: BAC
    bac = g("bac_realizada")
    if _chk(bac):
        ws.cell(row=69, column=7).value = "  X Si"
    elif _is_no(bac):
        ws.cell(row=69, column=8).value = "X No"
    bac_n = g("bac_casos_sospechosos")
    if bac_n:
        ws.cell(row=69, column=10).value = bac_n

    # R70: Vacunacion bloqueo — C7="Si", C8="No"
    vac_bloq = g("vacunacion_bloqueo")
    if _chk(vac_bloq):
        ws.cell(row=70, column=7).value = "  X Si"
    elif _is_no(vac_bloq):
        ws.cell(row=70, column=8).value = "X No"

    # R70: Monitoreo rapido — C14 "Si  No"
    mon_rap = g("monitoreo_rapido_vacunacion")
    if _chk(mon_rap):
        ws.cell(row=70, column=14).value = "X Si            No"
    elif _is_no(mon_rap):
        ws.cell(row=70, column=14).value = "Si         X No"

    # R71: Vacunacion barrido
    vac_barr = g("vacunacion_barrido")
    if _chk(vac_barr):
        ws.cell(row=71, column=7).value = "  X Si"
    elif _is_no(vac_barr):
        ws.cell(row=71, column=8).value = "X No"

    # R73-74: Fuente posible de contagio — labels with EMPTY adjacent cells
    fc = g("fuente_posible_contagio", "").upper()
    if "HOGAR" in fc or "CONTACTO" in fc:
        ws.cell(row=73, column=1).value = "   X    Contacto en el hogar"
    if "SERVICIO" in fc or "SALUD" in fc:
        ws.cell(row=73, column=5).value = "X Servicio de salud"
    if "EDUCATIVA" in fc or "ESCUELA" in fc:
        ws.cell(row=73, column=7).value = "X Institución educativa"
    if "PUBLICO" in fc or "PÚBLICO" in fc or "ESPACIO" in fc:
        ws.cell(row=73, column=9).value = "X Espacio público"
    if "COMUNIDAD" in fc:
        ws.cell(row=73, column=13).value = "X"
    if "EVENTO" in fc or "MASIVO" in fc:
        ws.cell(row=74, column=1).value = "   X    Evento público masivo"
    if "TRANSPORTE" in fc:
        ws.cell(row=74, column=4).value = "X Transporte internacional"
    if "DESCONOCIDO" in fc:
        ws.cell(row=74, column=7).value = "X Desconocido"
    fc_otro = g("fuente_contagio_otro")
    if "OTRO" in fc or fc_otro:
        ws.cell(row=74, column=9).value = f"X Otro: {fc_otro}"

    # R75: Vitamina A — C5="Si", C6="No Desconocido"
    vit_a = g("vitamina_a_administrada")
    if _chk(vit_a):
        ws.cell(row=75, column=5).value = " X Si"
    elif _is_no(vit_a):
        ws.cell(row=75, column=6).value = "X No"
    elif _is_desc(vit_a):
        ws.cell(row=75, column=7).value = "X"

    vit_dosis = g("vitamina_a_dosis")
    if vit_dosis:
        ws.cell(row=75, column=9).value = vit_dosis

    # ===================================================================
    # SECTION VII: Laboratorio (Row 77-92)
    # ===================================================================

    # R78: Muestras obtenidas — G78:H78="Si Suero", I78:J78="Si Orina", K78="Si hisopado"
    # These are labels. We need to mark the EMPTY cells adjacent to them.
    suero = _chk(g("muestra_suero"))
    orina = _chk(g("muestra_orina"))
    hisopado = _chk(g("muestra_hisopado"))

    if suero:
        ws.cell(row=78, column=6).value = "X"
    if orina:
        ws.cell(row=78, column=7).value = "X Si Suero"  # prepend X
    if hisopado:
        ws.cell(row=78, column=9).value = "X Si Orina"

    # Actually let me reconsider - the labels ARE at C7, C9, C11
    # We mark by prepending X to the label text
    if suero:
        ws.cell(row=78, column=7).value = "X Si Suero"
    if orina:
        ws.cell(row=78, column=9).value = "X Si Orina"
    if hisopado:
        ws.cell(row=78, column=11).value = "X Si hisopado nasofaríngeo"

    # R79: Motivo no recoleccion — append to label
    motivo = g("motivo_no_recoleccion", g("motivo_no_3_muestras"))
    if motivo:
        label = ws.cell(row=79, column=1).value or ""
        ws.cell(row=79, column=1).value = f"{label} {motivo}"

    # Lab samples (rows 83-92)
    # Structure per sample:
    #   Col A-B: label (e.g. "Primera"/"Segunda"/"Orina"/"Hisopado")
    #   Col C: fecha toma (EMPTY)
    #   Col D-E: fecha envio (EMPTY merged)
    #   Col F: antigeno label
    #   Col G-I: tipo prueba labels (IgM/IgG/Avidez or RT-PCR)
    #   Col J-L: resultado (EMPTY for values) — R82 has sub-headers IgM/IgG/Avidez
    #   Col M: fecha resultado
    #   Col N: secuenciacion

    # Primera Suero (R83-84)
    d, m, y = _parse_date(g("muestra_suero_fecha"))
    if d:
        ws.cell(row=83, column=3).value = f"{d}/{m}/{y}"

    d_env, m_env, y_env = _parse_date(g("fecha_recepcion_laboratorio"))
    if d_env:
        ws.cell(row=83, column=4).value = f"{d_env}/{m_env}/{y_env}"

    # Results — IgM col 10, IgG col 11, Avidez col 12
    igm = g("resultado_igm_cualitativo")
    igg = g("resultado_igg_cualitativo")
    if igm:
        ws.cell(row=83, column=10).value = igm
    if igg:
        ws.cell(row=83, column=11).value = igg

    # Fecha resultado
    d, m, y = _parse_date(g("fecha_resultado_laboratorio"))
    if d:
        ws.cell(row=83, column=13).value = f"{d}/{m}/{y}"

    # Orina (R87-88)
    d, m, y = _parse_date(g("muestra_orina_fecha"))
    if d:
        ws.cell(row=87, column=3).value = f"{d}/{m}/{y}"

    pcr_orina = g("resultado_pcr_orina")
    if pcr_orina:
        ws.cell(row=87, column=10).value = pcr_orina

    # Hisopado (R89-90)
    d, m, y = _parse_date(g("muestra_hisopado_fecha"))
    if d:
        ws.cell(row=89, column=3).value = f"{d}/{m}/{y}"

    pcr_hisop = g("resultado_pcr_hisopado")
    if pcr_hisop:
        ws.cell(row=89, column=10).value = pcr_hisop

    # Process lab_muestras_json for detailed multi-sample data
    lab_json = _safe_json_loads(g("lab_muestras_json"))
    if lab_json and isinstance(lab_json, list):
        for sample in lab_json:
            if not isinstance(sample, dict):
                continue
            tipo = str(sample.get("tipo_muestra", "")).upper()
            num = str(sample.get("numero_muestra", "1"))

            if "SUERO" in tipo:
                tr = 83 if num == "1" else 85  # Primera/Segunda suero
            elif "ORINA" in tipo:
                tr = 87
            elif "HISOPADO" in tipo or "NASOFARINGEO" in tipo or "ASPIRADO" in tipo:
                tr = 89
            else:
                tr = 91  # OTRO

            d, m, y = _parse_date(str(sample.get("fecha_toma", "")))
            if d:
                ws.cell(row=tr, column=3).value = f"{d}/{m}/{y}"

            d, m, y = _parse_date(str(sample.get("fecha_envio", "")))
            if d:
                ws.cell(row=tr, column=4).value = f"{d}/{m}/{y}"

            res_igm = str(sample.get("resultado_igm", ""))
            res_igg = str(sample.get("resultado_igg", ""))
            res_avidez = str(sample.get("resultado_avidez", ""))
            res_pcr = str(sample.get("resultado_pcr", ""))

            if res_igm:
                ws.cell(row=tr, column=10).value = res_igm
            if res_igg:
                ws.cell(row=tr, column=11).value = res_igg
            if res_avidez:
                ws.cell(row=tr, column=12).value = res_avidez

            d, m, y = _parse_date(str(sample.get("fecha_resultado", "")))
            if d:
                ws.cell(row=tr, column=13).value = f"{d}/{m}/{y}"

    # Secuenciacion (R91 C14 area — N81:N86 or N87:N88 or N89:N90 or N91:N92)
    seq_res = g("secuenciacion_resultado")
    seq_fecha = g("secuenciacion_fecha")
    if seq_res or seq_fecha:
        d, m, y = _parse_date(seq_fecha)
        fecha_str = f" ({d}/{m}/{y})" if d else ""
        ws.cell(row=91, column=14).value = f"{seq_res}{fecha_str}"

    # ===================================================================
    # SECTION VIII: Clasificacion (Row 93-109)
    # ===================================================================

    # R94: A94:E94="Clasificacion final", F94:J94="Criterio confirmacion", K94:N94="Criterio descarte"
    # R95: A95:B95="Sarampion", C95:E95="Rubeola", F95:J95="Laboratorio", K95:M95="Laboratorial", N95="Clinico"
    # R96: A96:B96="Descartado", C96:E96="Pendiente", F96:J96="Nexo epi", K96:M96="Rel. vacuna"
    # R97: A97:E97="No cumple def", F97:J97="Clinico", K97:M97="Otro dx"

    clasif = g("clasificacion_caso", "").upper()
    # Prepend X to matching classification label
    if "SARAMPION" in clasif or "SARAMPIÓN" in clasif:
        ws.cell(row=95, column=1).value = "  X    Sarampión"
    if "RUBEOLA" in clasif or "RUBÉOLA" in clasif:
        ws.cell(row=95, column=3).value = "  X    Rubéola"
    if "DESCARTADO" in clasif or "DESCARTA" in clasif:
        ws.cell(row=96, column=1).value = "  X    Descartado"
    if "PENDIENTE" in clasif:
        ws.cell(row=96, column=3).value = "  X    Pendiente"
    if "NO CUMPLE" in clasif or "DEFINICION" in clasif:
        ws.cell(row=97, column=1).value = "  X   No cumple con la definición de caso"

    # Criterio confirmacion
    crit_conf = g("criterio_confirmacion", "").upper()
    if "LABORATORIO" in crit_conf:
        ws.cell(row=95, column=6).value = "  X    Laboratorio"
    if "NEXO" in crit_conf or "EPIDEMIOLOG" in crit_conf:
        ws.cell(row=96, column=6).value = "  X    Nexo epidemiológico"
    if "CLINICO" in crit_conf or "CLÍNICO" in crit_conf:
        ws.cell(row=97, column=6).value = "  X    Clínico"

    # Criterio descarte
    crit_desc = g("criterio_descarte", "").upper()
    if "LABORATORI" in crit_desc:
        ws.cell(row=95, column=11).value = "  X   Laboratorial"
    if "CLINICO" in crit_desc or "CLÍNICO" in crit_desc:
        ws.cell(row=95, column=14).value = "    X    Clínico"
    if "VACUNA" in crit_desc:
        ws.cell(row=96, column=11).value = "  X   Relacionado con la vacuna"
    if "OTRO" in crit_desc:
        ws.cell(row=97, column=11).value = f"  X   Otro: {g('criterio_descarte')}"

    # R98: Fuente de infeccion de casos confirmados
    # R99: A99:B99="Importado", C99:F99="Relacionado importacion", G99:H99="Pais importacion:"
    # R100: A100:B100="Endemico", C100:F100="Fuente desconocida"
    fuente_inf = g("fuente_infeccion", "").upper()
    if "IMPORTADO" in fuente_inf and "RELACIONADO" not in fuente_inf:
        ws.cell(row=99, column=1).value = "  X    Importado"
    if "RELACIONADO" in fuente_inf:
        ws.cell(row=99, column=3).value = "X Relacionado con la importación"
    pais_imp = g("pais_importacion")
    if pais_imp:
        ws.cell(row=99, column=9).value = pais_imp
    if "ENDEMICO" in fuente_inf or "ENDÉMICO" in fuente_inf:
        ws.cell(row=100, column=1).value = "  X    Endémico"
    if "DESCONOCID" in fuente_inf:
        ws.cell(row=100, column=3).value = "   X     Fuente desconocida"

    # R101: Contacto otro caso — C3="Si", C5="No", C6="Desconocido"
    cont_otro = g("contacto_otro_caso")
    if _chk(cont_otro):
        ws.cell(row=101, column=2).value = "X"
    elif _is_no(cont_otro):
        ws.cell(row=101, column=4).value = "X"
    elif _is_desc(cont_otro):
        ws.cell(row=101, column=7).value = "X"

    # R103-105: Analizado por
    analizado = g("caso_analizado_por", "").upper()
    if "CONAPI" in analizado:
        ws.cell(row=103, column=1).value = "  X    CONAPI"
    if "EPIDEMIOLOG" in analizado or "DIRECCION" in analizado:
        ws.cell(row=103, column=3).value = "X Dirección de Epidemiológica y Gestión de riesgo"
    if "COMISION" in analizado or "COMISIÓN" in analizado:
        ws.cell(row=104, column=1).value = (
            "  X    Comisión Nacional para verificar la interrupción "
            "de la transmisión endémica"
        )
    analizado_otro = g("caso_analizado_por_otro")
    if "OTRO" in analizado or analizado_otro:
        ws.cell(row=105, column=1).value = f"  X    Otros: {analizado_otro}"

    # R106-107: Condicion final del paciente
    # R107: C1="Recuperado", C3="Con Secuelas", C6="Fallecido", C7="Desconocido"
    condicion = g("condicion_final_paciente", g("condicion_egreso", "")).upper()
    if "RECUPER" in condicion:
        ws.cell(row=107, column=1).value = "X Recuperado"
    elif "SECUELA" in condicion:
        ws.cell(row=107, column=3).value = "X Con Secuelas"
    elif "FALLEC" in condicion or "MUERT" in condicion:
        ws.cell(row=107, column=6).value = "X Fallecido"
    elif "DESCONOCID" in condicion:
        ws.cell(row=107, column=7).value = "X Desconocido"

    # Fecha defuncion — R106 C13 merged M106:N106 has template "     /     / "
    d, m, y = _parse_date(g("fecha_defuncion"))
    if d:
        ws.cell(row=106, column=13).value = f"          {d}  /      {m}  / {y}"

    # R108: Causa muerte — I108:N108 EMPTY merged
    causa = g("causa_muerte_certificado")
    if causa:
        ws.cell(row=108, column=9).value = f"Causa de muerte según certificado de defunción: {causa}"

    # R109: Observaciones — C2-C14 all EMPTY
    obs = g("observaciones")
    if obs:
        ws.cell(row=109, column=2).value = obs


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _find_libreoffice() -> str:
    """Find the LibreOffice executable on the system."""
    candidates = [
        "libreoffice",
        "soffice",
        "/usr/bin/libreoffice",
        "/usr/local/bin/libreoffice",
        "/usr/bin/soffice",
        "/opt/homebrew/bin/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/lib/libreoffice/program/soffice",
        "/opt/libreoffice/program/soffice",
    ]
    for candidate in candidates:
        if shutil.which(candidate):
            return candidate
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return "libreoffice"


def generar_ficha_v2_pdf(data: dict) -> bytes:
    """Generate PDF using Excel template + LibreOffice headless.

    Args:
        data: Dictionary with patient/case data (keys match database.COLUMNS).

    Returns:
        PDF file contents as bytes.

    Raises:
        FileNotFoundError: If template not found.
        RuntimeError: If LibreOffice conversion fails.
    """
    from openpyxl import load_workbook

    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")

    with tempfile.TemporaryDirectory(prefix="ficha_pdf_") as tmpdir:
        xlsx_path = os.path.join(tmpdir, "ficha.xlsx")
        shutil.copy2(TEMPLATE_PATH, xlsx_path)

        wb = load_workbook(xlsx_path)
        ws = wb["Hoja1"]
        _fill_hoja1(ws, data)
        wb.save(xlsx_path)

        lo_bin = _find_libreoffice()
        # Use unique user profile to allow parallel conversions
        user_profile = os.path.join(tmpdir, "lo_profile")
        os.makedirs(user_profile, exist_ok=True)

        result = subprocess.run(
            [
                lo_bin,
                "--headless",
                "--norestore",
                f"-env:UserInstallation=file://{user_profile}",
                "--convert-to",
                "pdf",
                "--outdir",
                tmpdir,
                xlsx_path,
            ],
            capture_output=True,
            text=True,
            timeout=120,
            env=os.environ.copy(),
        )

        if result.returncode != 0:
            logger.error(
                "LibreOffice conversion failed (rc=%d): stderr=%s stdout=%s",
                result.returncode,
                result.stderr[:500],
                result.stdout[:500],
            )
            raise RuntimeError(
                f"PDF conversion failed (rc={result.returncode}): "
                f"{(result.stderr or result.stdout)[:300]}"
            )

        pdf_path = os.path.join(tmpdir, "ficha.pdf")
        if not os.path.exists(pdf_path):
            import glob as _glob
            pdfs = _glob.glob(os.path.join(tmpdir, "*.pdf"))
            if pdfs:
                pdf_path = pdfs[0]
            else:
                raise RuntimeError(
                    f"PDF not generated. stdout: {result.stdout[:200]}, "
                    f"stderr: {result.stderr[:200]}"
                )

        with open(pdf_path, "rb") as f:
            return f.read()


def generar_fichas_v2_bulk(records: list, merge: bool = True) -> bytes:
    """Generate multiple PDFs from a list of records.

    Args:
        records: List of dicts, each with patient/case data.
        merge: If True, returns a single merged PDF. If False, returns a ZIP.

    Returns:
        PDF bytes (merged) or ZIP bytes (individual files).

    Raises:
        ValueError: If records list is empty.
    """
    if not records:
        raise ValueError("No records provided")

    if merge:
        try:
            from PyPDF2 import PdfMerger
        except ImportError:
            from pypdf import PdfMerger

        merger = PdfMerger()
        for i, rec in enumerate(records):
            try:
                pdf_bytes = generar_ficha_v2_pdf(rec)
                merger.append(io.BytesIO(pdf_bytes))
            except Exception as e:
                rid = rec.get("registro_id", f"record_{i}")
                logger.warning("Failed to generate PDF for %s: %s", rid, e)
                continue

        if not merger.pages:
            raise RuntimeError("No PDFs were generated successfully")

        output = io.BytesIO()
        merger.write(output)
        merger.close()
        return output.getvalue()
    else:
        import zipfile

        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, rec in enumerate(records):
                rid = rec.get("registro_id", f"unknown_{i}")
                try:
                    pdf_bytes = generar_ficha_v2_pdf(rec)
                    zf.writestr(f"ficha_godata_{rid}.pdf", pdf_bytes)
                except Exception as e:
                    logger.warning("Failed to generate PDF for %s: %s", rid, e)
                    continue
        return output.getvalue()


# ---------------------------------------------------------------------------
# Backward compatibility aliases
# ---------------------------------------------------------------------------
generar_ficha_pdf = generar_ficha_v2_pdf
generar_fichas_bulk = generar_fichas_v2_bulk
