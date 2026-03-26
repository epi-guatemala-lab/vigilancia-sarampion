"""
PDF Generator for MSPAS Sarampion/Rubeola Epidemiological Form — Version 2026.

Generates a replica of the official MSPAS ficha epidemiologica 2026 using
reportlab Canvas with absolute coordinate positioning.

Public API:
    generar_ficha_v2_pdf(data: dict) -> bytes
    generar_fichas_v2_bulk(records: list, merge: bool = True) -> bytes
"""

import io
import os
import zipfile
import logging
from datetime import datetime

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import Color, black, white

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = LETTER   # 612 x 792 pt
MARGIN = 20
CONTENT_W = PAGE_W - 2 * MARGIN  # ~572 pt

# Colors
SECTION_BG    = Color(0.102, 0.137, 0.494, 1)  # #1a237e — MSPAS dark blue 2026
SECTION_LIGHT = Color(0.153, 0.196, 0.600, 1)  # lighter strip for gradient
LIGHT_GRAY    = Color(0.92, 0.92, 0.92, 1)
MED_GRAY      = Color(0.75, 0.75, 0.75, 1)
DIAG_BG       = Color(0.95, 0.95, 0.98, 1)     # very light blue for diag area

# Row heights
SECTION_H  = 14    # section header bar
RH         = 20    # standard row (label + value)
RH_DATE    = 26    # row with date boxes
RH_TALL    = 34    # tall row (observaciones, etc.)
RH_SM      = 16    # small/compact row

# Sizes
CB_SIZE    = 7.5   # checkbox square side
DATE_BOX   = 8.5   # individual digit box
TRI_CB     = 7.0   # tri-state (Si/No/Desconocido) checkbox

# Fonts
F_SECTION   = ("Helvetica-Bold", 8.5)
F_LABEL     = ("Helvetica-Bold", 5.5)
F_VALUE     = ("Helvetica", 7)
F_BOLD6     = ("Helvetica-Bold", 6)
F_BOLD7     = ("Helvetica-Bold", 7)
F_SMALL     = ("Helvetica", 3.2)
F_TITLE_LG  = ("Helvetica-Bold", 9)
F_TITLE_MD  = ("Helvetica-Bold", 8)
F_TITLE_SM  = ("Helvetica-Bold", 7)
F_TITLE_XS  = ("Helvetica-Bold", 6)
F_ITALIC    = ("Helvetica-Oblique", 5)
F_CHECK     = ("Helvetica-Bold", 10)
F_DATE_DIG  = ("Helvetica", 6)
F_CB_LABEL  = ("Helvetica", 5.5)
F_HDR_SM    = ("Helvetica", 4.5)
F_HDR_BOX   = ("Helvetica-Bold", 5.5)
F_FACTOR    = ("Helvetica", 5.2)
F_CONTACT   = ("Helvetica", 5.0)
F_LAB_HDR   = ("Helvetica-Bold", 5)
F_LAB_VAL   = ("Helvetica", 5)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get(data: dict, key: str, default: str = '') -> str:
    val = data.get(key, '') or ''
    val = str(val).strip()
    if val.upper() in ('NONE', 'NULL', 'N/A', 'NAN', ''):
        return default
    return val


def _parse_date(val: str) -> tuple:
    """Return (dd, mm, yyyy) strings or empty strings if unparseable."""
    if not val:
        return ('', '', '')
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S', '%d-%m-%Y'):
        try:
            dt = datetime.strptime(val.strip()[:10], fmt)
            return (f"{dt.day:02d}", f"{dt.month:02d}", f"{dt.year:04d}")
        except (ValueError, TypeError):
            continue
    return ('', '', '')


def _trunc(text: str, w: float, cw: float = 3.4) -> str:
    mx = max(3, int(w / cw))
    if len(text) > mx:
        return text[:mx - 1] + '\u2026'
    return text


def _yn(val: str, positive: str) -> bool:
    """True if val matches positive keyword."""
    return str(val).strip().upper() == positive.upper()


def _chk(v) -> bool:
    """Truthy check for checkbox state."""
    return str(v).strip().upper() in ('SI', 'SÍ', 'S', '1', 'TRUE', 'X', 'YES')


# ---------------------------------------------------------------------------
# FichaV2Builder — 2026 MSPAS format
# ---------------------------------------------------------------------------

