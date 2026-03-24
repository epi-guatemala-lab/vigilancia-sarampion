"""
PDF Generator for MSPAS Sarampion/Rubeola Epidemiological Form.

Generates a pixel-accurate replica of the official MSPAS ficha epidemiologica
using reportlab. Two pages, letter size, table-based layout.

Public API:
    generar_ficha_pdf(data: dict) -> bytes
    generar_fichas_bulk(records: list[dict], merge: bool = True) -> bytes
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
PAGE_W, PAGE_H = LETTER  # 612 x 792 pt
MARGIN = 22
CONTENT_W = PAGE_W - 2 * MARGIN  # ~562 pt

SECTION_BG = Color(0.20, 0.20, 0.20, 1)   # darker for contrast (MSPAS style)
LIGHT_GRAY = Color(0.92, 0.92, 0.92, 1)

# Heights
SECTION_H = 17       # section header bars (MSPAS style)
RH = 21              # standard field row (label + value, no dates)
RH_DATE = 27         # rows containing date boxes (need room for digits + label)
RH_TALL = 36         # observaciones

CB_SIZE = 8          # checkbox side
DATE_BOX = 9         # individual date digit box size

# Fonts
F_SECTION    = ("Helvetica-Bold", 9.5)
F_LABEL      = ("Helvetica-Bold", 6)
F_VALUE      = ("Helvetica", 7.5)
F_BOLD6      = ("Helvetica-Bold", 6)
F_SMALL      = ("Helvetica", 3.5)
F_TITLE_LG   = ("Helvetica-Bold", 9)
F_TITLE_MD   = ("Helvetica-Bold", 7.5)
F_TITLE_SM   = ("Helvetica-Bold", 7)
F_ITALIC     = ("Helvetica-Oblique", 5)
F_CHECK      = ("Helvetica-Bold", 11)
F_DATE_DIGIT = ("Helvetica", 6.5)
F_CB_LABEL   = ("Helvetica", 5.5)
F_FACTOR     = ("Helvetica", 5.5)
F_CONTACT    = ("Helvetica", 5.5)
F_HDR_BOX    = ("Helvetica-Bold", 5.5)
F_HDR_SM     = ("Helvetica", 4.5)

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
    if not val:
        return ('', '', '')
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S', '%d-%m-%Y'):
        try:
            dt = datetime.strptime(val.strip()[:10], fmt)
            return (f"{dt.day:02d}", f"{dt.month:02d}", f"{dt.year:04d}")
        except (ValueError, TypeError):
            continue
    return ('', '', '')

def _trunc(text: str, w: float, cw: float = 3.5) -> str:
    mx = max(3, int(w / cw))
    if len(text) > mx:
        return text[:mx - 1] + '\u2026'
    return text

# ---------------------------------------------------------------------------
# FichaBuilder
# ---------------------------------------------------------------------------

class FichaBuilder:

    def __init__(self, c: Canvas, data: dict):
        self.c = c
        self.d = data
        self.y = PAGE_H - MARGIN

    # -- primitives --

    def _sf(self, f):
        self.c.setFont(f[0], f[1])

    def _cell(self, x, y, w, h, label='', value=''):
        """Bordered cell: label top-left (6pt bold), value below (7.5pt)."""
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(x, y, w, h)
        if label:
            self._sf(F_LABEL)  # Helvetica-Bold 6pt — bold labels per MSPAS
            self.c.setFillColor(black)
            self.c.drawString(x + 2.5, y + h - 8, _trunc(label, w - 5, 3.2))
        if value:
            self._sf(F_VALUE)
            self.c.setFillColor(black)
            self.c.drawString(x + 2.5, y + h - 17, _trunc(value, w - 5))

    def _cell_plain(self, x, y, w, h, text='', font=F_VALUE, center=False):
        """Bordered cell with single text, no label/value split."""
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(x, y, w, h)
        if text:
            self._sf(font)
            self.c.setFillColor(black)
            ty = y + (h - font[1]) / 2
            if center:
                self.c.drawCentredString(x + w / 2, ty, _trunc(text, w - 4, 3.0))
            else:
                self.c.drawString(x + 2, ty, _trunc(text, w - 4, 3.0))

    def _section(self, title):
        h = SECTION_H
        y = self.y - h
        # Gradient simulation: thin lighter strip at top of section bar
        self.c.setFillColor(Color(0.30, 0.30, 0.30, 1))
        self.c.rect(MARGIN, y + h * 0.6, CONTENT_W, h * 0.4, fill=1, stroke=0)
        self.c.setFillColor(SECTION_BG)
        self.c.rect(MARGIN, y, CONTENT_W, h * 0.6, fill=1, stroke=0)
        # Full border around entire section header
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(MARGIN, y, CONTENT_W, h, fill=0, stroke=1)
        # Title text centered with padding
        self.c.setFillColor(white)
        self._sf(F_SECTION)
        self.c.drawCentredString(MARGIN + CONTENT_W / 2, y + (h - F_SECTION[1]) / 2 + 0.5, title)
        self.c.setFillColor(black)
        self.y -= h

    def _subtitle(self, text):
        self.y -= 11
        self._sf(F_BOLD6)
        self.c.setFillColor(black)
        self.c.drawString(MARGIN + 2, self.y + 2, text)

    def _checkbox(self, x, y, checked=False, label=''):
        """Checkbox at (x,y) bottom-left. Returns x after label."""
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.6)
        self.c.rect(x, y, CB_SIZE, CB_SIZE)
        if checked:
            self._sf(F_CHECK)
            self.c.setFillColor(black)
            # Bold centered X — offset fine-tuned for F_CHECK=11pt
            self.c.drawCentredString(x + CB_SIZE / 2, y + (CB_SIZE - F_CHECK[1]) / 2 - 0.3, 'X')
        nx = x + CB_SIZE + 2
        if label:
            self._sf(F_CB_LABEL)
            self.c.setFillColor(black)
            self.c.drawString(nx, y + 1, label)
            nx += len(label) * 3.3 + 3
        return nx

    def _date_cell(self, x, y, w, h, label='', date_str=''):
        """Cell with label at top-left, date digit boxes at bottom-left.
        Uses compact layout: label on top line, Dia/Mes/Ano labels ABOVE boxes.
        """
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(x, y, w, h)

        if label:
            self._sf(F_LABEL)  # Helvetica-Bold 6pt
            self.c.setFillColor(black)
            self.c.drawString(x + 2.5, y + h - 8, _trunc(label, w - 5, 3.2))

        dd, mm, yyyy = _parse_date(date_str)
        bs = DATE_BOX
        bx = x + 3
        by = y + 2

        # Dia — label ABOVE boxes
        self._sf(F_SMALL)
        self.c.setFillColor(black)
        self.c.drawCentredString(bx + bs, by + bs + 1.5, 'D\u00eda')
        for i, ch in enumerate(dd.ljust(2)):
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.4)
            self.c.rect(bx + i * bs, by, bs, bs)
            if ch.strip():
                self._sf(F_DATE_DIGIT)
                self.c.setFillColor(black)
                self.c.drawCentredString(bx + i * bs + bs / 2, by + 1.5, ch)
        bx += 2 * bs
        # Separator "/"
        self._sf(F_DATE_DIGIT)
        self.c.setFillColor(black)
        self.c.drawCentredString(bx + 2.5, by + 1.5, '/')
        bx += 5

        # Mes — label ABOVE boxes
        self._sf(F_SMALL)
        self.c.setFillColor(black)
        self.c.drawCentredString(bx + bs, by + bs + 1.5, 'Mes')
        for i, ch in enumerate(mm.ljust(2)):
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.4)
            self.c.rect(bx + i * bs, by, bs, bs)
            if ch.strip():
                self._sf(F_DATE_DIGIT)
                self.c.setFillColor(black)
                self.c.drawCentredString(bx + i * bs + bs / 2, by + 1.5, ch)
        bx += 2 * bs
        # Separator "/"
        self._sf(F_DATE_DIGIT)
        self.c.setFillColor(black)
        self.c.drawCentredString(bx + 2.5, by + 1.5, '/')
        bx += 5

        # Ano — label ABOVE boxes
        self._sf(F_SMALL)
        self.c.setFillColor(black)
        self.c.drawCentredString(bx + 2 * bs, by + bs + 1.5, 'A\u00f1o')
        for i, ch in enumerate(yyyy.ljust(4)):
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.4)
            self.c.rect(bx + i * bs, by, bs, bs)
            if ch.strip():
                self._sf(F_DATE_DIGIT)
                self.c.setFillColor(black)
                self.c.drawCentredString(bx + i * bs + bs / 2, by + 1.5, ch)

    def _row(self, fields, h=RH):
        """Row of cells. fields = [(frac, label, value), ...]"""
        x = MARGIN
        y = self.y - h
        for wf, lbl, val in fields:
            w = CONTENT_W * wf
            self._cell(x, y, w, h, lbl, val)
            x += w
        self.y -= h

    # -----------------------------------------------------------------------
    # PAGE 1
    # -----------------------------------------------------------------------

    def draw_page1(self):
        self.y = PAGE_H - MARGIN
        self._p1_header()
        self._p1_definition()
        self._p1_datos_generales()
        self._p1_datos_paciente()
        self._p1_antecedente_vacunal()
        self._p1_informacion_clinica()
        self._p1_factores_riesgo()

    def _p1_header(self):
        c = self.c
        d = self.d
        top = self.y

        # Logo / Escudo de Guatemala top-left
        # Try: escudo_guatemala.png, then mspas_logo.png, then placeholder
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        logo_path = None
        for fname in ('escudo_guatemala.png', 'mspas_logo.png'):
            cand = os.path.join(assets_dir, fname)
            if os.path.isfile(cand):
                logo_path = cand
                break

        logo_size = 45  # 45x45pt box (prominent like MSPAS original)
        lx = MARGIN
        ly = top - logo_size
        if logo_path:
            try:
                c.drawImage(logo_path, lx, ly, width=logo_size, height=logo_size,
                            preserveAspectRatio=True, mask='auto')
            except Exception:
                logo_path = None  # fall through to placeholder
        if not logo_path:
            # Clean bordered placeholder box
            c.setStrokeColor(black)
            c.setLineWidth(0.8)
            c.rect(lx, ly, logo_size, logo_size)
            # Inner border for double-line effect
            c.setLineWidth(0.3)
            c.rect(lx + 2, ly + 2, logo_size - 4, logo_size - 4)
            self._sf(("Helvetica-Bold", 7))
            c.setFillColor(Color(0.25, 0.25, 0.25))
            c.drawCentredString(lx + logo_size / 2, ly + logo_size / 2 + 4, 'MSPAS')
            self._sf(("Helvetica", 5))
            c.drawCentredString(lx + logo_size / 2, ly + logo_size / 2 - 5, 'Guatemala')
            c.setFillColor(black)

        # Center titles — between logo (left) and disease box (right)
        title_left = MARGIN + logo_size + 8
        title_right = MARGIN + CONTENT_W - 165
        title_center = (title_left + title_right) / 2
        self._sf(F_TITLE_LG)
        c.setFillColor(black)
        c.drawCentredString(title_center, top - 14, "MINISTERIO DE SALUD P\u00daBLICA Y ASISTENCIA SOCIAL")
        self._sf(F_TITLE_MD)
        c.drawCentredString(title_center, top - 26, "DEPARTAMENTO DE EPIDEMIOLOG\u00cdA")
        self._sf(F_TITLE_SM)
        c.drawCentredString(title_center, top - 37, "FICHA EPIDEMIOL\u00d3GICA")

        # Disease selection box — top right
        bw = 160
        bh = logo_size  # match logo height
        bx = MARGIN + CONTENT_W - bw
        by = top - bh
        c.setStrokeColor(black)
        c.setLineWidth(0.6)
        c.rect(bx, by, bw, bh)

        self._sf(F_HDR_BOX)
        c.setFillColor(black)
        c.drawString(bx + 3, by + bh - 10, "FICHA EPIDEMIOL\u00d3GICA")
        self._sf(F_HDR_SM)
        c.drawString(bx + 3, by + bh - 19, "Caso sospechoso de:")
        self._sf(("Helvetica", 3.5))
        c.drawString(bx + 3, by + bh - 27, "Marque la enfermedad que va a notificar")

        diag = _get(d, 'diagnostico_registrado', '').upper()
        is_sar = 'B05' in diag or 'SARAMP' in diag
        is_rub = 'B06' in diag or 'RUBEO' in diag or 'RUBE' in diag
        if not is_sar and not is_rub:
            is_sar = True

        cb_row_y = by + 5
        self._checkbox(bx + 6, cb_row_y, checked=is_sar, label='Sarampi\u00f3n')
        self._checkbox(bx + 80, cb_row_y, checked=is_rub, label='Rub\u00e9ola')

        self.y = top - logo_size - 4

    def _p1_definition(self):
        c = self.c
        self._sf(F_ITALIC)
        c.setFillColor(black)
        c.drawString(MARGIN, self.y - 6,
            "Sospecha rub\u00e9ola en: Persona de cualquier edad en la que un trabajador de salud sospeche infecci\u00f3n por rub\u00e9ola.")
        c.drawString(MARGIN, self.y - 12,
            "Sospeche sarampi\u00f3n en: Persona de cualquier edad que presente fiebre, erupci\u00f3n y alguno de los siguientes: Tos, Coriza o Conjuntivitis.")
        self.y -= 16

    # -- DATOS GENERALES --

    def _p1_datos_generales(self):
        d = self.d
        self._section("DATOS GENERALES")

        self._row([(1.0, 'Unidad notificadora', _get(d, 'unidad_medica'))], h=RH)

        # Dates row
        h = RH_DATE
        y = self.y - h
        w = CONTENT_W * 0.5
        self._date_cell(MARGIN, y, w, h, 'Fecha de notificaci\u00f3n', _get(d, 'fecha_notificacion'))
        self._date_cell(MARGIN + w, y, w, h, 'Fecha de registro', _get(d, 'fecha_registro_diagnostico'))
        self.y -= h

        self._row([
            (0.40, 'Unidad M\u00e9dica', _get(d, 'unidad_medica')),
            (0.30, 'Municipio', _get(d, 'municipio_residencia')),
            (0.30, 'Departamento', _get(d, 'departamento_residencia')),
        ])
        self._row([
            (0.40, 'Responsable', _get(d, 'nom_responsable')),
            (0.30, 'Cargo', _get(d, 'cargo_responsable')),
            (0.30, 'Tel\u00e9fono', _get(d, 'telefono_responsable')),
        ])

    # -- DATOS PACIENTE --

    def _p1_datos_paciente(self):
        d = self.d
        self._section("DATOS PACIENTE")
        sexo = _get(d, 'sexo', '').upper()

        # Names + Sexo
        h = RH
        y = self.y - h
        x = MARGIN
        w_n = CONTENT_W * 0.33
        w_a = CONTENT_W * 0.33
        w_sx = CONTENT_W * 0.06
        w_f = CONTENT_W * 0.14
        w_m = CONTENT_W * 0.14

        self._cell(x, y, w_n, h, 'Nombres', _get(d, 'nombres'))
        self._cell(x + w_n, y, w_a, h, 'Apellidos', _get(d, 'apellidos'))
        self._cell_plain(x + w_n + w_a, y, w_sx, h, 'Sexo', font=F_BOLD6, center=True)
        # F
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        bx = x + w_n + w_a + w_sx
        self.c.rect(bx, y, w_f, h)
        cb_y = y + (h - CB_SIZE) / 2
        self._checkbox(bx + 4, cb_y, checked=(sexo == 'F'), label='F')
        # M
        bx2 = bx + w_f
        self.c.rect(bx2, y, w_m, h)
        self._checkbox(bx2 + 4, cb_y, checked=(sexo == 'M'), label='M')
        self.y -= h

        self._row([
            (0.35, 'CUI paciente', _get(d, 'afiliacion')),
            (0.35, 'Ocupaci\u00f3n', _get(d, 'ocupacion')),
            (0.30, 'Escolaridad', _get(d, 'escolaridad')),
        ])

        # Residencia label row (borderless, bold text only — matches MSPAS original)
        h = 12
        y = self.y - h
        self._sf(("Helvetica-Bold", 6.5))
        self.c.setFillColor(black)
        self.c.drawString(MARGIN + 2, y + 3, 'Residencia')
        # Subtle underline extending across content width
        self.c.setStrokeColor(Color(0.6, 0.6, 0.6, 1))
        self.c.setLineWidth(0.3)
        self.c.line(MARGIN, y, MARGIN + CONTENT_W, y)
        self.c.setStrokeColor(black)
        self.y -= h

        self._row([
            (0.35, 'Departamento', _get(d, 'departamento_residencia')),
            (0.35, 'Municipio', _get(d, 'municipio_residencia')),
            (0.30, 'Poblado', _get(d, 'poblado')),
        ])

        self._row([(1.0, 'Direcci\u00f3n exacta', _get(d, 'direccion_exacta'))])

        self._row([
            (0.50, 'Pueblo de pertinencia', _get(d, 'pueblo_etnia')),
            (0.50, 'Comunidad ling\u00fc\u00edstica', _get(d, 'comunidad_linguistica')),
        ])

        # Fecha Nacimiento + Anos/Meses/Dias
        h = RH_DATE
        y = self.y - h
        w_fn = CONTENT_W * 0.40
        w_r = CONTENT_W * 0.20
        self._date_cell(MARGIN, y, w_fn, h, 'Fecha de Nacimiento', _get(d, 'fecha_nacimiento'))
        self._cell(MARGIN + w_fn, y, w_r, h, 'A\u00f1os', _get(d, 'edad_anios'))
        self._cell(MARGIN + w_fn + w_r, y, w_r, h, 'Meses', _get(d, 'edad_meses'))
        self._cell(MARGIN + w_fn + 2 * w_r, y, w_r, h, 'D\u00edas', _get(d, 'edad_dias'))
        self.y -= h

        self._row([
            (0.75, 'Nombre de la Madre, Padre o Encargado', _get(d, 'nombre_encargado')),
            (0.25, 'Tel\u00e9fono', _get(d, 'telefono_encargado')),
        ])

    # -- ANTECEDENTE VACUNAL --

    def _p1_antecedente_vacunal(self):
        d = self.d
        self._section("ANTECEDENTE VACUNAL")
        vacunado = _get(d, 'vacunado', '').upper()
        fuente = _get(d, 'fuente_info_vacuna', '').upper()

        # Vacunado SI/NO | Fuente checkboxes
        h = RH
        y = self.y - h
        x = MARGIN
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(x, y, CONTENT_W, h)

        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + 2, y + h - 8, 'Vacunado (SR/SPR)')
        cb_y = y + 3
        self._checkbox(x + 3, cb_y, checked=(vacunado == 'SI'), label='SI')
        self._checkbox(x + 35, cb_y, checked=(vacunado == 'NO'), label='NO')

        div = x + CONTENT_W * 0.20
        self.c.line(div, y, div, y + h)
        self._sf(F_LABEL)
        self.c.drawString(div + 2, y + h - 8, 'Fuente de Informaci\u00f3n')
        fx = div + 3
        for lbl, kw in [('Carn\u00e9', 'CARNE'), ('SIGSA 5a', 'SIGSA'),
                         ('Cuadernillo', 'CUADERNILLO'), ('Verbal', 'VERBAL')]:
            fx = self._checkbox(fx, cb_y, checked=(kw in fuente), label=lbl)
            fx += 5
        self.y -= h

        # No. dosis | Fecha ultima dosis | Observaciones
        h = RH_DATE
        y = self.y - h
        w_d = CONTENT_W * 0.10
        w_f = CONTENT_W * 0.35
        w_o = CONTENT_W * 0.55
        self._cell(x, y, w_d, h, 'No. dosis', _get(d, 'numero_dosis_spr'))
        self._date_cell(x + w_d, y, w_f, h, 'Fecha \u00faltima dosis', _get(d, 'fecha_ultima_dosis'))
        self._cell(x + w_d + w_f, y, w_o, h, 'Observaciones', _get(d, 'observaciones_vacuna'))
        self.y -= h

    # -- INFORMACION CLINICA --

    def _p1_informacion_clinica(self):
        d = self.d
        self._section("INFORMACI\u00d3N CL\u00cdNICA")
        self._subtitle('Conocimiento de caso')

        x = MARGIN

        # Fecha inicio sintomas | space | Semana Epi
        h = RH_DATE
        y = self.y - h
        w1 = CONTENT_W * 0.40
        w2 = CONTENT_W * 0.25
        w3 = CONTENT_W * 0.35
        self._date_cell(x, y, w1, h, 'Fecha inicio s\u00edntomas', _get(d, 'fecha_inicio_sintomas'))
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(x + w1, y, w2, h)
        self._cell(x + w1 + w2, y, w3, h, 'Semana Epidemiol\u00f3gica', _get(d, 'semana_epidemiologica'))
        self.y -= h

        # Fecha Captacion | Fuente notificacion
        h = RH_DATE
        y = self.y - h
        w_fc = CONTENT_W * 0.35
        w_fn = CONTENT_W * 0.65
        self._date_cell(x, y, w_fc, h, 'Fecha de Captaci\u00f3n', _get(d, 'fecha_captacion'))
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(x + w_fc, y, w_fn, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + w_fc + 2, y + h - 8, 'Fuente de notificaci\u00f3n')

        fuente_not = _get(d, 'fuente_notificacion', '').upper()
        is_serv = any(k in fuente_not for k in ('PUBLICA', 'PRIVADA', 'SERVICIO', 'LABORATORIO'))
        is_rumor = 'COMUNIDAD' in fuente_not or 'RUMOR' in fuente_not
        is_visita = any(k in fuente_not for k in ('BUSQUEDA', 'ACTIVA', 'VISITA', 'DOMICILIAR'))
        cb_y = y + 3
        fx = x + w_fc + 3
        fx = self._checkbox(fx, cb_y, checked=is_serv, label='Servicio de salud')
        fx += 6
        fx = self._checkbox(fx, cb_y, checked=is_rumor, label='Rumor')
        fx += 6
        self._checkbox(fx, cb_y, checked=is_visita, label='Visita domiciliaria')
        self.y -= h

        # Fecha planificada | Embarazada
        h = RH_DATE
        y = self.y - h
        w_fp = CONTENT_W * 0.55
        w_emb = CONTENT_W * 0.45
        self._date_cell(x, y, w_fp, h,
                        'Fecha planificada inicio investigaci\u00f3n (visita domiciliar)',
                        _get(d, 'fecha_inicio_investigacion'))
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(x + w_fp, y, w_emb, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(x + w_fp + 2, y + h - 8, 'Paciente embarazada')
        emb = _get(d, 'esta_embarazada', '').upper()
        cb_y = y + 3
        ex = x + w_fp + 3
        ex = self._checkbox(ex, cb_y, checked=(emb == 'SI'), label='SI')
        ex += 3
        ex = self._checkbox(ex, cb_y, checked=(emb == 'NO'), label='NO')
        ex += 3
        self._checkbox(ex, cb_y, checked=(emb in ('NA', 'N/A')), label='NA')
        self.y -= h

        # -- Signos y sintomas --
        self._subtitle('Signos y s\u00edntomas (marque con una "X" los s\u00edntomas/signos que presenta)')

        signos = {
            'Tos': _get(d, 'signo_tos'),
            'Coriza (o catarro)': _get(d, 'signo_coriza'),
            'Adenopat\u00edas': _get(d, 'signo_adenopatias'),
            'Artralgia o artritis': _get(d, 'signo_artralgia'),
            'Conjuntivitis': _get(d, 'signo_conjuntivitis'),
            'Fiebre': _get(d, 'signo_fiebre'),
        }

        def _chk(v):
            return str(v).strip().upper() in ('SI', 'S', '1', 'TRUE', 'X')

        asint = _get(d, 'asintomatico', '').upper()

        row_h = 12
        total_h = row_h * 3
        y = self.y - total_h

        w_left = CONTENT_W * 0.28
        w_right = CONTENT_W * 0.32
        w_asint = CONTENT_W * 0.40

        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(MARGIN, y, w_left, total_h)
        self.c.rect(MARGIN + w_left, y, w_right, total_h)
        self.c.rect(MARGIN + w_left + w_right, y, w_asint, total_h)

        for i in range(1, 3):
            ly = y + i * row_h
            self.c.setLineWidth(0.3)
            self.c.line(MARGIN, ly, MARGIN + CONTENT_W, ly)

        left_s = ['Tos', 'Coriza (o catarro)', 'Adenopat\u00edas']
        right_s = ['Artralgia o artritis', 'Conjuntivitis', 'Fiebre']

        for i, s in enumerate(left_s):
            sy = y + total_h - (i + 1) * row_h + (row_h - CB_SIZE) / 2
            self._checkbox(MARGIN + 3, sy, checked=_chk(signos[s]), label=s)

        for i, s in enumerate(right_s):
            sy = y + total_h - (i + 1) * row_h + (row_h - CB_SIZE) / 2
            self._checkbox(MARGIN + w_left + 3, sy, checked=_chk(signos[s]), label=s)

        # Asintomatico in top-right area
        ax = MARGIN + w_left + w_right + 3
        ay = y + total_h - row_h + (row_h - CB_SIZE) / 2
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(ax, ay + 1, 'Asintom\u00e1tico')
        self._checkbox(ax + 35, ay, checked=(asint == 'SI'), label='SI')
        self._checkbox(ax + 60, ay, checked=(asint == 'NO'), label='No')

        self.y -= total_h

        # Motivo sospecha — derived from existing fields when motivo_sospecha is not stored
        h = 14
        y = self.y - h
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(MARGIN, y, CONTENT_W, h)
        motivo = _get(d, 'motivo_sospecha', '').upper()
        # Derive motivo from other fields if not explicitly stored
        is_hallazgo = 'HALLAZGO' in motivo or 'LABORATORIO' in motivo
        is_contacto = 'CONTACTO' in motivo
        if not motivo and asint == 'SI':
            # Check if lab results exist → hallazgo de laboratorio
            has_lab = any(_get(d, f) for f in (
                'resultado_igg_cualitativo', 'resultado_igm_cualitativo',
                'resultado_pcr_orina', 'resultado_pcr_hisopado',
            ))
            if has_lab:
                is_hallazgo = True
            # Check if contact with suspect → contacto
            if _get(d, 'contacto_sospechoso_7_23', '').upper() == 'SI':
                is_contacto = True
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(MARGIN + 2, y + h - 8, 'En paciente asintom\u00e1tico marque motivo de sospecha')
        cb_y = y + (h - CB_SIZE) / 2
        mx = MARGIN + CONTENT_W * 0.40
        self._checkbox(mx, cb_y, checked=is_hallazgo, label='Hallazgo de laboratorio')
        self._checkbox(mx + 105, cb_y, checked=is_contacto, label='Contacto')
        self.y -= h

        # Fecha erupcion | Fecha fiebre | T grados
        h = RH_DATE
        y = self.y - h
        w1 = CONTENT_W * 0.38
        w2 = CONTENT_W * 0.38
        w3 = CONTENT_W * 0.24
        self._date_cell(MARGIN, y, w1, h, 'Fecha de Inicio Erupci\u00f3n', _get(d, 'fecha_inicio_erupcion'))
        self._date_cell(MARGIN + w1, y, w2, h, 'Fecha inicio fiebre', _get(d, 'fecha_inicio_fiebre'))
        self._cell(MARGIN + w1 + w2, y, w3, h, 'T grados C', _get(d, 'temperatura_celsius'))
        self.y -= h

        # -- Hospitalizacion --
        self._subtitle('Hospitalizaci\u00f3n y defunci\u00f3n')

        hosp = _get(d, 'hospitalizado', '').upper()

        # Hospitalizacion SI/NO | Hospital
        h = RH
        y = self.y - h
        w1 = CONTENT_W * 0.26
        w2 = CONTENT_W * 0.74
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(MARGIN, y, w1, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(MARGIN + 2, y + h - 8, 'Hospitalizaci\u00f3n')
        cb_y = y + 3
        self._checkbox(MARGIN + 3, cb_y, checked=(hosp == 'SI'), label='SI')
        self._checkbox(MARGIN + 35, cb_y, checked=(hosp == 'NO'), label='NO')
        self._cell(MARGIN + w1, y, w2, h, 'Nombre del Hospital', _get(d, 'hosp_nombre'))
        self.y -= h

        # Fecha hospitalizacion | Registro
        h = RH_DATE
        y = self.y - h
        w1 = CONTENT_W * 0.40
        w2 = CONTENT_W * 0.60
        self._date_cell(MARGIN, y, w1, h, 'Fecha de Hospitalizaci\u00f3n', _get(d, 'hosp_fecha'))
        self._cell(MARGIN + w1, y, w2, h, 'N\u00famero de Registro M\u00e9dico', _get(d, 'no_registro_medico'))
        self.y -= h

        # Condicion Egreso | Fecha defuncion
        h = RH_DATE
        y = self.y - h
        egreso = _get(d, 'condicion_egreso', '').upper()
        w1 = CONTENT_W * 0.55
        w2 = CONTENT_W * 0.45

        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(MARGIN, y, w1, h)
        self._sf(F_LABEL)
        self.c.setFillColor(black)
        self.c.drawString(MARGIN + 2, y + h - 8, 'Condici\u00f3n de Egreso')
        cb_y = y + 3
        ex = MARGIN + 3
        for lbl, kw in [('Mejorado', 'MEJOR'), ('Grave', 'GRAVE'), ('Muerto', 'MUERT')]:
            ex = self._checkbox(ex, cb_y, checked=(kw in egreso), label=lbl)
            ex += 6
        self._date_cell(MARGIN + w1, y, w2, h, 'Fecha de defunci\u00f3n', _get(d, 'fecha_defuncion'))
        self.y -= h

    # -- FACTORES DE RIESGO --

    def _p1_factores_riesgo(self):
        d = self.d
        self._section("FACTORES DE RIESGO")

        factores = [
            ("Tuvo contacto con otro sospechoso de 7-23 d\u00edas previos al inicio de la erupci\u00f3n",
             _get(d, 'contacto_sospechoso_7_23', '').upper()),
            ("Hubo alg\u00fan caso sospechoso en la comunidad en los \u00faltimos 3 meses",
             _get(d, 'caso_sospechoso_comunidad_3m', '').upper()),
            ("Viaj\u00f3 durante los 7-23 d\u00edas previos al inicio de la erupci\u00f3n",
             _get(d, 'viajo_7_23_previo', '').upper()),
        ]

        wf = CONTENT_W * 0.80
        ws = CONTENT_W * 0.10
        wn = CONTENT_W * 0.10

        # Header
        h = 13
        y = self.y - h
        self.c.setFillColor(LIGHT_GRAY)
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(MARGIN, y, wf, h, fill=1)
        self.c.rect(MARGIN + wf, y, ws, h, fill=1)
        self.c.rect(MARGIN + wf + ws, y, wn, h, fill=1)
        self.c.setFillColor(black)
        self._sf(F_BOLD6)
        self.c.drawString(MARGIN + 2, y + 3, 'Factor')
        self.c.drawCentredString(MARGIN + wf + ws / 2, y + 3, 'SI')
        self.c.drawCentredString(MARGIN + wf + ws + wn / 2, y + 3, 'NO')
        self.y -= h

        h = 14
        for texto, val in factores:
            y = self.y - h
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.5)
            self.c.rect(MARGIN, y, wf, h)
            self.c.rect(MARGIN + wf, y, ws, h)
            self.c.rect(MARGIN + wf + ws, y, wn, h)
            self._sf(F_FACTOR)
            self.c.setFillColor(black)
            self.c.drawString(MARGIN + 2, y + (h - 5) / 2, _trunc(texto, wf - 4, 2.6))
            cb_y = y + (h - CB_SIZE) / 2
            self._checkbox(MARGIN + wf + (ws - CB_SIZE) / 2, cb_y, checked=(val == 'SI'))
            self._checkbox(MARGIN + wf + ws + (wn - CB_SIZE) / 2, cb_y, checked=(val == 'NO'))
            self.y -= h

    # -----------------------------------------------------------------------
    # PAGE 2
    # -----------------------------------------------------------------------

    def draw_page2(self):
        self.y = PAGE_H - MARGIN
        self._p2_datos_laboratorio()
        self._p2_clasificacion_final()
        self._p2_listado_contactos()

    def _p2_datos_laboratorio(self):
        d = self.d
        self._section("DATOS DE LABORATORIO")

        h = RH
        y = self.y - h
        x = MARGIN
        recolecto = _get(d, 'recolecto_muestra', '').upper()

        w1 = CONTENT_W * 0.30
        w2 = CONTENT_W * 0.70
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(x, y, w1, h)
        cb_y = y + (h - CB_SIZE) / 2
        self._checkbox(x + 3, cb_y, checked=(recolecto == 'NO'), label='No se recolect\u00f3 la muestra')
        self._cell(x + w1, y, w2, h, '\u00bfPor qu\u00e9 no se recolect\u00f3 la muestra?',
                   _get(d, 'motivo_no_recoleccion'))
        self.y -= h

        # Header
        h_hdr = 14
        y = self.y - h_hdr
        col_t = CONTENT_W * 0.20
        col_f = (CONTENT_W - col_t) / 3

        self.c.setFillColor(LIGHT_GRAY)
        hx = x
        for lbl, w in [('Tipo de Muestra', col_t), ('Fecha de recolecci\u00f3n', col_f),
                        ('Fecha de recepci\u00f3n (LNS)', col_f), ('Fecha Resultado (LNS)', col_f)]:
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.5)
            self.c.rect(hx, y, w, h_hdr, fill=1)
            self.c.setFillColor(black)
            self._sf(F_BOLD6)
            self.c.drawString(hx + 2, y + 4, _trunc(lbl, w - 4, 3.2))
            self.c.setFillColor(LIGHT_GRAY)
            hx += w
        self.c.setFillColor(black)
        self.y -= h_hdr

        # Data rows — per-sample date for recolección, global dates for recepción/resultado
        h = RH_DATE
        global_recepcion = _get(d, 'fecha_recepcion_laboratorio')
        global_resultado = _get(d, 'fecha_resultado_laboratorio')
        muestras = [
            ('Suero', 'muestra_suero_fecha'),
            ('Hisopado Nasofar\u00edngeo', 'muestra_hisopado_fecha'),
            ('Orina', 'muestra_orina_fecha'),
            ('Otra', 'muestra_otra_fecha'),
        ]

        for tipo, f_recoleccion in muestras:
            y = self.y - h
            self._cell_plain(x, y, col_t, h, tipo, font=F_VALUE)
            dx = x + col_t
            self._date_cell(dx, y, col_f, h, '', _get(d, f_recoleccion))
            dx += col_f
            self._date_cell(dx, y, col_f, h, '', global_recepcion)
            dx += col_f
            self._date_cell(dx, y, col_f, h, '', global_resultado)
            self.y -= h

    def _p2_clasificacion_final(self):
        d = self.d
        self.y -= 4
        self._section("CLASIFICACI\u00d3N FINAL")

        clasif = _get(d, 'clasificacion_caso', '').upper()

        h = RH
        y = self.y - h
        x = MARGIN
        w_lbl = CONTENT_W * 0.20
        w_rest = CONTENT_W * 0.80

        self._cell_plain(x, y, w_lbl, h, 'Clasificaci\u00f3n Final', font=F_BOLD6)
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.rect(x + w_lbl, y, w_rest, h)
        cb_y = y + (h - CB_SIZE) / 2
        cx = x + w_lbl + 5
        for lbl, kw in [('Confirmado', 'CONFIRM'), ('Descartado', 'DESCART'),
                         ('Confirmado por nexo epidemiol\u00f3gico', 'NEXO')]:
            cx = self._checkbox(cx, cb_y, checked=(kw in clasif), label=lbl)
            cx += 10
        self.y -= h

        h = RH_DATE
        y = self.y - h
        w1 = CONTENT_W * 0.40
        w2 = CONTENT_W * 0.60
        self._date_cell(x, y, w1, h, 'Fecha de clasificaci\u00f3n final', _get(d, 'fecha_clasificacion_final'))
        self._cell(x + w1, y, w2, h, 'Responsable clasificaci\u00f3n', _get(d, 'responsable_clasificacion'))
        self.y -= h

        self._row([
            (0.50, 'Cargo', _get(d, 'cargo_responsable')),
            (0.50, 'Tel\u00e9fono', _get(d, 'telefono_responsable')),
        ])

        h = RH_TALL
        y = self.y - h
        self._cell(MARGIN, y, CONTENT_W, h, 'Observaciones', _get(d, 'observaciones'))
        self.y -= h

    def _p2_listado_contactos(self):
        d = self.d
        self.y -= 4
        self._section("LISTADO DE CONTACTOS DIRECTOS")

        cols = [
            ('No', 0.05), ('Nombres y Apellidos del contacto', 0.28),
            ('Edad', 0.07), ('Sexo', 0.06), ('Tel\u00e9fono', 0.12),
            ('Direcci\u00f3n', 0.27), ('Fecha de contacto', 0.15),
        ]

        # Header
        h = 13
        y = self.y - h
        hx = MARGIN
        self.c.setFillColor(LIGHT_GRAY)
        for _, frac in cols:
            w = CONTENT_W * frac
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.5)
            self.c.rect(hx, y, w, h, fill=1)
            hx += w
        self.c.setFillColor(black)
        hx = MARGIN
        for lbl, frac in cols:
            w = CONTENT_W * frac
            self._sf(F_BOLD6)
            self.c.drawString(hx + 2, y + 3, _trunc(lbl, w - 4, 2.8))
            hx += w
        self.y -= h

        contactos = d.get('contactos', []) or []
        num_rows = max(10, len(contactos))
        h = 13

        for i in range(num_rows):
            y = self.y - h
            if y < MARGIN + 5:
                break
            contact = contactos[i] if i < len(contactos) else {}
            vals = [
                str(i + 1),
                _get(contact, 'nombre', ''),
                _get(contact, 'edad', ''),
                _get(contact, 'sexo', ''),
                _get(contact, 'telefono', ''),
                _get(contact, 'direccion', ''),
                _get(contact, 'fecha_contacto', ''),
            ]
            hx = MARGIN
            for j, (_, frac) in enumerate(cols):
                w = CONTENT_W * frac
                self.c.setStrokeColor(black)
                self.c.setLineWidth(0.5)
                self.c.rect(hx, y, w, h)
                if vals[j]:
                    self._sf(F_CONTACT)
                    self.c.setFillColor(black)
                    self.c.drawString(hx + 2, y + 3, _trunc(vals[j], w - 4, 2.8))
                hx += w
            self.y -= h

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generar_ficha_pdf(data: dict) -> bytes:
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=LETTER)
    c.setTitle("Ficha Epidemiol\u00f3gica - Sarampi\u00f3n/Rub\u00e9ola")
    c.setAuthor("IGSS Epidemiolog\u00eda")
    builder = FichaBuilder(c, data)
    builder.draw_page1()
    c.showPage()
    builder.draw_page2()
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

def generar_fichas_bulk(records: list, merge: bool = True) -> bytes:
    if not records:
        raise ValueError("No records provided")
    if merge:
        buf = io.BytesIO()
        c = Canvas(buf, pagesize=LETTER)
        c.setTitle("Fichas Epidemiol\u00f3gicas - Sarampi\u00f3n/Rub\u00e9ola")
        c.setAuthor("IGSS Epidemiolog\u00eda")
        for data in records:
            builder = FichaBuilder(c, data)
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
                pdf_bytes = generar_ficha_pdf(data)
                nombre = _get(data, 'nombres', 'caso')
                apellido = _get(data, 'apellidos', '')
                filename = f"{i+1:03d}_{nombre}_{apellido}.pdf".replace(' ', '_')
                zf.writestr(filename, pdf_bytes)
        zip_buf.seek(0)
        return zip_buf.read()

# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

def _test():
    sample = {
        'diagnostico_registrado': 'B05 - Sarampion',
        'unidad_medica': 'Hospital General de Enfermedades - Zona 9',
        'fecha_notificacion': '2026-03-15',
        'fecha_registro_diagnostico': '2026-03-15',
        'nom_responsable': 'Dr. Juan P\u00e9rez Garc\u00eda',
        'cargo_responsable': 'Epidemi\u00f3logo',
        'telefono_responsable': '2412-1224',
        'nombres': 'Mar\u00eda Isabel',
        'apellidos': 'L\u00f3pez Garc\u00eda',
        'sexo': 'F',
        'afiliacion': '1234567890101',
        'ocupacion': 'Ama de casa',
        'escolaridad': 'Primaria completa',
        'departamento_residencia': 'Guatemala',
        'municipio_residencia': 'Mixco',
        'poblado': 'Colonia El Milagro Zona 6',
        'direccion_exacta': '4ta Avenida 12-34 Zona 1, Colonia Las Flores',
        'pueblo_etnia': 'Ladino',
        'comunidad_linguistica': 'Espa\u00f1ol',
        'fecha_nacimiento': '1990-05-20',
        'edad_anios': '35',
        'edad_meses': '',
        'edad_dias': '',
        'nombre_encargado': 'Pedro Antonio L\u00f3pez M\u00e9ndez',
        'telefono_encargado': '5555-1234',
        'vacunado': 'SI',
        'fuente_info_vacuna': 'Carne',
        'numero_dosis_spr': '2',
        'fecha_ultima_dosis': '2015-03-10',
        'observaciones_vacuna': 'Esquema completo seg\u00fan carn\u00e9',
        'fecha_inicio_sintomas': '2026-03-10',
        'semana_epidemiologica': '11',
        'fecha_captacion': '2026-03-12',
        'fuente_notificacion': 'Servicio de salud p\u00fablica',
        'fecha_inicio_investigacion': '2026-03-14',
        'esta_embarazada': 'NO',
        'signo_tos': 'SI',
        'signo_coriza': 'NO',
        'signo_adenopatias': 'NO',
        'signo_artralgia': 'SI',
        'signo_conjuntivitis': 'SI',
        'signo_fiebre': 'SI',
        'asintomatico': 'NO',
        'fecha_inicio_erupcion': '2026-03-11',
        'fecha_inicio_fiebre': '2026-03-10',
        'temperatura_celsius': '38.5',
        'hospitalizado': 'SI',
        'hosp_nombre': 'Hospital General de Enfermedades Zona 9',
        'hosp_fecha': '2026-03-13',
        'no_registro_medico': 'HGE-2026-12345',
        'condicion_egreso': 'Mejorado',
        'fecha_defuncion': '',
        'contacto_sospechoso_7_23': 'SI',
        'caso_sospechoso_comunidad_3m': 'NO',
        'viajo_7_23_previo': 'NO',
        'recolecto_muestra': 'SI',
        'muestra_suero_fecha': '2026-03-13',
        'muestra_suero_recepcion': '2026-03-14',
        'muestra_suero_resultado': '2026-03-18',
        'muestra_hisopado_fecha': '2026-03-13',
        'muestra_hisopado_recepcion': '2026-03-14',
        'muestra_hisopado_resultado': '2026-03-19',
        'clasificacion_caso': 'Confirmado',
        'fecha_clasificacion_final': '2026-03-20',
        'responsable_clasificacion': 'Dra. Ana Patricia Mart\u00ednez Gonz\u00e1lez',
        'cargo_clasificacion': 'Coordinadora Epidemiolog\u00eda',
        'telefono_clasificacion': '2412-5678',
        'observaciones': 'Caso confirmado por laboratorio. PCR positivo para sarampi\u00f3n genotipo D8. '
                         'Contactos bajo vigilancia activa por 21 d\u00edas.',
        'contactos': [
            {'nombre': 'Carlos Antonio L\u00f3pez M\u00e9ndez', 'edad': '40', 'sexo': 'M',
             'telefono': '5555-0001', 'direccion': '4ta Av 12-34 Z1 Col Las Flores',
             'fecha_contacto': '2026-03-10'},
            {'nombre': 'Ana Lucrecia L\u00f3pez P\u00e9rez', 'edad': '12', 'sexo': 'F',
             'telefono': '5555-0001', 'direccion': '4ta Av 12-34 Z1 Col Las Flores',
             'fecha_contacto': '2026-03-10'},
            {'nombre': 'Roberto Enrique Garc\u00eda', 'edad': '65', 'sexo': 'M',
             'telefono': '5555-0002', 'direccion': '5ta Av 8-90 Z1',
             'fecha_contacto': '2026-03-11'},
        ],
    }

    pdf_bytes = generar_ficha_pdf(sample)
    out_path = '/tmp/ficha_sarampion_test.pdf'
    with open(out_path, 'wb') as f:
        f.write(pdf_bytes)
    print(f"Generated test PDF: {out_path} ({len(pdf_bytes)} bytes)")
    return out_path

if __name__ == '__main__':
    _test()
