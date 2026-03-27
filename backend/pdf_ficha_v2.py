"""
PDF Generator for MSPAS Sarampion/Rubeola Form - Platypus Table Version.

Uses reportlab Platypus Tables for structured layout with automatic borders,
cell alignment, and spanning. Produces a pixel-accurate 2-page LETTER replica
of the official MSPAS 2026 "FICHA EPIDEMIOLOGICA DE VIGILANCIA DE SARAMPION RUBEOLA".

Key design rule: NO nested tables. Every table cell contains only Paragraphs
or plain strings, never sub-Tables. This avoids the blPara wrapping bug.

Public API:
    generar_ficha_v2_pdf(data: dict) -> bytes
    generar_fichas_v2_bulk(records: list, merge: bool = True) -> bytes
"""
import io
import json
import os
import zipfile
import logging
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image,
)
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = LETTER
MARGIN = 18
CONTENT_W = PAGE_W - 2 * MARGIN

DARK_BLUE = HexColor('#1a237e')
LIGHT_GRAY = HexColor('#eeeeee')
BC = colors.black  # border color

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
LOGO_PATH = None
for _fname in ('escudo_guatemala.png', 'mspas_logo.png'):
    _cand = os.path.join(ASSETS_DIR, _fname)
    if os.path.isfile(_cand):
        LOGO_PATH = _cand
        break

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
_base = getSampleStyleSheet()

S_LABEL = ParagraphStyle('FL', parent=_base['Normal'],
    fontName='Helvetica-Bold', fontSize=6, leading=7)
S_VALUE = ParagraphStyle('FV', parent=_base['Normal'],
    fontName='Helvetica', fontSize=7, leading=8.5)
S_VALUE_SM = ParagraphStyle('FVS', parent=S_VALUE, fontSize=6, leading=7)
S_VALUE_C = ParagraphStyle('FVC', parent=S_VALUE, alignment=TA_CENTER)
S_SECTION = ParagraphStyle('FS', parent=_base['Normal'],
    fontName='Helvetica-Bold', fontSize=8, leading=10,
    textColor=colors.white, alignment=TA_CENTER)
S_TITLE = ParagraphStyle('FT', parent=_base['Normal'],
    fontName='Helvetica-Bold', fontSize=9, leading=11, alignment=TA_CENTER)
S_DEF = ParagraphStyle('FD', parent=_base['Normal'],
    fontName='Helvetica-Oblique', fontSize=5, leading=6)
S_CB = ParagraphStyle('FCB', parent=_base['Normal'],
    fontName='Helvetica', fontSize=7, leading=8.5)
S_CB_SM = ParagraphStyle('FCBS', parent=S_CB, fontSize=5.5, leading=6.5)
S_CB_XS = ParagraphStyle('FCBXS', parent=S_CB, fontSize=5, leading=6)
S_HDR = ParagraphStyle('FH', parent=_base['Normal'],
    fontName='Helvetica-Bold', fontSize=5.5, leading=6.5, alignment=TA_CENTER)
S_CONTACT = ParagraphStyle('FC', parent=_base['Normal'],
    fontName='Helvetica', fontSize=5.5, leading=6.5)
S_SUB = ParagraphStyle('FSub', parent=_base['Normal'],
    fontName='Helvetica-Bold', fontSize=6.5, leading=8)
S_LEGEND = ParagraphStyle('FLeg', parent=_base['Normal'],
    fontName='Helvetica', fontSize=5, leading=6)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _g(data, key, default=""):
    val = data.get(key)
    if val is None:
        return default
    s = str(val).strip()
    if s.upper() in ("NONE", "NULL", "NAN", ""):
        return default
    return s

def _parse_date(date_str):
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

def _chk(value):
    if value is None: return False
    return str(value).strip().upper() in ("SI", "SÍ", "S", "1", "TRUE", "X", "YES")

def _is_no(value):
    if value is None: return False
    return str(value).strip().upper() in ("NO", "N", "0", "FALSE")

def _is_desc(value):
    if value is None: return False
    return str(value).strip().upper() in ("DESCONOCIDO", "DESC", "D", "UNKNOWN")

def _cb(checked=False):
    """Checkbox: [X] if checked, [  ] if not."""
    if checked:
        return '<font face="Courier-Bold" size="7">[X]</font>'
    else:
        return '<font face="Courier" size="7">[&nbsp;&nbsp;]</font>'

def _cb_sm(checked=False):
    """Small checkbox."""
    if checked:
        return '<font face="Courier-Bold" size="6">[X]</font>'
    else:
        return '<font face="Courier" size="6">[&nbsp;&nbsp;]</font>'

def _p(text, style=S_VALUE):
    return Paragraph(str(text), style)

def _lv(label, value):
    """Label + value stacked in one Paragraph."""
    return Paragraph(
        f'<b><font size="6">{label}</font></b><br/>'
        f'<font size="7">{value}</font>', S_VALUE)

def _date_lv(label, date_str):
    """Label + date formatted as [DD]/[MM]/[YYYY] in one Paragraph."""
    dd, mm, yyyy = _parse_date(date_str)
    if dd:
        dstr = f'<font face="Courier" size="7">[{dd}]/[{mm}]/[{yyyy}]</font>'
    else:
        dstr = '<font face="Courier" size="7">[__]/[__]/[____]</font>'
    return Paragraph(
        f'<b><font size="6">{label}</font></b><br/>{dstr}', S_VALUE)

def _safe_json(val):
    if not val: return []
    if isinstance(val, (list, dict)): return val
    try: return json.loads(val)
    except: return []

# ---------------------------------------------------------------------------
# Grid style template
# ---------------------------------------------------------------------------
GRID = [
    ('GRID', (0,0), (-1,-1), 0.5, BC),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 1),
    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ('LEFTPADDING', (0,0), (-1,-1), 2),
    ('RIGHTPADDING', (0,0), (-1,-1), 2),
]

def _section_hdr(text):
    t = Table([[Paragraph(text, S_SECTION)]], colWidths=[CONTENT_W], rowHeights=[16])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK_BLUE),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ]))
    return t

def _sub_hdr(text):
    t = Table([[Paragraph(f'<b>{text}</b>', S_SUB)]], colWidths=[CONTENT_W], rowHeights=[12])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GRAY),
        ('BOX', (0,0), (-1,-1), 0.5, BC),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ]))
    return t