class FichaV2Builder:

    def __init__(self, c: Canvas, data: dict):
        self.c = c
        self.d = data
        self.y = PAGE_H - MARGIN

    # -----------------------------------------------------------------------
    # Low-level primitives
    # -----------------------------------------------------------------------

    def _sf(self, f):
        self.c.setFont(f[0], f[1])

    def _rect(self, x, y, w, h, fill=False, fill_color=None, lw=0.5):
        self.c.setStrokeColor(black)
        self.c.setLineWidth(lw)
        if fill and fill_color is not None:
            self.c.setFillColor(fill_color)
            self.c.rect(x, y, w, h, fill=1)
            self.c.setFillColor(black)
        else:
            self.c.rect(x, y, w, h, fill=0)

    def _cell(self, x, y, w, h, label='', value='', label_color=None):
        """Bordered cell: small bold label top-left, value below."""
        self._rect(x, y, w, h)
        if label:
            self._sf(F_LABEL)
            self.c.setFillColor(label_color or black)
            self.c.drawString(x + 2, y + h - 7.5, _trunc(label, w - 4, 3.0))
            self.c.setFillColor(black)
        if value:
            self._sf(F_VALUE)
            self.c.setFillColor(black)
            self.c.drawString(x + 2, y + h - 15, _trunc(value, w - 4, 3.4))

    def _cell_plain(self, x, y, w, h, text='', font=None, center=False, bg=None):
        """Bordered cell with single centered/left text."""
        if bg:
            self.c.setFillColor(bg)
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.5)
            self.c.rect(x, y, w, h, fill=1)
            self.c.setFillColor(black)
        else:
            self._rect(x, y, w, h)
        if text:
            f = font or F_VALUE
            self._sf(f)
            self.c.setFillColor(black)
            ty = y + (h - f[1]) / 2
            if center:
                self.c.drawCentredString(x + w / 2, ty, _trunc(text, w - 3, 3.0))
            else:
                self.c.drawString(x + 2, ty, _trunc(text, w - 4, 3.0))

    def _section(self, title, subtitle=None):
        """Dark-blue section header bar — MSPAS 2026 style."""
        h = SECTION_H
        y = self.y - h
        # Gradient: lighter strip at top third
        self.c.setFillColor(SECTION_LIGHT)
        self.c.rect(MARGIN, y + h * 0.55, CONTENT_W, h * 0.45, fill=1, stroke=0)
        self.c.setFillColor(SECTION_BG)
        self.c.rect(MARGIN, y, CONTENT_W, h * 0.55, fill=1, stroke=0)
        # Border
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.6)
        self.c.rect(MARGIN, y, CONTENT_W, h, fill=0, stroke=1)
        # Title
        self.c.setFillColor(white)
        self._sf(F_SECTION)
        cx = MARGIN + CONTENT_W / 2
        if subtitle:
            self.c.drawCentredString(cx, y + h - 9, title)
            self._sf(F_HDR_SM)
            self.c.drawCentredString(cx, y + 2.5, subtitle)
        else:
            self.c.drawCentredString(cx, y + (h - F_SECTION[1]) / 2 + 0.5, title)
        self.c.setFillColor(black)
        self.y -= h

    def _subsection(self, text, bg_color=None):
        """Subtle sub-section label row."""
        h = 11
        y = self.y - h
        bg = bg_color or LIGHT_GRAY
        self.c.setFillColor(bg)
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.4)
        self.c.rect(MARGIN, y, CONTENT_W, h, fill=1)
        self.c.setFillColor(black)
        self._sf(F_BOLD6)
        self.c.drawString(MARGIN + 3, y + 2.5, text)
        self.y -= h

    def _checkbox(self, x, y, checked=False, label='', size=None):
        """Draw checkbox. Returns x after the label."""
        s = size or CB_SIZE
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.6)
        self.c.rect(x, y, s, s)
        if checked:
            self._sf(F_CHECK)
            self.c.setFillColor(black)
            self.c.drawCentredString(x + s / 2, y + (s - F_CHECK[1]) / 2 - 0.3, 'X')
        nx = x + s + 1.5
        if label:
            self._sf(F_CB_LABEL)
            self.c.setFillColor(black)
            self.c.drawString(nx, y + 1, label)
            nx += len(label) * 3.1 + 2
        return nx

    def _tri_checkbox(self, x, y, value: str, label=''):
        """Three-state (Sí / No / Desc) checkbox group. Returns next x."""
        v = value.upper()
        nx = x
        if label:
            self._sf(F_CB_LABEL)
            self.c.setFillColor(black)
            self.c.drawString(nx, y + 1, label)
            nx += len(label) * 3.1 + 3
        nx = self._checkbox(nx, y, checked=(v in ('SI', 'SÍ', '1')), label='Sí', size=TRI_CB)
        nx = self._checkbox(nx, y, checked=(v == 'NO'), label='No', size=TRI_CB)
        nx = self._checkbox(nx, y, checked=(v in ('DESCONOCIDO', 'DESC', 'NK', '?')), label='Desc', size=TRI_CB)
        return nx

    def _date_cell(self, x, y, w, h, label='', date_str=''):
        """Cell with label + Día/Mes/Año digit boxes."""
        self._rect(x, y, w, h)
        if label:
            self._sf(F_LABEL)
            self.c.setFillColor(black)
            self.c.drawString(x + 2, y + h - 7.5, _trunc(label, w - 4, 3.0))
        dd, mm, yyyy = _parse_date(date_str)
        bs = DATE_BOX
        bx = x + 3
        by = y + 2

        # Día
        self._sf(F_SMALL)
        self.c.setFillColor(black)
        self.c.drawCentredString(bx + bs, by + bs + 1.5, 'Día')
        for i, ch in enumerate(dd.ljust(2)):
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.35)
            self.c.rect(bx + i * bs, by, bs, bs)
            if ch.strip():
                self._sf(F_DATE_DIG)
                self.c.setFillColor(black)
                self.c.drawCentredString(bx + i * bs + bs / 2, by + 1.5, ch)
        bx += 2 * bs + 3

        # Mes
        self._sf(F_SMALL)
        self.c.setFillColor(black)
        self.c.drawCentredString(bx + bs, by + bs + 1.5, 'Mes')
        for i, ch in enumerate(mm.ljust(2)):
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.35)
            self.c.rect(bx + i * bs, by, bs, bs)
            if ch.strip():
                self._sf(F_DATE_DIG)
                self.c.setFillColor(black)
                self.c.drawCentredString(bx + i * bs + bs / 2, by + 1.5, ch)
        bx += 2 * bs + 3

        # Año
        self._sf(F_SMALL)
        self.c.setFillColor(black)
        self.c.drawCentredString(bx + 2 * bs, by + bs + 1.5, 'Año')
        for i, ch in enumerate(yyyy.ljust(4)):
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.35)
            self.c.rect(bx + i * bs, by, bs, bs)
            if ch.strip():
                self._sf(F_DATE_DIG)
                self.c.setFillColor(black)
                self.c.drawCentredString(bx + i * bs + bs / 2, by + 1.5, ch)

    def _row(self, fields, h=RH):
        """Row of labeled cells. fields = [(frac, label, value), ...]"""
        x = MARGIN
        y = self.y - h
        for wf, lbl, val in fields:
            w = CONTENT_W * wf
            self._cell(x, y, w, h, lbl, val)
            x += w
        self.y -= h

    def _hline(self, lw=0.3):
        self.c.setStrokeColor(MED_GRAY)
        self.c.setLineWidth(lw)
        self.c.line(MARGIN, self.y, MARGIN + CONTENT_W, self.y)
        self.c.setStrokeColor(black)

    # -----------------------------------------------------------------------
    # PAGE 1
    # -----------------------------------------------------------------------

    def draw_page1(self):
        self.y = PAGE_H - MARGIN
        self._p1_header()
        self._p1_diagnostic_checkboxes()
        self._s1_unidad_notificadora()
        self._s2_informacion_paciente()
        self._s3_antecedentes_vacunacion()
        self._s4_datos_clinicos()

    def _p1_header(self):
        c = self.c
        top = self.y

        # Logo
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        logo_path = None
        for fname in ('escudo_guatemala.png', 'mspas_logo.png'):
            cand = os.path.join(assets_dir, fname)
            if os.path.isfile(cand):
                logo_path = cand
                break

        logo_sz = 42
        lx, ly = MARGIN, top - logo_sz
        if logo_path:
            try:
                c.drawImage(logo_path, lx, ly, width=logo_sz, height=logo_sz,
                            preserveAspectRatio=True, mask='auto')
            except Exception:
                logo_path = None
        if not logo_path:
            c.setStrokeColor(black)
            c.setLineWidth(0.7)
            c.rect(lx, ly, logo_sz, logo_sz)
            c.setLineWidth(0.3)
            c.rect(lx + 2, ly + 2, logo_sz - 4, logo_sz - 4)
            self._sf(("Helvetica-Bold", 6.5))
            c.setFillColor(Color(0.25, 0.25, 0.25))
            c.drawCentredString(lx + logo_sz / 2, ly + logo_sz / 2 + 3, 'MSPAS')
            self._sf(("Helvetica", 4.5))
            c.drawCentredString(lx + logo_sz / 2, ly + logo_sz / 2 - 5, 'Guatemala')
            c.setFillColor(black)

        # Center titles
        title_x = MARGIN + logo_sz + 8
        title_right_edge = MARGIN + CONTENT_W - 155
        tc = (title_x + title_right_edge) / 2

        self._sf(F_TITLE_LG)
        c.setFillColor(SECTION_BG)
        c.drawCentredString(tc, top - 12, "MINISTERIO DE SALUD PÚBLICA Y ASISTENCIA SOCIAL")
        self._sf(F_TITLE_MD)
        c.setFillColor(black)
        c.drawCentredString(tc, top - 23, "FICHA EPIDEMIOLÓGICA DE VIGILANCIA DE SARAMPIÓN RUBÉOLA")
        self._sf(F_TITLE_SM)
        c.drawCentredString(tc, top - 33, "Dirección de Epidemiología y Gestión del Riesgo")
        self._sf(("Helvetica-Oblique", 6))
        c.setFillColor(Color(0.3, 0.3, 0.3))
        c.drawCentredString(tc, top - 42, "Versión 2026")
        c.setFillColor(black)

        # Top-right info box
        bw, bh = 150, logo_sz
        bx = MARGIN + CONTENT_W - bw
        by = top - bh
        c.setStrokeColor(SECTION_BG)
        c.setLineWidth(1.0)
        c.rect(bx, by, bw, bh)
        c.setStrokeColor(black)
        c.setLineWidth(0.5)

        self._sf(F_HDR_BOX)
        c.setFillColor(SECTION_BG)
        c.drawString(bx + 4, by + bh - 10, "No. de caso:")
        c.setFillColor(black)
        c.drawString(bx + 50, by + bh - 10, _get(self.d, 'numero_caso', ''))

        self._sf(F_HDR_SM)
        c.drawString(bx + 4, by + bh - 20, f"Código de caso: {_get(self.d, 'codigo_caso', '')}")
        c.drawString(bx + 4, by + bh - 29, f"Área de salud: {_get(self.d, 'area_salud', '')}")

        # Folio box
        c.setStrokeColor(black)
        c.setLineWidth(0.4)
        c.rect(bx + bw - 40, by + bh - 12, 36, 10)
        self._sf(F_HDR_SM)
        c.drawString(bx + bw - 42, by + bh - 1, "Folio:")
        folio_val = _get(self.d, 'folio', '')
        if folio_val:
            self._sf(F_VALUE)
            c.drawString(bx + bw - 38, by + bh - 11, folio_val)

        self.y = top - logo_sz - 3

    def _p1_diagnostic_checkboxes(self):
        """Diagnostic type selection box below header."""
        h = 22
        y = self.y - h
        c = self.c

        # Background
        c.setFillColor(DIAG_BG)
        c.setStrokeColor(SECTION_BG)
        c.setLineWidth(0.8)
        c.rect(MARGIN, y, CONTENT_W, h, fill=1)
        c.setFillColor(black)
        c.setStrokeColor(black)

        self._sf(F_BOLD6)
        c.setFillColor(SECTION_BG)
        c.drawString(MARGIN + 3, y + h - 8, "Diagnóstico presuntivo:")
        c.setFillColor(black)

        diag = _get(self.d, 'diagnostico_registrado', '').upper()
        is_sar  = 'B05' in diag or 'SARAMP' in diag
        is_rub  = 'B06' in diag or 'RUBEO' in diag
        is_den  = 'A90' in diag or 'A91' in diag or 'DENGUE' in diag
        is_arbo = 'ARBO' in diag
        is_feb  = 'FEBRIL' in diag or 'EXANT' in diag
        is_alt  = 'ALTAMENTE' in diag or 'SOSPECHOSO' in diag
        # Default: sarampión
        if not any([is_sar, is_rub, is_den, is_arbo, is_feb, is_alt]):
            is_sar = True

        cb_y = y + 4
        options = [
            (is_sar,  'Sarampión'),
            (is_rub,  'Rubéola'),
            (is_den,  'Dengue'),
            (is_arbo, 'Otra Arbovirosis'),
            (is_feb,  'Otra febril exantemática'),
            (is_alt,  'Caso altamente sospechoso'),
        ]
        # Distribute across full width
        step = CONTENT_W / len(options)
        for i, (checked, label) in enumerate(options):
            self._checkbox(MARGIN + 8 + i * step, cb_y, checked=checked, label=label)

        self.y -= h

    # -- SECTION 1: DATOS DE LA UNIDAD NOTIFICADORA --

    def _s1_unidad_notificadora(self):
        d = self.d
        self._section("1. DATOS DE LA UNIDAD NOTIFICADORA")

        # Row 1: Fecha notificacion | Area de Salud | Distrito | Servicio
        h = RH_DATE
        y = self.y - h
        x = MARGIN
        w1 = CONTENT_W * 0.22
        w2 = CONTENT_W * 0.28
        w3 = CONTENT_W * 0.22
        w4 = CONTENT_W * 0.28
        self._date_cell(x,          y, w1, h, 'Fecha notificación', _get(d, 'fecha_notificacion'))
        self._cell(x + w1,          y, w2, h, 'Área de Salud',      _get(d, 'area_salud'))
        self._cell(x + w1 + w2,     y, w3, h, 'Distrito',           _get(d, 'distrito'))
        self._cell(x + w1 + w2 + w3, y, w4, h, 'Servicio/Unidad',  _get(d, 'unidad_medica'))
        self.y -= h

        # Row 2: Fecha consulta | Fecha investigación domiciliaria | Investigador
        h = RH_DATE
        y = self.y - h
        w1 = CONTENT_W * 0.28
        w2 = CONTENT_W * 0.32
        w3 = CONTENT_W * 0.40
        self._date_cell(x,      y, w1, h, 'Fecha consulta',                 _get(d, 'fecha_consulta'))
        self._date_cell(x + w1, y, w2, h, 'Fecha investigación domiciliaria', _get(d, 'fecha_investigacion_domiciliaria'))
        self._cell(x + w1 + w2, y, w3, h, 'Investigador',                   _get(d, 'investigador'))
        self.y -= h

        # Row 3: Tipo de establecimiento checkboxes + Fuente de notificacion
        h = RH
        y = self.y - h
        w_tipo = CONTENT_W * 0.38
        w_fuente = CONTENT_W * 0.62

        # Tipo de establecimiento
        self._rect(x, y, w_tipo, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + 2, y + h - 7.5, 'Tipo de establecimiento')
        cb_y = y + 3
        tipo = _get(d, 'tipo_establecimiento', '').upper()
        cx = x + 3
        cx = self._checkbox(cx, cb_y, checked=('IGSS' in tipo or 'SEGURO' in tipo), label='Seguro Social')
        cx += 3
        self._checkbox(cx, cb_y, checked=('PRIVADO' in tipo or 'PARTICULAR' in tipo), label='Establecimiento Privado')

        # Fuente de notificacion
        self._rect(x + w_tipo, y, w_fuente, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + w_tipo + 2, y + h - 7.5, 'Fuente de notificación')
        fuente_not = _get(d, 'fuente_notificacion', '').upper()
        is_serv   = any(k in fuente_not for k in ('PUBLICA', 'PRIVADA', 'SERVICIO'))
        is_lab    = 'LABORATORIO' in fuente_not
        is_rumor  = 'RUMOR' in fuente_not or 'COMUNIDAD' in fuente_not
        is_visita = any(k in fuente_not for k in ('BUSQUEDA', 'ACTIVA', 'VISITA', 'DOMICIL'))
        is_otro   = 'OTRO' in fuente_not
        fx = x + w_tipo + 3
        for checked, label in [(is_serv, 'Servicio de salud'), (is_lab, 'Laboratorio'),
                                (is_rumor, 'Rumor/comunidad'), (is_visita, 'B.A. domiciliar'),
                                (is_otro, 'Otro')]:
            fx = self._checkbox(fx, cb_y, checked=checked, label=label)
            fx += 3
        self.y -= h

    # -- SECTION 2: INFORMACIÓN DEL PACIENTE --

    def _s2_informacion_paciente(self):
        d = self.d
        self._section("2. INFORMACIÓN DEL PACIENTE")
        sexo = _get(d, 'sexo', '').upper()

        # Nombres | Apellidos | Sexo F/M
        h = RH
        y = self.y - h
        x = MARGIN
        w_n = CONTENT_W * 0.32
        w_a = CONTENT_W * 0.32
        w_sx_lbl = CONTENT_W * 0.06
        w_f = CONTENT_W * 0.15
        w_m = CONTENT_W * 0.15
        self._cell(x, y, w_n, h, 'Nombres', _get(d, 'nombres'))
        self._cell(x + w_n, y, w_a, h, 'Apellidos', _get(d, 'apellidos'))
        self._cell_plain(x + w_n + w_a, y, w_sx_lbl, h, 'Sexo', font=F_BOLD6, center=True)
        bx = x + w_n + w_a + w_sx_lbl
        self._rect(bx, y, w_f, h)
        self._checkbox(bx + 4, y + (h - CB_SIZE) / 2, checked=(sexo == 'F'), label='F')
        bx2 = bx + w_f
        self._rect(bx2, y, w_m, h)
        self._checkbox(bx2 + 4, y + (h - CB_SIZE) / 2, checked=(sexo == 'M'), label='M')
        self.y -= h

        # Fecha nacimiento | Edad | DPI
        h = RH_DATE
        y = self.y - h
        w_fn = CONTENT_W * 0.30
        w_ae = CONTENT_W * 0.10
        w_dpi = CONTENT_W * 0.35
        w_tel = CONTENT_W * 0.25
        self._date_cell(x, y, w_fn, h, 'Fecha de Nacimiento', _get(d, 'fecha_nacimiento'))
        self._cell(x + w_fn, y, w_ae, h, 'Edad', _get(d, 'edad_anios'))
        self._cell(x + w_fn + w_ae, y, w_dpi, h, 'DPI (CUI)', _get(d, 'afiliacion'))
        self._cell(x + w_fn + w_ae + w_dpi, y, w_tel, h, 'Teléfono', _get(d, 'telefono_paciente'))
        self.y -= h

        # Nombre tutor | Parentesco | DPI tutor
        h = RH
        self._row([
            (0.45, 'Nombre del Tutor/Encargado', _get(d, 'nombre_encargado')),
            (0.20, 'Parentesco',                 _get(d, 'parentesco_tutor')),
            (0.35, 'DPI Tutor',                  _get(d, 'dpi_tutor')),
        ], h=h)

        # Pueblo | Migrante | Embarazada | Trimestre
        h = RH
        y = self.y - h
        w_pueblo  = CONTENT_W * 0.42
        w_mig     = CONTENT_W * 0.15
        w_emb     = CONTENT_W * 0.24
        w_tri     = CONTENT_W * 0.19
        pueblo_val = _get(d, 'pueblo_etnia', '').upper()
        emb = _get(d, 'esta_embarazada', '').upper()
        mig = _get(d, 'migrante', '').upper()
        tri = _get(d, 'trimestre', '')

        # Pueblo checkboxes
        self._rect(x, y, w_pueblo, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + 2, y + h - 7.5, 'Pueblo')
        cb_y = y + 3
        pueblos = [('Maya', 'MAYA'), ('Xinca', 'XINCA'), ('Garifuna', 'GARI'),
                   ('Ladino', 'LADINO'), ('Mestizo', 'MESTIZO'), ('Otro', 'OTRO')]
        px = x + 3
        for label, kw in pueblos:
            px = self._checkbox(px, cb_y, checked=(kw in pueblo_val), label=label)
            px += 2

        # Migrante
        self._rect(x + w_pueblo, y, w_mig, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + w_pueblo + 2, y + h - 7.5, 'Migrante')
        mx = x + w_pueblo + 3
        mx = self._checkbox(mx, cb_y, checked=(mig in ('SI', 'SÍ')), label='Sí')
        self._checkbox(mx + 1, cb_y, checked=(mig == 'NO'), label='No')

        # Embarazada
        self._rect(x + w_pueblo + w_mig, y, w_emb, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + w_pueblo + w_mig + 2, y + h - 7.5, 'Embarazada')
        ex = x + w_pueblo + w_mig + 3
        ex = self._checkbox(ex, cb_y, checked=(emb in ('SI', 'SÍ')), label='Sí')
        ex += 2
        ex = self._checkbox(ex, cb_y, checked=(emb == 'NO'), label='No')
        ex += 2
        self._checkbox(ex, cb_y, checked=(emb in ('NA', 'N/A')), label='N/A')

        # Trimestre
        self._cell(x + w_pueblo + w_mig + w_emb, y, w_tri, h, 'Trimestre', tri)
        self.y -= h

        # Ocupacion | Escolaridad | Telefono (separate row already done above)
        self._row([
            (0.40, 'Ocupación',   _get(d, 'ocupacion')),
            (0.35, 'Escolaridad', _get(d, 'escolaridad')),
        ])

        # Residencia subsection
        h_sub = 9
        y_sub = self.y - h_sub
        self.c.setFillColor(LIGHT_GRAY)
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.3)
        self.c.rect(MARGIN, y_sub, CONTENT_W, h_sub, fill=1)
        self.c.setFillColor(Color(0.2, 0.2, 0.2))
        self._sf(("Helvetica-Bold", 5.5))
        self.c.drawString(MARGIN + 3, y_sub + 1.5, 'Lugar de residencia:')
        self.c.setFillColor(black)
        self.y -= h_sub

        # País | Depto | Municipio | Poblado
        self._row([
            (0.20, 'País',         _get(d, 'pais_residencia', 'Guatemala')),
            (0.25, 'Departamento', _get(d, 'departamento_residencia')),
            (0.25, 'Municipio',    _get(d, 'municipio_residencia')),
            (0.30, 'Poblado',      _get(d, 'poblado')),
        ])

        self._row([(1.0, 'Dirección exacta', _get(d, 'direccion_exacta'))])

    # -- SECTION 3: ANTECEDENTES MÉDICOS Y DE VACUNACIÓN --

    def _s3_antecedentes_vacunacion(self):
        d = self.d
        self._section("3. ANTECEDENTES MÉDICOS Y DE VACUNACIÓN")
        vacunado = _get(d, 'vacunado', '').upper()
        fuente   = _get(d, 'fuente_info_vacuna', '').upper()

        # Vacunado SI/NO | Antecedentes médicos
        h = RH
        y = self.y - h
        x = MARGIN
        w_vac = CONTENT_W * 0.22
        w_ant = CONTENT_W * 0.78

        self._rect(x, y, w_vac, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + 2, y + h - 7.5, 'Vacunado (SR/SPR/SPRV)')
        cb_y = y + 3
        self._checkbox(x + 3,  cb_y, checked=(vacunado in ('SI', 'SÍ')), label='Sí')
        self._checkbox(x + 30, cb_y, checked=(vacunado == 'NO'), label='No')
        self._checkbox(x + 55, cb_y, checked=(vacunado in ('DESC', 'DESCONOCIDO', 'NK')), label='Desc')
        self._cell(x + w_vac, y, w_ant, h, 'Antecedentes médicos relevantes', _get(d, 'antecedentes_medicos'))
        self.y -= h

        # Vaccine table header: Vacuna | No. Dosis | Fecha | Fuente info | Sector
        h_hdr = 12
        y = self.y - h_hdr
        col_vac  = CONTENT_W * 0.16
        col_dos  = CONTENT_W * 0.12
        col_fecha = CONTENT_W * 0.26
        col_fuente = CONTENT_W * 0.30
        col_sector = CONTENT_W * 0.16
        cols_vac = [('Vacuna', col_vac), ('No. Dosis', col_dos), ('Fecha última dosis', col_fecha),
                    ('Fuente de información', col_fuente), ('Sector', col_sector)]
        hx = x
        for lbl, w in cols_vac:
            self._cell_plain(hx, y, w, h_hdr, lbl, font=F_BOLD6, bg=LIGHT_GRAY)
            hx += w
        self.y -= h_hdr

        # Vaccine rows
        h_vrow = RH_DATE
        vac_rows = [
            ('SPR',  'dosis_spr',  'fecha_spr'),
            ('SR',   'dosis_sr',   'fecha_sr'),
            ('SPRV', 'dosis_sprv', 'fecha_sprv'),
        ]
        for vac_label, dosis_key, fecha_key in vac_rows:
            y = self.y - h_vrow
            hx = x
            self._cell_plain(hx, y, col_vac, h_vrow, vac_label, font=F_VALUE)
            hx += col_vac
            self._cell(hx, y, col_dos, h_vrow, '', _get(d, dosis_key))
            hx += col_dos
            self._date_cell(hx, y, col_fecha, h_vrow, '', _get(d, fecha_key))
            hx += col_fecha

            # Fuente checkboxes
            self._rect(hx, y, col_fuente, h_vrow)
            cb_y = y + 3
            self._sf(F_SMALL)
            self.c.setFillColor(black)
            self.c.drawString(hx + 2, y + h_vrow - 5, 'Fuente:')
            fuente_v = _get(d, f'fuente_{vac_label.lower()}', fuente).upper()
            fx = hx + 3
            for lbl, kw in [('Carné', 'CARNE'), ('SIGSA', 'SIGSA'),
                             ('Cuad', 'CUAD'), ('Verbal', 'VERBAL')]:
                fx = self._checkbox(fx, cb_y, checked=(kw in fuente_v), label=lbl, size=6)
                fx += 2
            hx += col_fuente

            # Sector
            self._cell(hx, y, col_sector, h_vrow, 'Sector', _get(d, f'sector_{vac_label.lower()}'))
            self.y -= h_vrow

    # -- SECTION 4: DATOS CLÍNICOS --

    def _s4_datos_clinicos(self):
        d = self.d
        self._section("4. DATOS CLÍNICOS")

        h = RH_DATE
        y = self.y - h
        x = MARGIN
        w1, w2, w3, w4 = (CONTENT_W * f for f in (0.26, 0.26, 0.26, 0.22))
        self._date_cell(x,          y, w1, h, 'Fecha inicio síntomas',  _get(d, 'fecha_inicio_sintomas'))
        self._date_cell(x + w1,     y, w2, h, 'Fecha inicio erupción',  _get(d, 'fecha_inicio_erupcion'))
        self._date_cell(x+w1+w2,    y, w3, h, 'Fecha inicio fiebre',    _get(d, 'fecha_inicio_fiebre'))
        self._cell(x+w1+w2+w3,      y, w4, h, 'Semana epidemiológica',  _get(d, 'semana_epidemiologica'))
        self.y -= h

        # Signs table: header + si/no/desc per sign
        self._s4_signos_table()

        # Hospitalización
        self._s4_hospitalizacion()

        # Complicaciones
        self._s4_complicaciones()

        # Aislamiento/condicion egreso
        self._s4_aislamiento()

    def _s4_signos_table(self):
        d = self.d
        signs = [
            ('Fiebre',         'signo_fiebre'),
            ('Erupción',       'signo_erupcion'),
            ('Tos',            'signo_tos'),
            ('Coriza',         'signo_coriza'),
            ('Conjuntivitis',  'signo_conjuntivitis'),
            ('Adenopatías',    'signo_adenopatias'),
            ('Artralgia',      'signo_artralgia'),
            ('Linfadenopatía', 'signo_linfadenopatia'),
            ('Dolor cabeza',   'signo_cefalea'),
            ('T° fiebre (°C)', 'temperatura_celsius'),
        ]

        # Header row
        h_hdr = 11
        y = self.y - h_hdr
        x = MARGIN
        w_sign = CONTENT_W * 0.22
        w_col  = (CONTENT_W - w_sign) / 3
        self._cell_plain(x, y, w_sign, h_hdr, 'Signo / Síntoma', font=F_BOLD6, bg=LIGHT_GRAY)
        for lbl in ('Sí', 'No', 'Desconocido'):
            self._cell_plain(x + w_sign + ('Sí' == lbl and 0 or ('No' == lbl and w_col or 2 * w_col)),
                             y, w_col, h_hdr, lbl, font=F_BOLD6, bg=LIGHT_GRAY, center=True)
        # Redraw properly in loop
        self.c.setFillColor(LIGHT_GRAY)
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(x, y, w_sign, h_hdr, fill=1)
        for i, lbl in enumerate(['Sí', 'No', 'Desconocido']):
            self.c.rect(x + w_sign + i * w_col, y, w_col, h_hdr, fill=1)
        self.c.setFillColor(black)
        self._sf(F_BOLD6)
        self.c.drawString(x + 2, y + 3, 'Signo / Síntoma')
        for i, lbl in enumerate(['Sí', 'No', 'Desconocido']):
            self.c.drawCentredString(x + w_sign + i * w_col + w_col / 2, y + 3, lbl)
        self.y -= h_hdr

        # Sign rows — two columns layout
        half = len(signs) // 2 + (len(signs) % 2)
        left_signs  = signs[:half]
        right_signs = signs[half:]
        h_row = 12

        # Column widths for 2-column layout
        col_w = CONTENT_W / 2
        sub_sign = col_w * 0.44
        sub_col  = (col_w - sub_sign) / 3

        total_rows = half
        block_h = total_rows * h_row
        y_start = self.y

        for i in range(total_rows):
            y = y_start - (i + 1) * h_row
            for col_idx, sign_list in enumerate(([left_signs, right_signs])):
                if i >= len(sign_list):
                    continue
                sign_label, sign_key = sign_list[i]
                val = _get(d, sign_key, '').upper()
                cx = MARGIN + col_idx * col_w

                # Special case for temperature — show value text
                if sign_key == 'temperatura_celsius':
                    self._rect(cx, y, sub_sign, h_row)
                    self._sf(F_FACTOR)
                    self.c.setFillColor(black)
                    self.c.drawString(cx + 2, y + 3, sign_label)
                    self._cell(cx + sub_sign, y, sub_sign * 2, h_row, '', val)
                    # Fill remaining cols
                    remaining = col_w - sub_sign - sub_sign * 2
                    if remaining > 0:
                        self._rect(cx + sub_sign + sub_sign * 2, y, remaining, h_row)
                    continue

                is_si   = val in ('SI', 'SÍ', '1', 'TRUE', 'S', 'X')
                is_no   = val == 'NO'
                is_desc = val in ('DESCONOCIDO', 'DESC', 'NK', '?', 'D', 'U')

                self._rect(cx, y, sub_sign, h_row)
                self._sf(F_FACTOR)
                self.c.setFillColor(black)
                self.c.drawString(cx + 2, y + 3, _trunc(sign_label, sub_sign - 4, 2.8))
                cb_y = y + (h_row - TRI_CB) / 2
                for j, checked in enumerate([is_si, is_no, is_desc]):
                    self._rect(cx + sub_sign + j * sub_col, y, sub_col, h_row)
                    self._checkbox(cx + sub_sign + j * sub_col + (sub_col - TRI_CB) / 2,
                                   cb_y, checked=checked, size=TRI_CB)

        self.y = y_start - block_h

    def _s4_hospitalizacion(self):
        d = self.d
        hosp = _get(d, 'hospitalizado', '').upper()

        h = RH
        y = self.y - h
        x = MARGIN
        w1 = CONTENT_W * 0.24
        w2 = CONTENT_W * 0.46
        w3 = CONTENT_W * 0.30

        # Hospitalizado
        self._rect(x, y, w1, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + 2, y + h - 7.5, 'Hospitalizado')
        cb_y = y + 3
        self._checkbox(x + 3,  cb_y, checked=(hosp in ('SI', 'SÍ')), label='Sí')
        self._checkbox(x + 30, cb_y, checked=(hosp == 'NO'), label='No')

        self._cell(x + w1, y, w2, h, 'Nombre del Hospital / Servicio', _get(d, 'hosp_nombre'))

        # Fecha hospitalización
        self._date_cell(x + w1 + w2, y, w3, h, 'Fecha hospitalización', _get(d, 'hosp_fecha'))
        self.y -= h

    def _s4_complicaciones(self):
        d = self.d
        h = RH
        y = self.y - h
        x = MARGIN
        comp = _get(d, 'complicaciones', '').upper()
        w1 = CONTENT_W * 0.26
        w2 = CONTENT_W * 0.74

        self._rect(x, y, w1, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + 2, y + h - 7.5, 'Complicaciones')
        cb_y = y + 3
        self._checkbox(x + 3,  cb_y, checked=(comp in ('SI', 'SÍ')), label='Sí')
        self._checkbox(x + 27, cb_y, checked=(comp == 'NO'), label='No')

        self._cell(x + w1, y, w2, h, 'Descripción complicaciones', _get(d, 'descripcion_complicaciones'))
        self.y -= h

    def _s4_aislamiento(self):
        d = self.d
        h = RH
        y = self.y - h
        x = MARGIN
        aisla = _get(d, 'aislamiento', '').upper()
        w1 = CONTENT_W * 0.26
        w2 = CONTENT_W * 0.40
        w3 = CONTENT_W * 0.34

        self._rect(x, y, w1, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + 2, y + h - 7.5, 'Aislamiento domiciliar')
        cb_y = y + 3
        self._checkbox(x + 3,  cb_y, checked=(aisla in ('SI', 'SÍ')), label='Sí')
        self._checkbox(x + 27, cb_y, checked=(aisla == 'NO'), label='No')

        self._cell(x + w1, y, w2, h, 'Condición de egreso', _get(d, 'condicion_egreso'))
        self._date_cell(x + w1 + w2, y, w3, h, 'Fecha defunción', _get(d, 'fecha_defuncion'))
        self.y -= h

    # -----------------------------------------------------------------------
    # PAGE 2
    # -----------------------------------------------------------------------

    def draw_page2(self):
        self.y = PAGE_H - MARGIN
        self._s5_factores_riesgo()
        self._s6_acciones_respuesta()
        self._s7_laboratorio()
        self._s8_clasificacion()

    # -- SECTION 5: FACTORES DE RIESGO --

    def _s5_factores_riesgo(self):
        d = self.d
        self._section("5. FACTORES DE RIESGO")

        wf = CONTENT_W * 0.68
        ws = CONTENT_W * 0.08
        wn = CONTENT_W * 0.08
        wd = CONTENT_W * 0.16  # Desconocido col
        x  = MARGIN

        # Column header
        h = 12
        y = self.y - h
        for col_x, w, label in [
            (x,          wf, 'Factor'),
            (x+wf,       ws, 'Sí'),
            (x+wf+ws,    wn, 'No'),
            (x+wf+ws+wn, wd, 'Desconocido'),
        ]:
            self._cell_plain(col_x, y, w, h, label, font=F_BOLD6, bg=LIGHT_GRAY, center=(label != 'Factor'))
        self.y -= h

        factores = [
            ("Caso confirmado en comunidad en últimos 3 meses",          _get(d, 'caso_confirmado_comunidad_3m', '')),
            ("Contacto con caso sospechoso 7-23 días previos a erupción", _get(d, 'contacto_sospechoso_7_23', '')),
            ("Contacto con embarazada en periodo infeccioso",             _get(d, 'contacto_embarazada', '')),
        ]

        h = 14
        for texto, val in factores:
            y = self.y - h
            v = val.upper()
            is_si   = v in ('SI', 'SÍ', '1')
            is_no   = v == 'NO'
            is_desc = v in ('DESCONOCIDO', 'DESC', 'NK', '?')
            self._rect(x,          y, wf, h)
            self._rect(x+wf,       y, ws, h)
            self._rect(x+wf+ws,    y, wn, h)
            self._rect(x+wf+ws+wn, y, wd, h)
            self._sf(F_FACTOR)
            self.c.setFillColor(black)
            self.c.drawString(x + 2, y + (h - 5) / 2, _trunc(texto, wf - 4, 2.7))
            cb_y = y + (h - CB_SIZE) / 2
            self._checkbox(x + wf + (ws - CB_SIZE) / 2,        cb_y, checked=is_si)
            self._checkbox(x + wf + ws + (wn - CB_SIZE) / 2,   cb_y, checked=is_no)
            self._checkbox(x + wf + ws + wn + (wd - CB_SIZE) / 2, cb_y, checked=is_desc)
            self.y -= h

        # Viajó row with date range
        h = RH_DATE
        y = self.y - h
        vx = CONTENT_W * 0.40
        vy = _get(d, 'viajo_previo', '').upper()
        self._rect(x, y, vx, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + 2, y + h - 7.5, 'Viajó 7-23 días previos al inicio de la erupción')
        cb_y = y + 3
        self._checkbox(x + 3,  cb_y, checked=(vy in ('SI', 'SÍ')), label='Sí')
        self._checkbox(x + 27, cb_y, checked=(vy == 'NO'), label='No')
        w_remaining = CONTENT_W - vx
        w_half = w_remaining / 2
        self._date_cell(x + vx,          y, w_half, h, 'Fecha inicio viaje', _get(d, 'fecha_inicio_viaje'))
        self._date_cell(x + vx + w_half, y, w_half, h, 'Fecha fin viaje',    _get(d, 'fecha_fin_viaje'))
        self.y -= h

        # Familiar viajó | lugar destino
        h = RH
        y = self.y - h
        fam_v = _get(d, 'familiar_viajo', '').upper()
        w1 = CONTENT_W * 0.26
        w2 = CONTENT_W * 0.44
        w3 = CONTENT_W * 0.30
        self._rect(x, y, w1, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + 2, y + h - 7.5, 'Familiar/contacto cercano viajó')
        cb_y = y + 3
        self._checkbox(x + 3,  cb_y, checked=(fam_v in ('SI', 'SÍ')), label='Sí')
        self._checkbox(x + 27, cb_y, checked=(fam_v == 'NO'), label='No')
        self._cell(x + w1,      y, w2, h, 'País/lugar destino del viaje',       _get(d, 'lugar_viaje'))
        self._cell(x + w1 + w2, y, w3, h, 'Fuente posible de contagio',         _get(d, 'fuente_contagio'))
        self.y -= h

    # -- SECTION 6: ACCIONES DE RESPUESTA --

    def _s6_acciones_respuesta(self):
        d = self.d
        self._section("6. ACCIONES DE RESPUESTA")

        acciones = [
            ('BAI (Búsqueda activa institucional)',   'accion_bai',       'fecha_bai'),
            ('BAC (Búsqueda activa comunitaria)',      'accion_bac',       'fecha_bac'),
            ('Vacunación bloqueo',                    'accion_vacunacion', 'fecha_vacunacion'),
            ('Monitoreo rápido de cobertura',         'accion_monitoreo',  'fecha_monitoreo'),
            ('Barrido vacunal',                       'accion_barrido',    'fecha_barrido'),
            ('Vitamina A',                            'accion_vitamina_a', 'fecha_vitamina_a'),
        ]

        h_hdr = 11
        y = self.y - h_hdr
        w_accion = CONTENT_W * 0.40
        w_si     = CONTENT_W * 0.08
        w_no     = CONTENT_W * 0.08
        w_fecha  = CONTENT_W * 0.44
        for col_x, w, label in [
            (MARGIN,                  w_accion, 'Acción'),
            (MARGIN + w_accion,       w_si,     'Sí'),
            (MARGIN + w_accion + w_si, w_no,    'No'),
            (MARGIN + w_accion + w_si + w_no, w_fecha, 'Fecha de realización'),
        ]:
            self._cell_plain(col_x, y, w, h_hdr, label, font=F_BOLD6, bg=LIGHT_GRAY,
                             center=(label != 'Acción'))
        self.y -= h_hdr

        h_row = RH_DATE
        for label, key_accion, key_fecha in acciones:
            y = self.y - h_row
            val = _get(d, key_accion, '').upper()
            is_si = val in ('SI', 'SÍ', '1')
            is_no = val == 'NO'
            self._rect(MARGIN, y, w_accion, h_row)
            self._sf(F_FACTOR)
            self.c.setFillColor(black)
            self.c.drawString(MARGIN + 2, y + (h_row - 5) / 2, label)
            cb_y = y + (h_row - CB_SIZE) / 2
            self._rect(MARGIN + w_accion, y, w_si, h_row)
            self._rect(MARGIN + w_accion + w_si, y, w_no, h_row)
            self._checkbox(MARGIN + w_accion + (w_si - CB_SIZE) / 2,        cb_y, checked=is_si)
            self._checkbox(MARGIN + w_accion + w_si + (w_no - CB_SIZE) / 2, cb_y, checked=is_no)
            self._date_cell(MARGIN + w_accion + w_si + w_no, y, w_fecha, h_row, '', _get(d, key_fecha))
            self.y -= h_row

    # -- SECTION 7: LABORATORIO --

    def _s7_laboratorio(self):
        d = self.d

        # Parse lab_muestras_json into flat fields for PDF rendering
        import json as _json
        lab_json_str = _get(d, 'lab_muestras_json')
        if lab_json_str:
            try:
                samples = _json.loads(lab_json_str)
                if isinstance(samples, list):
                    slot_prefix_map = {
                        'suero_1': 'suero1', 'suero_2': 'suero2',
                        'orina_1': 'orina1', 'hisopado_1': 'hisopado1',
                        'otro': 'otra',
                    }
                    for sample in samples:
                        slot = sample.get('slot', '')
                        prefix = slot_prefix_map.get(slot)
                        if not prefix:
                            continue
                        if sample.get('fecha_toma'):
                            d[f'muestra_{prefix}_fecha'] = sample['fecha_toma']
                        # Result codes: sarampion/rubeola igm/igg/avidez
                        for virus, vshort in [('sarampion', 'sar'), ('rubeola', 'rub')]:
                            for test in ['igm', 'igg']:
                                val = sample.get(f'{virus}_{test}', '')
                                if val:
                                    d[f'{prefix}_{vshort}_{test}'] = val
                            val_av = sample.get(f'{virus}_avidez', '')
                            if val_av:
                                d[f'{prefix}_{vshort}_av'] = val_av
                        if sample.get('secuenciacion_genotipo'):
                            d[f'{prefix}_secuencia'] = sample['secuenciacion_genotipo']
            except Exception:
                pass  # Fall through to empty lab matrix

        self._section("7. LABORATORIO")
        x = MARGIN

        # Tipo muestra taken + motivo no 3 muestras
        h = RH
        y = self.y - h
        recolecto = _get(d, 'recolecto_muestra', '').upper()
        w1 = CONTENT_W * 0.32
        w2 = CONTENT_W * 0.68
        self._rect(x, y, w1, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + 2, y + h - 7.5, 'Se recolectó muestra')
        cb_y = y + (h - CB_SIZE) / 2
        self._checkbox(x + 3,  cb_y, checked=(recolecto in ('SI', 'SÍ')), label='Sí')
        self._checkbox(x + 27, cb_y, checked=(recolecto == 'NO'), label='No')
        self._cell(x + w1, y, w2, h, 'Motivo por el que no se tomaron 3 muestras', _get(d, 'motivo_no_recoleccion'))
        self.y -= h

        # Matrix table:
        # Rows: 5 samples (Suero1, Suero2, Hisopado, Orina, Otra)
        # Cols: Tipo | Fecha recolección | Sarampión IgM | Sarampión IgG | Sarampión Avidez |
        #        Rubéola IgM | Rubéola IgG | Rubéola Avidez | Secuenciación
        matrix_cols = [
            ('Tipo de muestra',       CONTENT_W * 0.15),
            ('Fecha\nrecolección',    CONTENT_W * 0.13),
            ('Sarampión\nIgM',        CONTENT_W * 0.09),
            ('Sarampión\nIgG',        CONTENT_W * 0.09),
            ('Sarampión\nAvidez',     CONTENT_W * 0.09),
            ('Rubéola\nIgM',          CONTENT_W * 0.09),
            ('Rubéola\nIgG',          CONTENT_W * 0.09),
            ('Rubéola\nAvidez',       CONTENT_W * 0.09),
            ('Secuenciación\ngenotipo', CONTENT_W * 0.18),
        ]

        # Double header row: group headers
        h_grp = 10
        y = self.y - h_grp
        grp_cols = [
            ('',               CONTENT_W * 0.15),
            ('',               CONTENT_W * 0.13),
            ('Sarampión',      CONTENT_W * 0.27),  # IgM+IgG+Avidez
            ('Rubéola',        CONTENT_W * 0.27),  # IgM+IgG+Avidez
            ('',               CONTENT_W * 0.18),
        ]
        hx = x
        for grp_label, gw in grp_cols:
            if grp_label:
                self._cell_plain(hx, y, gw, h_grp, grp_label, font=F_BOLD6, bg=SECTION_BG,
                                 center=True)
                # White text
                self.c.setFillColor(white)
                self._sf(F_BOLD6)
                self.c.drawCentredString(hx + gw / 2, y + (h_grp - 6) / 2, grp_label)
                self.c.setFillColor(black)
            else:
                self.c.setStrokeColor(black)
                self.c.setLineWidth(0.4)
                self.c.rect(hx, y, gw, h_grp)
            hx += gw
        self.y -= h_grp

        # Sub-header row
        h_sub = 14
        y = self.y - h_sub
        hx = x
        for col_label, cw in matrix_cols:
            self._cell_plain(hx, y, cw, h_sub, col_label.replace('\n', ' '), font=F_LAB_HDR,
                             bg=LIGHT_GRAY, center=True)
            hx += cw
        # Re-draw with line breaks for two-line headers
        hx = x
        for col_label, cw in matrix_cols:
            self.c.setFillColor(LIGHT_GRAY)
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.4)
            self.c.rect(hx, y, cw, h_sub, fill=1)
            self.c.setFillColor(black)
            lines = col_label.split('\n')
            self._sf(F_LAB_HDR)
            if len(lines) == 2:
                self.c.drawCentredString(hx + cw / 2, y + 7, lines[0])
                self.c.drawCentredString(hx + cw / 2, y + 2, lines[1])
            else:
                self.c.drawCentredString(hx + cw / 2, y + (h_sub - 5) / 2, col_label)
            hx += cw
        self.y -= h_sub

        # Sample rows
        muestras = [
            ('Suero 1',   'muestra_suero1_fecha',    'suero1_sar_igm',  'suero1_sar_igg',  'suero1_sar_av',
             'suero1_rub_igm', 'suero1_rub_igg', 'suero1_rub_av', 'suero1_secuencia'),
            ('Suero 2',   'muestra_suero2_fecha',    'suero2_sar_igm',  'suero2_sar_igg',  'suero2_sar_av',
             'suero2_rub_igm', 'suero2_rub_igg', 'suero2_rub_av', 'suero2_secuencia'),
            ('Hisopado',  'muestra_hisopado_fecha',  'hisopado_sar_igm','hisopado_sar_igg','hisopado_sar_av',
             'hisopado_rub_igm','hisopado_rub_igg','hisopado_rub_av','hisopado_secuencia'),
            ('Orina',     'muestra_orina_fecha',     'orina_sar_igm',   'orina_sar_igg',   'orina_sar_av',
             'orina_rub_igm','orina_rub_igg','orina_rub_av','orina_secuencia'),
            ('Otra',      'muestra_otra_fecha',      'otra_sar_igm',    'otra_sar_igg',    'otra_sar_av',
             'otra_rub_igm','otra_rub_igg','otra_rub_av','otra_secuencia'),
        ]

        h_row = RH_DATE
        for row in muestras:
            tipo, fecha_key = row[0], row[1]
            result_keys = row[2:]
            y = self.y - h_row
            hx = x
            # Tipo
            self._cell_plain(hx, y, matrix_cols[0][1], h_row, tipo, font=F_LAB_VAL)
            hx += matrix_cols[0][1]
            # Fecha recolección
            self._date_cell(hx, y, matrix_cols[1][1], h_row, '', _get(d, fecha_key))
            hx += matrix_cols[1][1]
            # Result cells (IgM, IgG, Avidez for Sarampión + Rubéola + Secuenciación)
            for i, rk in enumerate(result_keys):
                cw = matrix_cols[i + 2][1]
                val = _get(d, rk, '')
                self._cell_plain(hx, y, cw, h_row, val, font=F_LAB_VAL, center=True)
                hx += cw
            self.y -= h_row

        # Secuenciación extra note row
        h = RH_SM
        y = self.y - h
        self._cell(x, y, CONTENT_W, h, 'Observaciones laboratorio / Secuenciación adicional',
                   _get(d, 'observaciones_laboratorio'))
        self.y -= h

    # -- SECTION 8: CLASIFICACIÓN FINAL --

    def _s8_clasificacion(self):
        d = self.d
        self._section("8. CLASIFICACIÓN FINAL")
        x = MARGIN
        clasif = _get(d, 'clasificacion_caso', '').upper()
        criterio = _get(d, 'criterio_clasificacion', '').upper()

        # Clasificación final checkboxes
        h = RH
        y = self.y - h
        w_lbl = CONTENT_W * 0.22
        w_rest = CONTENT_W * 0.78
        self._cell_plain(x, y, w_lbl, h, 'Clasificación Final', font=F_BOLD6, bg=LIGHT_GRAY)
        self._rect(x + w_lbl, y, w_rest, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + w_lbl + 2, y + h - 7.5, 'Marque una opción:')
        cb_y = y + 3
        cx = x + w_lbl + 60
        for lbl, kw in [
            ('Confirmado laboratorio',     'CONFIRM'),
            ('Confirmado nexo epidemiol.', 'NEXO'),
            ('Descartado',                 'DESCART'),
            ('En estudio',                 'ESTUDIO'),
        ]:
            cx = self._checkbox(cx, cb_y, checked=(kw in clasif), label=lbl)
            cx += 6
        self.y -= h

        # Criterio confirmación / descarte
        h = RH
        y = self.y - h
        w1 = CONTENT_W * 0.50
        w2 = CONTENT_W * 0.50
        self._rect(x, y, w1, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + 2, y + h - 7.5, 'Criterio de confirmación / descarte')
        cb_y = y + 3
        cx2 = x + 3
        for lbl, kw in [('Clínico', 'CLÍNICO'), ('Lab', 'LAB'), ('Nexo', 'NEXO'),
                         ('Clín+Lab', 'CLIN+LAB')]:
            cx2 = self._checkbox(cx2, cb_y, checked=(kw in criterio), label=lbl)
            cx2 += 4
        self._cell(x + w1, y, w2, h, 'Fuente de infección', _get(d, 'fuente_infeccion'))
        self.y -= h

        # Caso analizado por | Condición final
        h = RH
        y = self.y - h
        condicion = _get(d, 'condicion_final', '').upper()
        w1 = CONTENT_W * 0.45
        w2 = CONTENT_W * 0.55
        self._cell(x, y, w1, h, 'Caso analizado por', _get(d, 'responsable_clasificacion'))
        self._rect(x + w1, y, w2, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + w1 + 2, y + h - 7.5, 'Condición final del paciente')
        cb_y = y + 3
        ex = x + w1 + 3
        for lbl, kw in [('Vivo', 'VIVO'), ('Fallecido', 'FALLEC'), ('Desconocido', 'DESC')]:
            ex = self._checkbox(ex, cb_y, checked=(kw in condicion), label=lbl)
            ex += 5
        self.y -= h

        # Fecha defunción | Causa muerte
        h = RH_DATE
        y = self.y - h
        w1 = CONTENT_W * 0.35
        w2 = CONTENT_W * 0.65
        self._date_cell(x, y, w1, h, 'Fecha de defunción', _get(d, 'fecha_defuncion'))
        self._cell(x + w1, y, w2, h, 'Causa de muerte', _get(d, 'causa_muerte'))
        self.y -= h

        # Observaciones (tall)
        h = RH_TALL
        y = self.y - h
        self._cell(x, y, CONTENT_W, h, 'Observaciones', _get(d, 'observaciones'))
        self.y -= h

        # Firma / Sello
        h = 28
        y = self.y - h
        if y > MARGIN:
            w_half = CONTENT_W / 2
            self._rect(x, y, w_half, h)
            self._rect(x + w_half, y, w_half, h)
            # Labels at bottom of signature boxes
            self._sf(F_LABEL)
            self.c.setFillColor(black)
            self.c.drawCentredString(x + w_half / 2, y + 3, 'Firma y sello responsable de clasificación')
            self.c.drawCentredString(x + w_half + w_half / 2, y + 3, 'Firma y sello jefe de Epidemiología')
            self.y -= h


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generar_ficha_v2_pdf(data: dict) -> bytes:
    """Genera PDF de ficha epidemiológica formato MSPAS 2026."""
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=LETTER)
    c.setTitle("Ficha Epidemiológica Sarampión/Rubéola — MSPAS 2026")
    c.setAuthor("IGSS Epidemiología")
    c.setSubject("Versión 2026")
    builder = FichaV2Builder(c, data)
    builder.draw_page1()
    c.showPage()
    builder.draw_page2()
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


def generar_fichas_v2_bulk(records: list, merge: bool = True) -> bytes:
    """Genera múltiples fichas v2 (merged PDF o ZIP según merge flag)."""
    if not records:
        raise ValueError("No se proporcionaron registros")
    if merge:
        buf = io.BytesIO()
        c = Canvas(buf, pagesize=LETTER)
        c.setTitle("Fichas Epidemiológicas Sarampión/Rubéola — MSPAS 2026")
        c.setAuthor("IGSS Epidemiología")
        for data in records:
            builder = FichaV2Builder(c, data)
            builder.draw_page1()
            c.showPage()
            builder.draw_page2()
            c.showPage()
        c.save()
        buf.seek(0)
        return buf.read()
    else:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, data in enumerate(records):
                pdf_bytes = generar_ficha_v2_pdf(data)
                nombre   = _get(data, 'nombres', 'caso')
                apellido = _get(data, 'apellidos', '')
                filename = f"{i + 1:03d}_{nombre}_{apellido}.pdf".replace(' ', '_')
                zf.writestr(filename, pdf_bytes)
        zip_buf.seek(0)
        return zip_buf.read()


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

def _test():
    sample = {
        'diagnostico_registrado': 'B05 - Sarampión',
        'numero_caso': '2026-GT-0042',
        'codigo_caso': 'GT-SAR-2026-042',
        'area_salud': 'Guatemala Metropolitana',
        'folio': '0042',
        # Sección 1
        'fecha_notificacion': '2026-03-15',
        'fecha_consulta': '2026-03-14',
        'fecha_investigacion_domiciliaria': '2026-03-16',
        'investigador': 'Dra. Ana Pérez',
        'distrito': 'Distrito 01',
        'unidad_medica': 'HGE Zona 9',
        'tipo_establecimiento': 'IGSS Seguro Social',
        'fuente_notificacion': 'Servicio de salud',
        # Sección 2
        'nombres': 'María Isabel',
        'apellidos': 'López García',
        'sexo': 'F',
        'fecha_nacimiento': '1990-05-20',
        'edad_anios': '35',
        'afiliacion': '1234567890101',
        'telefono_paciente': '5555-1234',
        'nombre_encargado': 'Pedro López Méndez',
        'parentesco_tutor': 'Padre',
        'dpi_tutor': '2345678901011',
        'pueblo_etnia': 'Ladino',
        'migrante': 'NO',
        'esta_embarazada': 'NO',
        'trimestre': '',
        'ocupacion': 'Ama de casa',
        'escolaridad': 'Primaria',
        'pais_residencia': 'Guatemala',
        'departamento_residencia': 'Guatemala',
        'municipio_residencia': 'Mixco',
        'poblado': 'Col. El Milagro Z6',
        'direccion_exacta': '4ta Av 12-34 Z1 Col Las Flores',
        # Sección 3
        'vacunado': 'SI',
        'antecedentes_medicos': 'Ninguno relevante',
        'dosis_spr': '2', 'fecha_spr': '2015-03-10', 'fuente_spr': 'CARNE',
        'dosis_sr':  '1', 'fecha_sr':  '2010-06-01', 'fuente_sr':  'SIGSA',
        'dosis_sprv': '',  'fecha_sprv': '',           'fuente_sprv': '',
        # Sección 4
        'fecha_inicio_sintomas': '2026-03-10',
        'fecha_inicio_erupcion': '2026-03-11',
        'fecha_inicio_fiebre':   '2026-03-10',
        'semana_epidemiologica': '11',
        'signo_fiebre': 'SI', 'signo_erupcion': 'SI', 'signo_tos': 'SI',
        'signo_coriza': 'NO', 'signo_conjuntivitis': 'SI', 'signo_adenopatias': 'NO',
        'signo_artralgia': 'NO', 'signo_linfadenopatia': 'DESCONOCIDO',
        'signo_cefalea': 'SI', 'temperatura_celsius': '38.5',
        'hospitalizado': 'SI', 'hosp_nombre': 'HGE Zona 9', 'hosp_fecha': '2026-03-13',
        'complicaciones': 'NO', 'descripcion_complicaciones': '',
        'aislamiento': 'SI', 'condicion_egreso': 'Mejorado', 'fecha_defuncion': '',
        # Sección 5
        'caso_confirmado_comunidad_3m': 'NO',
        'contacto_sospechoso_7_23': 'SI',
        'contacto_embarazada': 'NO',
        'viajo_previo': 'NO', 'fecha_inicio_viaje': '', 'fecha_fin_viaje': '',
        'familiar_viajo': 'NO', 'lugar_viaje': '', 'fuente_contagio': '',
        # Sección 6
        'accion_bai': 'SI', 'fecha_bai': '2026-03-17',
        'accion_bac': 'SI', 'fecha_bac': '2026-03-18',
        'accion_vacunacion': 'SI', 'fecha_vacunacion': '2026-03-19',
        'accion_monitoreo': 'NO', 'fecha_monitoreo': '',
        'accion_barrido': 'NO', 'fecha_barrido': '',
        'accion_vitamina_a': 'SI', 'fecha_vitamina_a': '2026-03-13',
        # Sección 7
        'recolecto_muestra': 'SI',
        'motivo_no_recoleccion': '',
        'muestra_suero1_fecha': '2026-03-13', 'suero1_sar_igm': 'POSITIVO',
        'suero1_sar_igg': 'POSITIVO', 'suero1_sar_av': 'BAJA',
        'suero1_rub_igm': 'NEGATIVO', 'suero1_rub_igg': 'POSITIVO', 'suero1_rub_av': '',
        'suero1_secuencia': 'D8',
        'muestra_suero2_fecha': '', 'muestra_hisopado_fecha': '2026-03-13',
        'muestra_orina_fecha': '', 'muestra_otra_fecha': '',
        'observaciones_laboratorio': 'PCR positivo genotipo D8. Confirmado por LNS.',
        # Sección 8
        'clasificacion_caso': 'CONFIRMADO LABORATORIO',
        'criterio_clasificacion': 'LAB',
        'fuente_infeccion': 'Caso importado',
        'responsable_clasificacion': 'Dra. Ana Patricia Martínez',
        'condicion_final': 'VIVO',
        'causa_muerte': '',
        'observaciones': 'Caso confirmado. PCR positivo genotipo D8. '
                         'Contactos bajo vigilancia 21 días.',
    }

    out_path = '/tmp/test_ficha_v2.pdf'
    pdf_bytes = generar_ficha_v2_pdf(sample)
    with open(out_path, 'wb') as f:
        f.write(pdf_bytes)
    print(f"PDF generado: {out_path} ({len(pdf_bytes):,} bytes)")


if __name__ == '__main__':
    _test()