def _tbl(rows, widths, heights=None, extra_style=None):
    """Create a table with GRID style. widths as fractions of CONTENT_W."""
    cw = [CONTENT_W * w for w in widths]
    rh = heights if heights else [20] * len(rows)
    if isinstance(rh, (int, float)):
        rh = [rh] * len(rows)
    t = Table(rows, colWidths=cw, rowHeights=rh)
    style = list(GRID)
    if extra_style:
        style.extend(extra_style)
    t.setStyle(TableStyle(style))
    return t


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class FichaBuilder:
    def __init__(self, data):
        self.d = data
        self.el = []

    def _a(self, e):
        self.el.append(e)

    def _sp(self, h=2):
        self.el.append(Spacer(1, h))

    def build(self):
        self._page1()
        self.el.append(PageBreak())
        self._page2_with_contacts()
        return self.el

    # ===================== PAGE 1 =====================

    def _page1(self):
        self._header()
        self._sp(2)
        self._diagnostico()
        self._sp(1)
        self._definicion()
        self._sp(2)
        self._sec1()
        self._sp(1)
        self._sec2()
        self._sp(1)
        self._sec3()
        self._sp(1)
        self._sec4()

    def _header(self):
        d = self.d
        # Header: Logo | Title | Version + top-right boxes
        if LOGO_PATH:
            try:
                logo = Image(LOGO_PATH, width=38, height=38)
            except Exception:
                logo = _p('<b>MSPAS</b>', S_TITLE)
        else:
            logo = _p('<b>MSPAS</b>', S_TITLE)

        title = Paragraph(
            'MINISTERIO DE SALUD P\u00daBLICA Y ASISTENCIA SOCIAL<br/>'
            '<font size="7.5">FICHA EPIDEMIOL\u00d3GICA DE VIGILANCIA DE SARAMPI\u00d3N RUB\u00c9OLA</font><br/>'
            '<font size="6.5">Direcci\u00f3n de Epidemiolog\u00eda y Gesti\u00f3n del Riesgo</font>',
            S_TITLE)

        folio = _g(d, 'folio', _g(d, 'numero_ficha', ''))
        no_caso = _g(d, 'no_caso', '')
        codigo = _g(d, 'codigo_caso', '')
        area = _g(d, 'area_salud_mspas', _g(d, 'departamento_residencia', ''))

        right = Paragraph(
            f'<font size="5.5">Versi\u00f3n 2026</font><br/>'
            f'<font size="5">Folio: <b>{folio}</b></font><br/>'
            f'<font size="5">No. caso: <b>{no_caso}</b></font><br/>'
            f'<font size="5">C\u00f3digo: <b>{codigo}</b></font><br/>'
            f'<font size="5">\u00c1rea: <b>{area}</b></font>',
            ParagraphStyle('hdr_r', parent=S_VALUE_SM, alignment=TA_CENTER))

        t = Table([[logo, title, right]],
                  colWidths=[46, CONTENT_W - 46 - 110, 110],
                  rowHeights=[48])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('ALIGN', (2,0), (2,0), 'CENTER'),
            ('BOX', (0,0), (-1,-1), 0.8, BC),
            ('LINEAFTER', (0,0), (0,0), 0.4, BC),
            ('LINEAFTER', (1,0), (1,0), 0.4, BC),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        self._a(t)

    def _diagnostico(self):
        d = self.d
        diag = _g(d, 'diagnostico_sospecha', _g(d, 'diagnostico_registrado', '')).upper()
        is_sar = 'SARAMP' in diag or 'B05' in diag
        is_rub = 'RUBEO' in diag or 'RUBE' in diag or 'B06' in diag
        is_dengue = 'DENGUE' in diag or 'A90' in diag or 'A91' in diag
        is_arbo = 'ARBO' in diag or 'ZIKA' in diag or 'CHIK' in diag
        is_otra_febril = 'FEBRIL' in diag or 'EXANTEM' in diag
        is_alta = 'ALTAMENTE' in diag
        if not any([is_sar, is_rub, is_dengue, is_arbo, is_otra_febril, is_alta]):
            is_sar = True

        espec_arbo = _g(d, 'especifique_arbovirosis', '')
        espec_febril = _g(d, 'especifique_febril', '')

        row = [
            _p('<b>Diagn\u00f3stico:</b>', S_LABEL),
            _p(f'{_cb(is_sar)} Sarampi\u00f3n', S_CB_SM),
            _p(f'{_cb(is_rub)} Rub\u00e9ola', S_CB_SM),
            _p(f'{_cb(is_dengue)} Dengue', S_CB_SM),
            _p(f'{_cb(is_arbo)} Otra Arbovirosis <font size="5">(Espec: {espec_arbo})</font>', S_CB_SM),
            _p(f'{_cb(is_otra_febril)} Otra febril exantem\u00e1tica <font size="5">(Espec: {espec_febril})</font>', S_CB_SM),
            _p(f'{_cb(is_alta)} Caso altamente sospechoso', S_CB_SM),
        ]
        self._a(_tbl([row], [0.10, 0.10, 0.09, 0.09, 0.22, 0.24, 0.16], 15,
                      [('BACKGROUND', (0,0), (0,0), LIGHT_GRAY)]))

    def _definicion(self):
        self._a(Paragraph(
            '<i>Sospecha rub\u00e9ola en:</i> Persona de cualquier edad en la que un trabajador '
            'de salud sospeche infecci\u00f3n por rub\u00e9ola. '
            '<i>Sospeche sarampi\u00f3n en:</i> Persona de cualquier edad que presente fiebre, '
            'erupci\u00f3n y alguno de los siguientes: Tos, Coriza o Conjuntivitis.', S_DEF))

    # -- Section 1: DATOS DE LA UNIDAD NOTIFICADORA --
    def _sec1(self):
        d = self.d
        self._a(_section_hdr('1. DATOS DE LA UNIDAD NOTIFICADORA'))

        # Row 1: Fecha Notificación | Dirección Área de Salud | Distrito de Salud | Servicio de Salud
        self._a(_tbl([[
            _date_lv('Fecha Notificaci\u00f3n', _g(d, 'fecha_notificacion')),
            _lv('Direcci\u00f3n de \u00c1rea de Salud', _g(d, 'area_salud_mspas', _g(d, 'departamento_residencia'))),
            _lv('Distrito de Salud', _g(d, 'distrito_salud_mspas')),
            _lv('Servicio de Salud', _g(d, 'servicio_salud_mspas', _g(d, 'unidad_medica'))),
        ]], [0.25, 0.25, 0.22, 0.28], 24))

        # Row 2: Fecha Consulta | Fecha investig. domiciliaria | Nombre quien investiga | Cargo | Teléfono y correo
        self._a(_tbl([[
            _date_lv('Fecha Consulta', _g(d, 'fecha_registro_diagnostico', _g(d, 'fecha_captacion'))),
            _date_lv('Fecha investig. domiciliaria', _g(d, 'fecha_inicio_investigacion')),
            _lv('Nombre quien investiga', _g(d, 'nom_responsable')),
            _lv('Cargo', _g(d, 'cargo_responsable')),
            _lv('Tel\u00e9fono y correo', _g(d, 'telefono_responsable')),
        ]], [0.20, 0.20, 0.28, 0.15, 0.17], 24))

        # Row 3: Seguro Social / Establecimiento Privado
        igss_u = _g(d, 'sector_vacunacion', _g(d, 'unidad_medica', '')).upper()
        is_igss = 'IGSS' in igss_u
        is_priv = 'PRIVAD' in igss_u
        spec = _g(d, 'unidad_medica')

        self._a(_tbl([[
            _p(f'{_cb(is_igss)} <b>Seguro Social (IGSS)</b> Especifique: {spec if is_igss else ""}', S_CB),
            _p(f'{_cb(is_priv)} <b>Establecimiento Privado</b> Especifique: {spec if is_priv else ""}', S_CB),
        ]], [0.50, 0.50], 16))

        # Row 4: Fuente de notificación (9 checkboxes)
        fuente = _g(d, 'fuente_notificacion', '').upper()
        is_serv = any(k in fuente for k in ('PUBLICA', 'PRIVADA', 'SERVICIO', 'SALUD'))
        is_ic = 'CONTACTO' in fuente or 'INVESTIG' in fuente
        is_lab = 'LABORAT' in fuente
        is_com = 'COMUNIDAD' in fuente or 'RUMOR' in fuente
        is_bai = 'BAI' in fuente or 'BUSQUEDA' in fuente
        is_auto = 'AUTO' in fuente
        is_bac = 'BAC' in fuente
        is_otro = 'OTRO' in fuente
        is_bal = 'BAL' in fuente
        if fuente and not any([is_serv, is_ic, is_lab, is_com, is_bai, is_auto, is_bac, is_otro, is_bal]):
            is_serv = True

        ft = ' '.join(f'{_cb_sm(v)} {l}' for l, v in [
            ('Serv.Salud', is_serv), ('Invest.Contacto', is_ic), ('Laborat.', is_lab),
            ('Comunidad', is_com), ('BAI', is_bai), ('Autonot.', is_auto),
            ('BAC', is_bac), ('Otro', is_otro), ('BAL', is_bal),
        ])
        self._a(_tbl([[
            _p('<b>Fuente de notificaci\u00f3n:</b>', S_LABEL),
            _p(ft, S_CB_XS),
        ]], [0.18, 0.82], 15))

    # -- Section 2: INFORMACIÓN DEL PACIENTE --
    def _sec2(self):
        d = self.d
        self._a(_section_hdr('2. INFORMACI\u00d3N DEL PACIENTE'))

        # Row 1: Nombres | Apellidos | Sexo M/F
        sx = _g(d, 'sexo', '').upper()
        self._a(_tbl([[
            _lv('Nombres', _g(d, 'nombres')),
            _lv('Apellidos', _g(d, 'apellidos')),
            _p(f'<b><font size="6">Sexo:</font></b> {_cb(sx=="M")} M {_cb(sx=="F")} F', S_CB),
        ]], [0.30, 0.40, 0.30], 20))

        # Row 2: Fecha Nacimiento | Edad Años/Meses/Días | CUI (DPI/Pasaporte/Otro)
        self._a(_tbl([[
            _date_lv('Fecha de Nacimiento', _g(d, 'fecha_nacimiento')),
            _lv('Edad A\u00f1os', _g(d, 'edad_anios')),
            _lv('Meses', _g(d, 'edad_meses')),
            _lv('D\u00edas', _g(d, 'edad_dias')),
            _lv('C\u00f3digo \u00danico Identificaci\u00f3n (DPI/Pasaporte/Otro)', _g(d, 'cui', _g(d, 'afiliacion'))),
        ]], [0.22, 0.08, 0.08, 0.08, 0.54], 24))

        # Row 3: Nombre Tutor | Parentesco | CUI Tutor
        self._a(_tbl([[
            _lv('Nombre del Tutor/Encargado', _g(d, 'nombre_encargado')),
            _lv('Parentesco', _g(d, 'parentesco_encargado')),
            _lv('CUI del Tutor', _g(d, 'cui_encargado')),
        ]], [0.45, 0.20, 0.35], 20))

        # Row 4: Pueblo | Extranjero | Migrante | Embarazada | Trimestre
        pueblo = _g(d, 'pueblo_etnia', '').upper()
        is_lad = 'LADINO' in pueblo or 'MESTIZ' in pueblo
        is_maya = 'MAYA' in pueblo
        is_gar = 'GARIFUNA' in pueblo or 'GARÍFUNA' in pueblo
        is_xin = 'XINCA' in pueblo
        extran = _g(d, 'extranjero', '').upper()
        migran = _g(d, 'migrante', '').upper()
        emb = _g(d, 'esta_embarazada', '').upper()
        trimestre = _g(d, 'trimestre_embarazo', '')

        self._a(_tbl([[
            _p(f'<b><font size="5">Pueblo:</font></b> {_cb_sm(is_lad)} Ladino {_cb_sm(is_maya)} Maya {_cb_sm(is_gar)} Gar\u00edfuna {_cb_sm(is_xin)} Xinca', S_CB_SM),
            _p(f'<b><font size="5">Extranjero:</font></b> {_cb_sm(_chk(extran))} S\u00ed {_cb_sm(_is_no(extran))} No', S_CB_SM),
            _p(f'<b><font size="5">Migrante:</font></b> {_cb_sm(_chk(migran))} S\u00ed {_cb_sm(_is_no(migran))} No', S_CB_SM),
            _p(f'<b><font size="5">Embarazada:</font></b> {_cb_sm(_chk(emb))} S\u00ed {_cb_sm(_is_no(emb))} No', S_CB_SM),
            _lv('Trimestre', trimestre),
        ]], [0.35, 0.15, 0.15, 0.18, 0.17], 16))

        # Row 5: Ocupación | Escolaridad | Teléfono
        self._a(_tbl([[
            _lv('Ocupaci\u00f3n', _g(d, 'ocupacion')),
            _lv('Escolaridad', _g(d, 'escolaridad')),
            _lv('Tel\u00e9fono', _g(d, 'telefono_encargado', _g(d, 'telefono_paciente'))),
        ]], [0.35, 0.35, 0.30], 20))

        # Row 6: País Residencia | Departamento | Municipio
        self._a(_tbl([[
            _lv('Pa\u00eds de Residencia', _g(d, 'pais_residencia', 'Guatemala')),
            _lv('Departamento', _g(d, 'departamento_residencia')),
            _lv('Municipio', _g(d, 'municipio_residencia')),
        ]], [0.30, 0.35, 0.35], 20))

        # Row 7: Lugar Poblado
        self._a(_tbl([[
            _lv('Lugar Poblado', _g(d, 'poblado')),
        ]], [1.0], 18))

        # Row 8: Dirección de Residencia
        self._a(_tbl([[
            _lv('Direcci\u00f3n de Residencia', _g(d, 'direccion_exacta')),
        ]], [1.0], 18))

    # -- Section 3: ANTECEDENTES MÉDICOS Y DE VACUNACIÓN --
    def _sec3(self):
        d = self.d
        self._a(_section_hdr('3. ANTECEDENTES M\u00c9DICOS Y DE VACUNACI\u00d3N'))

        # Row 1: Paciente vacunado Si/No/Desc/Verbal | Antecedentes médicos Si/No/Desc
        vac = _g(d, 'vacunado', '').upper()
        antec = _g(d, 'antecedentes_medicos', '').upper()
        desn = _g(d, 'desnutricion', '').upper()
        inmuno = _g(d, 'inmunocompromiso', '').upper()
        cronica = _g(d, 'enfermedad_cronica', '').upper()

        self._a(_tbl([[
            _p(f'<b><font size="6">Paciente Vacunado:</font></b> '
               f'{_cb(vac in ("SI","SÍ"))} S\u00ed {_cb(vac=="NO")} No '
               f'{_cb(_is_desc(vac))} Desc. {_cb(vac=="VERBAL")} Verbal', S_CB_SM),
            _p(f'<b><font size="6">Antecedentes m\u00e9dicos:</font></b> '
               f'{_cb(_chk(antec))} S\u00ed {_cb(_is_no(antec))} No {_cb(_is_desc(antec))} Desc.<br/>'
               f'<font size="5">{_cb_sm(_chk(desn))} Desnutrici\u00f3n '
               f'{_cb_sm(_chk(inmuno))} Inmunocompromiso '
               f'{_cb_sm(_chk(cronica))} Enf.Cr\u00f3nica</font>', S_CB_SM),
        ]], [0.45, 0.55], 24))

        # Vaccine table: SPR / SR / SPRV rows x (Dosis | Fecha | Fuente Info | Sector)
        # Header
        fuente_vac = _g(d, 'fuente_info_vacuna', '').upper()
        sector_vac = _g(d, 'sector_vacunacion', '').upper()

        vac_hdr = [
            _p('<b>Vacuna</b>', S_HDR),
            _p('<b>Dosis</b>', S_HDR),
            _p('<b>Fecha</b>', S_HDR),
            _p('<b>Fuente de Informaci\u00f3n</b>', S_HDR),
            _p('<b>Sector</b>', S_HDR),
        ]

        # Helper to build per-row fuente/sector legends (only checked if row has data)
        def _fuente_for(has_data):
            if has_data:
                return (
                    f'{_cb_sm("CARNE" in fuente_vac or "CARNÉ" in fuente_vac)} Carn\u00e9 '
                    f'{_cb_sm("SIGSA 5A" in fuente_vac or "SIGSA5A" in fuente_vac)} SIGSA 5a '
                    f'{_cb_sm("SIGSA 5B" in fuente_vac or "SIGSA5B" in fuente_vac)} SIGSA 5B '
                    f'{_cb_sm("REGISTRO" in fuente_vac)} Reg.\u00danico '
                    f'{_cb_sm("VERBAL" in fuente_vac)} Verbal'
                )
            return (
                f'{_cb_sm(False)} Carn\u00e9 '
                f'{_cb_sm(False)} SIGSA 5a '
                f'{_cb_sm(False)} SIGSA 5B '
                f'{_cb_sm(False)} Reg.\u00danico '
                f'{_cb_sm(False)} Verbal'
            )

        def _sector_for(has_data):
            if has_data:
                return (
                    f'{_cb_sm("MSPAS" in sector_vac)} MSPAS '
                    f'{_cb_sm("IGSS" in sector_vac)} IGSS '
                    f'{_cb_sm("PRIVAD" in sector_vac)} Privado'
                )
            return (
                f'{_cb_sm(False)} MSPAS '
                f'{_cb_sm(False)} IGSS '
                f'{_cb_sm(False)} Privado'
            )

        # SPR row
        dosis_spr = _g(d, 'numero_dosis_spr', _g(d, 'dosis_spr', ''))
        fecha_spr = _g(d, 'fecha_ultima_dosis_spr', _g(d, 'fecha_ultima_dosis', ''))
        dd_s, mm_s, yy_s = _parse_date(fecha_spr)
        f_spr = f'{dd_s}/{mm_s}/{yy_s}' if dd_s else ''
        has_spr = bool(dosis_spr or dd_s)

        # SR row
        dosis_sr = _g(d, 'numero_dosis_sr', '')
        fecha_sr = _g(d, 'fecha_ultima_dosis_sr', '')
        dd_sr, mm_sr, yy_sr = _parse_date(fecha_sr)
        f_sr = f'{dd_sr}/{mm_sr}/{yy_sr}' if dd_sr else ''
        has_sr = bool(dosis_sr or dd_sr)

        # SPRV row
        dosis_sprv = _g(d, 'numero_dosis_sprv', '')
        fecha_sprv = _g(d, 'fecha_ultima_dosis_sprv', '')
        dd_sv, mm_sv, yy_sv = _parse_date(fecha_sprv)
        f_sprv = f'{dd_sv}/{mm_sv}/{yy_sv}' if dd_sv else ''
        has_sprv = bool(dosis_sprv or dd_sv)

        vac_rows = [
            vac_hdr,
            [_p('<b>SPR</b>', S_VALUE_SM), _p(dosis_spr, S_VALUE_C), _p(f_spr, S_VALUE_C),
             _p(_fuente_for(has_spr), S_CB_XS), _p(_sector_for(has_spr), S_CB_XS)],
            [_p('<b>SR</b>', S_VALUE_SM), _p(dosis_sr, S_VALUE_C), _p(f_sr, S_VALUE_C),
             _p(_fuente_for(has_sr), S_CB_XS), _p(_sector_for(has_sr), S_CB_XS)],
            [_p('<b>SPRV</b>', S_VALUE_SM), _p(dosis_sprv, S_VALUE_C), _p(f_sprv, S_VALUE_C),
             _p(_fuente_for(has_sprv), S_CB_XS), _p(_sector_for(has_sprv), S_CB_XS)],
        ]

        self._a(_tbl(vac_rows, [0.10, 0.07, 0.15, 0.45, 0.23],
                      [14, 16, 16, 16],
                      [('BACKGROUND', (0,0), (-1,0), LIGHT_GRAY),
                       ('ALIGN', (1,0), (2,-1), 'CENTER')]))

    # -- Section 4: DATOS CLÍNICOS --
    def _sec4(self):
        d = self.d
        self._a(_section_hdr('4. DATOS CL\u00cdNICOS'))

        # Row 1: Fecha Inicio Síntomas | Fecha Inicio Fiebre | Fecha Inicio Exantema/Rash
        self._a(_tbl([[
            _date_lv('Fecha Inicio S\u00edntomas', _g(d, 'fecha_inicio_sintomas')),
            _date_lv('Fecha Inicio Fiebre', _g(d, 'fecha_inicio_fiebre')),
            _date_lv('Fecha Inicio Exantema/Rash', _g(d, 'fecha_inicio_erupcion')),
        ]], [0.34, 0.33, 0.33], 24))

        # Signs table: 2 parallel columns
        left = [('Fiebre', 'signo_fiebre'), ('Exantema', 'signo_exantema'),
                ('Tos', 'signo_tos'), ('Conjuntivitis', 'signo_conjuntivitis')]
        right = [('Coriza', 'signo_coriza'), ('Koplik', 'signo_manchas_koplik'),
                 ('Artralgia', 'signo_artralgia'), ('Adenopat\u00edas', 'signo_adenopatias')]

        hdr = [_p('<b>Signo</b>', S_HDR), _p('<b>S\u00ed</b>', S_HDR), _p('<b>No</b>', S_HDR),
               _p('<b>Desc</b>', S_HDR),
               _p('<b>Signo</b>', S_HDR), _p('<b>S\u00ed</b>', S_HDR), _p('<b>No</b>', S_HDR),
               _p('<b>Desc</b>', S_HDR)]

        rows = [hdr]
        for i in range(4):
            ln, lk = left[i]
            rn, rk = right[i]
            lv, rv = _g(d, lk, ''), _g(d, rk, '')
            rows.append([
                _p(ln, S_VALUE_SM), _p(_cb(_chk(lv)), S_VALUE_C), _p(_cb(_is_no(lv)), S_VALUE_C), _p(_cb(_is_desc(lv)), S_VALUE_C),
                _p(rn, S_VALUE_SM), _p(_cb(_chk(rv)), S_VALUE_C), _p(_cb(_is_no(rv)), S_VALUE_C), _p(_cb(_is_desc(rv)), S_VALUE_C),
            ])

        sw = [0.15, 0.055, 0.055, 0.07, 0.02, 0.15, 0.055, 0.055, 0.07]
        # The middle col (0.02) is a separator — but that adds a 9th col.
        # Simpler: use 8 cols like before
        sw = [0.18, 0.055, 0.055, 0.07, 0.18, 0.055, 0.055, 0.07]
        rem = 1.0 - sum(sw)
        sw[3] += rem / 2
        sw[7] += rem / 2

        st = _tbl(rows, sw, [13] * 5,
                  [('BACKGROUND', (0,0), (-1,0), LIGHT_GRAY),
                   ('ALIGN', (1,0), (3,-1), 'CENTER'),
                   ('ALIGN', (5,0), (7,-1), 'CENTER')])
        self._a(st)

        # Row: Temp C°
        self._a(_tbl([[
            _lv('Temperatura C\u00b0', _g(d, 'temperatura_celsius')),
        ]], [1.0], 16))

        # Hospitalización
        hosp = _g(d, 'hospitalizado', '').upper()
        self._a(_tbl([[
            _p(f'<b><font size="6">Hospitalizaci\u00f3n:</font></b> {_cb(hosp in ("SI","SÍ"))} S\u00ed {_cb(hosp=="NO")} No {_cb(_is_desc(hosp))} Desc.', S_CB),
            _lv('Nombre Hospital', _g(d, 'hosp_nombre')),
            _date_lv('Fecha Hospitalizaci\u00f3n', _g(d, 'hosp_fecha')),
        ]], [0.30, 0.40, 0.30], 22))

        # Complicaciones
        comp = _g(d, 'complicaciones', '').upper()
        comp_det = _g(d, 'complicaciones_detalle', '').upper()
        self._a(_tbl([[
            _p(f'<b><font size="6">Complicaciones:</font></b> {_cb(_chk(comp))} S\u00ed {_cb(_is_no(comp))} No {_cb(_is_desc(comp))} Desc.', S_CB_SM),
            _p(f'{_cb_sm("NEUMON" in comp_det)} Neumon\u00eda '
               f'{_cb_sm("ENCEFAL" in comp_det)} Encefalitis '
               f'{_cb_sm("DIARR" in comp_det)} Diarrea '
               f'{_cb_sm("TROMB" in comp_det)} Trombocitopenia '
               f'{_cb_sm("OTITIS" in comp_det)} Otitis '
               f'{_cb_sm("CEGUE" in comp_det)} Ceguera '
               f'{_cb_sm("OTRA" in comp_det)} Otra', S_CB_XS),
        ]], [0.30, 0.70], 16))

        # Aislamiento Respiratorio
        aisl = _g(d, 'aislamiento_respiratorio', '').upper()
        self._a(_tbl([[
            _p(f'<b><font size="6">Aislamiento Respiratorio:</font></b> '
               f'{_cb(_chk(aisl))} S\u00ed {_cb(_is_no(aisl))} No {_cb(_is_desc(aisl))} Desc.', S_CB),
            _date_lv('Fecha Aislamiento', _g(d, 'fecha_aislamiento')),
        ]], [0.55, 0.45], 20))

    # ===================== PAGE 2 =====================

    # -- Section 5: FACTORES DE RIESGO --
    def _sec5(self):
        d = self.d
        self._a(_section_hdr('5. FACTORES DE RIESGO'))

        # Caso confirmado en comunidad
        caso_com = _g(d, 'caso_sospechoso_comunidad_3m', '')
        self._a(_tbl([[
            _p('<b><font size="6">Caso confirmado en la comunidad:</font></b>', S_LABEL),
            _p(f'{_cb(_chk(caso_com))} S\u00ed', S_CB_SM),
            _p(f'{_cb(_is_no(caso_com))} No', S_CB_SM),
            _p(f'{_cb(_is_desc(caso_com))} Desconocido', S_CB_SM),
        ]], [0.45, 0.12, 0.12, 0.31], 14))

        # Contacto con caso 7-23 días
        cont_7_23 = _g(d, 'contacto_sospechoso_7_23', '')
        self._a(_tbl([[
            _p('<b><font size="6">Contacto con caso 7-23 d\u00edas previos:</font></b>', S_LABEL),
            _p(f'{_cb(_chk(cont_7_23))} S\u00ed', S_CB_SM),
            _p(f'{_cb(_is_no(cont_7_23))} No', S_CB_SM),
            _p(f'{_cb(_is_desc(cont_7_23))} Desconocido', S_CB_SM),
        ]], [0.45, 0.12, 0.12, 0.31], 14))

        # Viajó 7-23 días
        viajo = _g(d, 'viajo_7_23_previo', '')
        self._a(_tbl([[
            _p(f'<b><font size="6">Viaj\u00f3 7-23 d\u00edas previos:</font></b> {_cb(_chk(viajo))} S\u00ed {_cb(_is_no(viajo))} No', S_CB),
            _lv('Pa\u00eds/Depto/Municipio', _g(d, 'lugar_viaje', _g(d, 'procedencia_contacto'))),
        ]], [0.40, 0.60], 18))

        # Fecha Salida | Fecha Entrada | Persona viajó exterior | Fecha Retorno
        self._a(_tbl([[
            _date_lv('Fecha Salida', _g(d, 'fecha_salida_viaje')),
            _date_lv('Fecha Entrada', _g(d, 'fecha_entrada_viaje')),
            _p(f'<b><font size="6">Persona viaj\u00f3 al exterior:</font></b> '
               f'{_cb(_chk(_g(d, "persona_viajo_exterior")))} S\u00ed '
               f'{_cb(_is_no(_g(d, "persona_viajo_exterior")))} No', S_CB_SM),
            _date_lv('Fecha Retorno', _g(d, 'fecha_retorno_viaje')),
        ]], [0.22, 0.22, 0.34, 0.22], 24))

        # Contacto embarazada
        cont_emb = _g(d, 'contacto_embarazada', '')
        self._a(_tbl([[
            _p(f'<b><font size="6">Contacto con Embarazada:</font></b> '
               f'{_cb(_chk(cont_emb))} S\u00ed {_cb(_is_no(cont_emb))} No '
               f'{_cb(_is_desc(cont_emb))} Desconocido', S_CB),
        ]], [1.0], 14))

        # Fuente posible de contagio (9 checkboxes)
        fuente_cont = _g(d, 'fuente_posible_contagio', '').upper()
        fc_items = [
            ('Hogar', 'HOGAR'), ('Trabajo', 'TRABAJO'), ('Escuela', 'ESCUELA'),
            ('Viaje', 'VIAJE'), ('Hospital', 'HOSPITAL'), ('Mercado', 'MERCADO'),
            ('Transporte', 'TRANSPORTE'), ('Evento masivo', 'EVENTO'),
            ('Otro', 'OTRO'),
        ]
        fc_str = ' '.join(f'{_cb_sm(k in fuente_cont)} {l}' for l, k in fc_items)
        self._a(_tbl([[
            _p('<b><font size="6">Fuente posible de contagio:</font></b>', S_LABEL),
            _p(fc_str, S_CB_XS),
        ]], [0.22, 0.78], 15))

        # Contacto confirmado
        cont_conf = _g(d, 'contacto_confirmado', '')
        self._a(_tbl([[
            _p(f'<b><font size="6">Contacto con caso confirmado de sarampi\u00f3n o rub\u00e9ola:</font></b> '
               f'{_cb(_chk(cont_conf))} S\u00ed {_cb(_is_no(cont_conf))} No', S_CB),
        ]], [1.0], 14))

    # -- Section 6: ACCIONES DE RESPUESTA --
    def _sec6(self):
        d = self.d
        self._a(_section_hdr('6. ACCIONES DE RESPUESTA'))

        bai = _g(d, 'busqueda_activa_institucional', '')
        bai_num = _g(d, 'bai_numero_casos', '')
        bac = _g(d, 'busqueda_activa_comunitaria', '')
        bac_num = _g(d, 'bac_numero_casos', '')
        blq = _g(d, 'vacunacion_bloqueo', '')
        mrc = _g(d, 'monitoreo_rapido_coberturas', '')
        barrido = _g(d, 'barrido_vacunacion', '')
        vitA = _g(d, 'vitamina_a', '')
        vitA_dosis = _g(d, 'vitamina_a_dosis', '')

        self._a(_tbl([
            [_p(f'<b>BAI:</b> {_cb(_chk(bai))} S\u00ed {_cb(_is_no(bai))} No', S_CB),
             _lv('N\u00famero de casos BAI', bai_num),
             _p(f'<b>BAC:</b> {_cb(_chk(bac))} S\u00ed {_cb(_is_no(bac))} No', S_CB),
             _lv('N\u00famero de casos BAC', bac_num)],
            [_p(f'<b>Vacunaci\u00f3n bloqueo:</b> {_cb(_chk(blq))} S\u00ed {_cb(_is_no(blq))} No', S_CB),
             _p(f'<b>Monitoreo r\u00e1pido:</b> {_cb(_chk(mrc))} S\u00ed {_cb(_is_no(mrc))} No', S_CB),
             _p(f'<b>Barrido:</b> {_cb(_chk(barrido))} S\u00ed {_cb(_is_no(barrido))} No', S_CB),
             _p(f'<b>Vitamina A:</b> {_cb(_chk(vitA))} S\u00ed {_cb(_is_no(vitA))} No Dosis: {vitA_dosis}', S_CB_SM)],
        ], [0.25, 0.25, 0.25, 0.25], [15, 15]))

        self._a(_tbl([[_lv('Observaciones acciones de respuesta', _g(d, 'observaciones_acciones'))]], [1.0], 20))

    # -- Section 7: LABORATORIO --
    def _sec7(self):
        d = self.d
        self._a(_section_hdr('7. LABORATORIO'))

        # Tipo muestra checkboxes
        tipo_m = _g(d, 'tipo_muestra', '').upper()
        rec = _g(d, 'recolecto_muestra', '').upper()
        self._a(_tbl([[
            _p(f'<b><font size="6">Tipo Muestra:</font></b> '
               f'{_cb_sm("SUERO" in tipo_m or rec in ("SI","SÍ"))} Suero '
               f'{_cb_sm("ORINA" in tipo_m)} Orina '
               f'{_cb_sm("HISOP" in tipo_m)} Hisopado NF '
               f'{_cb_sm("OTRO" in tipo_m)} Otro', S_CB_SM),
            _lv('\u00bfPor qu\u00e9 no 3 muestras?', _g(d, 'motivo_no_3_muestras', _g(d, 'motivo_no_recoleccion'))),
        ]], [0.45, 0.55], 18))

        # Lab results matrix: 5 rows x multiple cols
        # Cols: Muestra | No.Muestra | F.Toma | F.Envío | Sarampión(IgM|IgG|Avidez) | Rubéola(IgM|IgG|Avidez) | Secuenciación
        cw = [0.10, 0.07, 0.08, 0.08, 0.065, 0.065, 0.065, 0.065, 0.065, 0.065, 0.08]
        rem = 1.0 - sum(cw)
        cw[-1] += rem

        # Header row 1: spans for Sarampión and Rubéola
        h1 = [_p('', S_HDR), _p('', S_HDR), _p('', S_HDR), _p('', S_HDR),
              _p('<b>Sarampi\u00f3n</b>', S_HDR), '', '',
              _p('<b>Rub\u00e9ola</b>', S_HDR), '', '',
              _p('', S_HDR)]

        # Header row 2
        h2 = [_p('<b>Muestra</b>', S_HDR), _p('<b>No.</b>', S_HDR),
              _p('<b>F.Toma</b>', S_HDR), _p('<b>F.Env\u00edo</b>', S_HDR),
              _p('<b>IgM</b>', S_HDR), _p('<b>IgG</b>', S_HDR), _p('<b>Avidez</b>', S_HDR),
              _p('<b>IgM</b>', S_HDR), _p('<b>IgG</b>', S_HDR), _p('<b>Avidez</b>', S_HDR),
              _p('<b>Secuenc.</b>', S_HDR)]

        muestras = [
            ('Suero 1', 'muestra_suero_fecha', 'muestra_suero_envio', 'suero'),
            ('Suero 2', 'muestra_suero2_fecha', 'muestra_suero2_envio', 'suero2'),
            ('Orina', 'muestra_orina_fecha', 'muestra_orina_envio', 'orina'),
            ('Hisopado NF', 'muestra_hisopado_fecha', 'muestra_hisopado_envio', 'hisopado'),
            ('Otro', 'muestra_otro_fecha', 'muestra_otro_envio', 'otro'),
        ]

        def _res(v):
            vu = (v or '').upper()
            if vu in ('POSITIVO', 'POS', 'REACTIVO', '+', 'SI', '1'): return '+'
            if vu in ('NEGATIVO', 'NEG', 'NO REACTIVO', '-', 'NO', '0'): return '-'
            if vu in ('INDETERMINADO', 'IND', '3'): return '?'
            if vu in ('INADECUADO', 'INADEC', '2'): return 'Inadec'
            return (v or '')[:6]

        data_rows = []
        for ml, ft, fe, pfx in muestras:
            dd_t, mm_t, yy_t = _parse_date(_g(d, ft))
            dd_e, mm_e, yy_e = _parse_date(_g(d, fe))
            ft_s = f'{dd_t}/{mm_t}' if dd_t else ''
            fe_s = f'{dd_e}/{mm_e}' if dd_e else ''
            no_muestra = _g(d, f'no_muestra_{pfx}', '')

            data_rows.append([
                _p(ml, S_VALUE_SM), _p(no_muestra, S_VALUE_C),
                _p(ft_s, S_VALUE_C), _p(fe_s, S_VALUE_C),
                _p(_res(_g(d, f'resultado_igm_sarampion_{pfx}', _g(d, 'resultado_igm_cualitativo', '') if pfx == 'suero' else '')), S_VALUE_C),
                _p(_res(_g(d, f'resultado_igg_sarampion_{pfx}', _g(d, 'resultado_igg_cualitativo', '') if pfx == 'suero' else '')), S_VALUE_C),
                _p(_res(_g(d, f'resultado_avidez_sarampion_{pfx}', '')), S_VALUE_C),
                _p(_res(_g(d, f'resultado_igm_rubeola_{pfx}', '')), S_VALUE_C),
                _p(_res(_g(d, f'resultado_igg_rubeola_{pfx}', '')), S_VALUE_C),
                _p(_res(_g(d, f'resultado_avidez_rubeola_{pfx}', '')), S_VALUE_C),
                _p(_res(_g(d, f'resultado_secuenciacion_{pfx}', '')), S_VALUE_C),
            ])

        all_rows = [h1, h2] + data_rows
        rh = [13, 14] + [14] * len(data_rows)

        self._a(_tbl(all_rows, cw, rh, [
            ('BACKGROUND', (0,0), (-1,1), LIGHT_GRAY),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('SPAN', (4,0), (6,0)),   # Sarampión
            ('SPAN', (7,0), (9,0)),   # Rubéola
            ('SPAN', (0,0), (0,1)),   # Muestra
            ('SPAN', (1,0), (1,1)),   # No.
            ('SPAN', (2,0), (2,1)),   # F.Toma
            ('SPAN', (3,0), (3,1)),   # F.Envío
            ('SPAN', (10,0), (10,1)), # Secuenc
        ]))

        # Results legend
        self._a(_tbl([[
            _p('<font size="4.5"><b>Resultados:</b> 0=Negativo  1=Positivo  2=Inadecuado  3=Indeterminado  4=No procesado  5=Alta avidez  6=Baja avidez</font>', S_LEGEND),
        ]], [1.0], 10))

        # Lab receptor
        self._a(_tbl([[
            _lv('Laboratorio receptor', _g(d, 'laboratorio_receptor', 'Lab. Nacional de Salud (LNS)')),
            _date_lv('Fecha recepci\u00f3n LNS', _g(d, 'fecha_recepcion_laboratorio')),
            _date_lv('Fecha resultado LNS', _g(d, 'fecha_resultado_laboratorio')),
        ]], [0.40, 0.30, 0.30], 18))

    def _page2_with_contacts(self):
        self._sec5()
        self._sp(1)
        self._sec6()
        self._sp(1)
        self._sec7()
        self._sp(1)
        self._sec8()

    # -- Section 8: CLASIFICACIÓN --
    def _sec8(self):
        """Section 8 with classification, then signatures."""
        d = self.d
        self._a(_section_hdr('8. CLASIFICACI\u00d3N'))

        # Clasificación Final
        cl = _g(d, 'clasificacion_caso', '').upper()
        self._a(_tbl([[
            _p('<b><font size="6">Clasificaci\u00f3n Final:</font></b>', S_LABEL),
            _p(f'{_cb("SARAMP" in cl)} Sarampi\u00f3n '
               f'{_cb("RUBEO" in cl or "RUBÉO" in cl)} Rub\u00e9ola '
               f'{_cb("DESCART" in cl)} Descartado '
               f'{_cb("PENDIENT" in cl)} Pendiente '
               f'{_cb("NO CUMPLE" in cl)} No cumple def.', S_CB_SM),
        ]], [0.18, 0.82], 16))

        # Criterio Confirmación
        crit_conf = _g(d, 'criterio_confirmacion', '').upper()
        cont_otro = _g(d, 'contacto_otro_caso', '')
        self._a(_tbl([[
            _p(f'<b><font size="6">Criterio Confirmaci\u00f3n:</font></b> '
               f'{_cb("LAB" in crit_conf)} Laboratorio '
               f'{_cb("NEXO" in crit_conf)} Nexo Epidemiol\u00f3gico '
               f'{_cb("CLIN" in crit_conf)} Cl\u00ednico', S_CB_SM),
            _p(f'<b><font size="6">Contacto Otro Caso:</font></b> '
               f'{_cb(_chk(cont_otro))} S\u00ed {_cb(_is_no(cont_otro))} No', S_CB_SM),
        ]], [0.65, 0.35], 16))

        # Criterio Descartar
        crit_desc = _g(d, 'criterio_descarte', '').upper()
        self._a(_tbl([[
            _p(f'<b><font size="6">Criterio para Descartar:</font></b> '
               f'{_cb("LAB" in crit_desc)} Laboratorio '
               f'{_cb("VACUN" in crit_desc)} Vacuna '
               f'{_cb("CLIN" in crit_desc)} Cl\u00ednico', S_CB_SM),
        ]], [1.0], 15))

        # Fuente Infección
        fuente_inf = _g(d, 'fuente_infeccion', '').upper()
        self._a(_tbl([[
            _p(f'<b><font size="6">Fuente Infecci\u00f3n:</font></b> '
               f'{_cb("IMPORT" in fuente_inf)} Importado '
               f'{_cb("RELACION" in fuente_inf)} Relacionado '
               f'{_cb("ENDEM" in fuente_inf or "ENDÉM" in fuente_inf)} End\u00e9mico '
               f'{_cb("DESCON" in fuente_inf)} Desconocida', S_CB_SM),
            _lv('Pa\u00eds', _g(d, 'pais_fuente_infeccion')),
        ]], [0.70, 0.30], 16))

        # Caso Analizado Por
        analiz = _g(d, 'caso_analizado_por', '').upper()
        self._a(_tbl([[
            _p(f'<b><font size="6">Caso Analizado Por:</font></b> '
               f'{_cb("CONAPI" in analiz)} CONAPI '
               f'{_cb("DEGR" in analiz)} DEGR '
               f'{_cb("COMISION" in analiz or "COMISIÓN" in analiz)} Comisi\u00f3n '
               f'{_cb("OTRO" in analiz)} Otros', S_CB_SM),
        ]], [1.0], 15))

        # Fecha Clasificación | Condición Final
        egreso = _g(d, 'condicion_egreso', _g(d, 'condicion_final_paciente', '')).upper()
        self._a(_tbl([[
            _date_lv('Fecha Clasificaci\u00f3n', _g(d, 'fecha_clasificacion_final')),
            _p(f'<b><font size="6">Condici\u00f3n Final:</font></b> '
               f'{_cb("RECUP" in egreso or "MEJOR" in egreso)} Recuperado '
               f'{_cb("SECUEL" in egreso)} Con Secuelas '
               f'{_cb("FALLEC" in egreso or "MUERT" in egreso)} Fallecido '
               f'{_cb("DESCON" in egreso or _is_desc(egreso))} Desconocido', S_CB_SM),
        ]], [0.30, 0.70], 22))

        # Fecha Defunción | Causa Muerte
        self._a(_tbl([[
            _date_lv('Fecha Defunci\u00f3n', _g(d, 'fecha_defuncion')),
            _lv('Causa de Muerte', _g(d, 'causa_muerte')),
        ]], [0.35, 0.65], 22))

        # Observaciones
        self._a(_tbl([[_lv('Observaciones', _g(d, 'observaciones'))]], [1.0], 28))

        # Signatures
        self._sp(6)
        sig_style = ParagraphStyle('sig', parent=S_VALUE, alignment=TA_CENTER, fontSize=6)
        sig = Table([[
            _p('_' * 35 + '<br/><b>Firma del Investigador</b>', sig_style),
            _p('_' * 35 + '<br/><b>Firma del Responsable</b>', sig_style),
            _p('_' * 35 + '<br/><b>Sello</b>', sig_style),
        ]], colWidths=[CONTENT_W * 0.33, CONTENT_W * 0.34, CONTENT_W * 0.33],
           rowHeights=[30])
        sig.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        self._a(sig)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generar_ficha_v2_pdf(data: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="Ficha Epidemiologica - Sarampion/Rubeola",
        author="IGSS Epidemiologia")
    elements = FichaBuilder(data).build()
    doc.build(elements)
    buf.seek(0)
    return buf.read()


def generar_fichas_v2_bulk(records: list, merge: bool = True) -> bytes:
    if not records:
        raise ValueError("No records provided")
    if merge:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=LETTER,
            leftMargin=MARGIN, rightMargin=MARGIN,
            topMargin=MARGIN, bottomMargin=MARGIN,
            title="Fichas Epidemiologicas - Sarampion/Rubeola",
            author="IGSS Epidemiologia")
        all_el = []
        for data in records:
            all_el.extend(FichaBuilder(data).build())
        doc.build(all_el)
        buf.seek(0)
        return buf.read()
    else:
        zbuf = io.BytesIO()
        with zipfile.ZipFile(zbuf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, data in enumerate(records):
                pdf = generar_ficha_v2_pdf(data)
                n = _g(data, 'nombres', 'caso')
                a = _g(data, 'apellidos', '')
                zf.writestr(f"{i+1:03d}_{n}_{a}.pdf".replace(' ', '_'), pdf)
        zbuf.seek(0)
        return zbuf.read()


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    sample = {
        'nombres': 'LUISA FERNANDA', 'apellidos': 'RAMIREZ CASTILLO DE LOPEZ',
        'sexo': 'F', 'fecha_nacimiento': '1988-11-20', 'edad_anios': '37',
        'edad_meses': '4', 'edad_dias': '5',
        'diagnostico_sospecha': 'Sarampion',
        'departamento_residencia': 'QUETZALTENANGO', 'municipio_residencia': 'QUETZALTENANGO',
        'poblado': 'QUETZALTENANGO - CIUDAD',
        'direccion_exacta': '12 Avenida 5-67 Zona 3, Quetzaltenango',
        'pueblo_etnia': 'Maya', 'comunidad_linguistica': "K'iche'",
        'unidad_medica': 'HOSPITAL GENERAL DE QUETZALTENANGO',
        'fecha_notificacion': '2026-03-25',
        'fecha_registro_diagnostico': '2026-03-25',
        'nom_responsable': 'DRA. CARMEN PATRICIA LOPEZ',
        'cargo_responsable': 'EPIDEMIOLOGA',
        'telefono_responsable': '5555-1234',
        'nombre_encargado': 'CARLOS EDUARDO RAMIREZ LOPEZ',
        'ocupacion': 'Enfermera', 'escolaridad': 'Universitario',
        'signo_fiebre': 'SI', 'signo_exantema': 'SI', 'signo_tos': 'SI',
        'signo_coriza': 'SI', 'signo_conjuntivitis': 'SI',
        'signo_manchas_koplik': 'NO', 'signo_artralgia': 'DESCONOCIDO',
        'signo_adenopatias': 'DESCONOCIDO',
        'temperatura_celsius': '39.5',
        'hospitalizado': 'SI', 'hosp_nombre': 'Hospital General de Quetzaltenango IGSS',
        'hosp_fecha': '2026-03-22',
        'complicaciones': 'NO',
        'aislamiento_respiratorio': 'SI', 'fecha_aislamiento': '2026-03-22',
        'clasificacion_caso': 'CONFIRMADO SARAMPION',
        'condicion_final_paciente': 'Recuperado',
        'recolecto_muestra': 'SI',
        'vacunado': 'SI', 'dosis_spr': '2', 'fuente_info_vacuna': 'Carne de Vacunacion',
        'sector_vacunacion': 'IGSS',
        'fecha_inicio_sintomas': '2026-03-18', 'semana_epidemiologica': '13',
        'fecha_captacion': '2026-03-20',
        'fecha_inicio_erupcion': '2026-03-19', 'fecha_inicio_fiebre': '2026-03-18',
        'contacto_sospechoso_7_23': 'SI', 'caso_sospechoso_comunidad_3m': 'NO',
        'viajo_7_23_previo': 'SI',
        'lugar_viaje': 'Ciudad de Guatemala',
        'contacto_confirmado': 'NO',
        'busqueda_activa_institucional': 'SI',
        'busqueda_activa_comunitaria': 'SI',
        'vacunacion_bloqueo': 'SI',
        'monitoreo_rapido_coberturas': 'SI',
        'muestra_suero_fecha': '2026-03-20', 'muestra_hisopado_fecha': '2026-03-20',
        'muestra_orina_fecha': '2026-03-21',
        'fecha_recepcion_laboratorio': '2026-03-21', 'fecha_resultado_laboratorio': '2026-03-24',
        'resultado_igm_cualitativo': 'POSITIVO', 'resultado_igg_cualitativo': 'NEGATIVO',
        'resultado_igm_sarampion_suero': 'POSITIVO', 'resultado_igg_sarampion_suero': 'POSITIVO',
        'resultado_igm_sarampion_suero2': 'POSITIVO', 'resultado_igg_sarampion_suero2': 'POSITIVO',
        'resultado_igm_sarampion_hisopado': 'POSITIVO', 'resultado_igg_sarampion_hisopado': 'POSITIVO',
        'resultado_secuenciacion_hisopado': 'POSITIVO',
        'resultado_igm_sarampion_orina': 'POSITIVO', 'resultado_igg_sarampion_orina': 'NEGATIVO',
        'resultado_secuenciacion_orina': 'POSITIVO',
        'fecha_clasificacion_final': '2026-03-25',
        'responsable_clasificacion': 'DRA. CARMEN PATRICIA LOPEZ MENDEZ',
        'observaciones': 'Caso confirmado. IgM reactivo 4.85, PCR positivo genotipo D8. 12 contactos en seguimiento.',
    }
    pdf = generar_ficha_v2_pdf(sample)
    out = '/tmp/ficha_audit_final.pdf'
    with open(out, 'wb') as f:
        f.write(pdf)
    print(f"PDF: {out} ({len(pdf)} bytes, valid={pdf[:5] == b'%PDF-'})")
