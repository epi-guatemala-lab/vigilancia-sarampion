"""
PDF Generator for MSPAS Sarampion/Rubeola Epidemiological Form.

Generates a pixel-accurate replica of the official MSPAS ficha epidemiologica
using reportlab. Two pages, letter size, absolute coordinate positioning.

Public API:
    generar_ficha_pdf(data: dict) -> bytes
    generar_fichas_bulk(records: list[dict], merge: bool = True) -> bytes
"""

import io
import zipfile
import logging
from datetime import datetime

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, black, white

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = LETTER  # 612 x 792 pt
MARGIN_L = 30
MARGIN_R = PAGE_W - 30
MARGIN_T = PAGE_H - 30
MARGIN_B = 30
CONTENT_W = MARGIN_R - MARGIN_L  # 552 pt

SECTION_BG = Color(0.2, 0.2, 0.2, 1)  # dark gray #333
SECTION_H = 16
ROW_H = 14
CHECKBOX_SZ = 8
DATE_CELL_W = 12  # width per digit cell in date boxes

FONT_SECTION = ("Helvetica-Bold", 9)
FONT_LABEL = ("Helvetica", 6)
FONT_VALUE = ("Helvetica", 7.5)
FONT_BOLD = ("Helvetica-Bold", 7)
FONT_SMALL = ("Helvetica", 5.5)
FONT_TITLE = ("Helvetica-Bold", 9)
FONT_SUBTITLE = ("Helvetica-Bold", 7)
FONT_ITALIC = ("Helvetica-Oblique", 6)
FONT_CHECK_X = ("Helvetica-Bold", 7)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get(data: dict, key: str, default: str = '') -> str:
    """Safely extract a string value from data dict."""
    val = data.get(key, '') or ''
    val = str(val).strip()
    if val.upper() in ('NONE', 'NULL', 'N/A', 'NAN', ''):
        return default
    return val


def _parse_date(val: str) -> tuple:
    """Parse date string to (dd, mm, yyyy). Returns ('','','') on failure."""
    if not val:
        return ('', '', '')
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S', '%d-%m-%Y'):
        try:
            dt = datetime.strptime(val.strip()[:10], fmt)
            return (f"{dt.day:02d}", f"{dt.month:02d}", f"{dt.year:04d}")
        except (ValueError, TypeError):
            continue
    return ('', '', '')


def _y(top_y: float) -> float:
    """Convert top-down y to reportlab bottom-up y. top_y=0 means top margin."""
    return MARGIN_T - top_y


# ---------------------------------------------------------------------------
# Drawing primitives
# ---------------------------------------------------------------------------

class FichaDrawer:
    """Draws a single ficha on a canvas, tracking vertical position from top."""

    def __init__(self, c: Canvas, data: dict):
        self.c = c
        self.data = data
        self.y = 0  # current y offset from top margin (increases downward)

    # -- primitives --

    def _set_font(self, font_tuple):
        self.c.setFont(font_tuple[0], font_tuple[1])

    def _line(self, x1, y1, x2, y2):
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        self.c.line(x1, y1, x2, y2)

    def _rect(self, x, y, w, h, fill=False, stroke=True):
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        if fill:
            self.c.rect(x, y, w, h, fill=1, stroke=1 if stroke else 0)
        else:
            self.c.rect(x, y, w, h, fill=0, stroke=1)

    def _text(self, x, y, txt, font=None, color=black):
        if font:
            self._set_font(font)
        self.c.setFillColor(color)
        self.c.drawString(x, y, txt)
        self.c.setFillColor(black)

    def _text_centered(self, x, y, txt, font=None, color=black):
        if font:
            self._set_font(font)
        self.c.setFillColor(color)
        self.c.drawCentredString(x, y, txt)
        self.c.setFillColor(black)

    def _draw_section_header(self, text: str):
        """Draw a dark section header bar spanning full width."""
        ry = _y(self.y + SECTION_H)
        self.c.setFillColor(SECTION_BG)
        self._rect(MARGIN_L, ry, CONTENT_W, SECTION_H, fill=True)
        self.c.setFillColor(white)
        self._set_font(FONT_SECTION)
        self.c.drawString(MARGIN_L + 4, ry + 4, text)
        self.c.setFillColor(black)
        self.y += SECTION_H

    def _draw_checkbox(self, x, y_top, checked=False):
        """Draw a checkbox at absolute x, relative y_top from top margin."""
        ry = _y(y_top + CHECKBOX_SZ)
        self._rect(x, ry, CHECKBOX_SZ, CHECKBOX_SZ)
        if checked:
            self._set_font(FONT_CHECK_X)
            self.c.drawString(x + 1.5, ry + 1.5, "X")

    def _draw_field_box(self, x, y_top, w, h=ROW_H):
        """Draw an outlined field box."""
        ry = _y(y_top + h)
        self._rect(x, ry, w, h)

    def _draw_field(self, x, y_top, w, label: str, value: str = '', h=ROW_H):
        """Draw a labeled field box with value inside."""
        ry = _y(y_top + h)
        self._rect(x, ry, w, h)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + 2, ry + h - 5, label)
        if value:
            self._set_font(FONT_VALUE)
            # Truncate if too long
            max_chars = int((w - 4) / 4)
            if len(value) > max_chars:
                value = value[:max_chars]
            self.c.drawString(x + 2, ry + 2, value)

    def _draw_date_boxes(self, x, y_top, date_tuple, label='', h=ROW_H):
        """Draw date input boxes: DD / MM / YYYY with label."""
        ry = _y(y_top + h)
        cx = x
        if label:
            self._set_font(FONT_LABEL)
            self.c.drawString(cx + 2, ry + h - 5, label)

        # Date digit cells at bottom of row
        box_y = ry + 1
        box_h = 9
        start_x = cx + 2 if not label else cx + 2
        labels_below = [("Dia", 2), ("Mes", 2), ("Ano", 4)]
        dd, mm_val, yyyy = date_tuple if date_tuple else ('', '', '')
        digits = list(dd.ljust(2)) + list(mm_val.ljust(2)) + list(yyyy.ljust(4))

        dx = x + (DATE_CELL_W * 0.5) if not label else x + 2
        # Draw sub-labels
        self._set_font(FONT_SMALL)
        self.c.drawString(dx, ry + h - 5, "Dia")
        self.c.drawString(dx + DATE_CELL_W * 2 + 4, ry + h - 5, "Mes")
        self.c.drawString(dx + DATE_CELL_W * 4 + 8, ry + h - 5, "Ano")

        # Draw 8 cells: DD MM YYYY
        cell_x = dx
        self._set_font(FONT_VALUE)
        for i, digit in enumerate(digits):
            self._rect(cell_x, box_y, DATE_CELL_W, box_h)
            if digit.strip():
                self.c.drawCentredString(cell_x + DATE_CELL_W / 2, box_y + 2, digit)
            cell_x += DATE_CELL_W
            if i == 1 or i == 3:  # separators after DD and MM
                self.c.drawString(cell_x, box_y + 2, "/")
                cell_x += 4
        return cell_x  # return end x position

    def _draw_row_border(self, y_top, h=ROW_H):
        """Draw a full-width row border."""
        ry = _y(y_top + h)
        self._rect(MARGIN_L, ry, CONTENT_W, h)

    # -- Composite field row helpers --

    def _field_row(self, fields, h=ROW_H):
        """Draw a row of fields. fields = [(label, value, width_fraction), ...]"""
        x = MARGIN_L
        for label, value, frac in fields:
            w = CONTENT_W * frac
            self._draw_field(x, self.y, w, label, value, h)
            x += w
        self.y += h

    # ---------------------------------------------------------------------------
    # PAGE 1
    # ---------------------------------------------------------------------------

    def draw_page1(self):
        self.y = 0
        self._draw_header()
        self._draw_definition_text()
        self._draw_datos_generales()
        self._draw_datos_paciente()
        self._draw_antecedente_vacunal()
        self._draw_informacion_clinica()
        self._draw_factores_riesgo()

    def _draw_header(self):
        """Header with title and top-right disease selection box."""
        d = self.data
        # Center title
        self._text_centered(PAGE_W / 2, _y(self.y + 10), "MINISTERIO DE SALUD PUBLICA Y ASISTENCIA SOCIAL", FONT_TITLE)
        self._text_centered(PAGE_W / 2, _y(self.y + 20), "DEPARTAMENTO DE EPIDEMIOLOGIA", ("Helvetica-Bold", 8))
        self._text_centered(PAGE_W / 2, _y(self.y + 30), "FICHA EPIDEMIOLOGICA", ("Helvetica-Bold", 8))

        # Top-right box
        box_x = MARGIN_R - 200
        box_y_top = self.y
        box_w = 200
        box_h = 42
        ry = _y(box_y_top + box_h)
        self._rect(box_x, ry, box_w, box_h)
        self._text(box_x + 4, ry + box_h - 8, "FICHA EPIDEMIOLOGICA", ("Helvetica-Bold", 7))
        self._text(box_x + 4, ry + box_h - 17, "Caso sospechoso de:", FONT_LABEL)
        self._text(box_x + 4, ry + box_h - 25, "Marque la enfermedad que va a notificar", FONT_SMALL)

        # Determine which checkbox to mark
        diag = _get(d, 'diagnostico_registrado', '').upper()
        is_sarampion = 'B05' in diag or 'SARAMP' in diag
        is_rubeola = 'B06' in diag or 'RUBEO' in diag or 'RUBE' in diag

        # Sarampion checkbox
        cb_y = box_y_top + 30
        self._draw_checkbox(box_x + 10, cb_y, checked=is_sarampion)
        self._text(box_x + 22, _y(cb_y + CHECKBOX_SZ) + 1.5, "Sarampion", FONT_LABEL)

        # Rubeola checkbox
        self._draw_checkbox(box_x + 100, cb_y, checked=is_rubeola)
        self._text(box_x + 112, _y(cb_y + CHECKBOX_SZ) + 1.5, "Rubeola", FONT_LABEL)

        self.y += 44

    def _draw_definition_text(self):
        """Italic definition text below header."""
        self._set_font(FONT_ITALIC)
        self.c.drawString(MARGIN_L, _y(self.y + 8),
            "Sospecha rubeola en: Persona de cualquier edad en la que un trabajador de salud sospeche infeccion por rubeola.")
        self.c.drawString(MARGIN_L, _y(self.y + 16),
            "Sospeche sarampion en: Persona de cualquier edad que presente fiebre, erupcion y alguno de los siguientes signos: Tos, Coriza o Conjuntivitis.")
        self.y += 20

    def _draw_datos_generales(self):
        """DATOS GENERALES section."""
        d = self.data
        self._draw_section_header("DATOS GENERALES")

        # Row 1: Unidad notificadora
        self._field_row([("Unidad notificadora", _get(d, 'unidad_medica'), 1.0)])

        # Row 2: Fecha notificacion ... Fecha registro
        fn = _parse_date(_get(d, 'fecha_notificacion'))
        fr = _parse_date(_get(d, 'fecha_registro'))
        x = MARGIN_L
        w1 = CONTENT_W * 0.5
        w2 = CONTENT_W * 0.5
        ry = _y(self.y + ROW_H)
        self._rect(x, ry, w1, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + 2, ry + ROW_H - 5, "Fecha de notificacion")
        self._draw_date_boxes(x + 75, self.y + 2, fn)
        self._rect(x + w1, ry, w2, ROW_H)
        self.c.drawString(x + w1 + 2, ry + ROW_H - 5, "Fecha de registro")
        self._draw_date_boxes(x + w1 + 65, self.y + 2, fr)
        self.y += ROW_H

        # Row 3: Unidad Medica | Municipio | Departamento
        self._field_row([
            ("Unidad Medica", _get(d, 'unidad_medica'), 0.40),
            ("Municipio", _get(d, 'municipio_unidad'), 0.30),
            ("Departamento", _get(d, 'departamento_unidad'), 0.30),
        ])

        # Row 4: Responsable | Cargo | Telefono
        self._field_row([
            ("Responsable", _get(d, 'responsable'), 0.45),
            ("Cargo", _get(d, 'cargo_responsable'), 0.30),
            ("Telefono", _get(d, 'telefono_responsable'), 0.25),
        ])

    def _draw_datos_paciente(self):
        """DATOS PACIENTE section."""
        d = self.data
        self._draw_section_header("DATOS PACIENTE")

        sexo = _get(d, 'sexo', '').upper()

        # Row 1: Nombres | Apellidos | Sexo
        x = MARGIN_L
        w_nom = CONTENT_W * 0.35
        w_ape = CONTENT_W * 0.35
        w_sex = CONTENT_W * 0.30
        ry = _y(self.y + ROW_H)

        self._draw_field(x, self.y, w_nom, "Nombres", _get(d, 'nombres'))
        self._draw_field(x + w_nom, self.y, w_ape, "Apellidos", _get(d, 'apellidos'))
        # Sexo with checkboxes
        self._rect(x + w_nom + w_ape, ry, w_sex, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + w_nom + w_ape + 2, ry + ROW_H - 5, "Sexo")
        sx = x + w_nom + w_ape + 25
        self._draw_checkbox(sx, self.y + 3, checked=(sexo == 'F'))
        self._text(sx + 10, _y(self.y + 3 + CHECKBOX_SZ) + 1.5, "F", FONT_LABEL)
        self._draw_checkbox(sx + 30, self.y + 3, checked=(sexo == 'M'))
        self._text(sx + 40, _y(self.y + 3 + CHECKBOX_SZ) + 1.5, "M", FONT_LABEL)
        self.y += ROW_H

        # Row 2: CUI | Ocupacion | Escolaridad
        self._field_row([
            ("CUI paciente", _get(d, 'afiliacion'), 0.40),
            ("Ocupacion", _get(d, 'ocupacion'), 0.30),
            ("Escolaridad", _get(d, 'escolaridad'), 0.30),
        ])

        # Row 3: Residencia label
        ry = _y(self.y + ROW_H)
        self._rect(MARGIN_L, ry, CONTENT_W, ROW_H)
        self._text(MARGIN_L + 2, ry + ROW_H - 5, "Residencia", FONT_BOLD)
        self.y += ROW_H

        # Row 4: Departamento | Municipio | Poblado
        self._field_row([
            ("Departamento", _get(d, 'departamento_residencia'), 0.34),
            ("Municipio", _get(d, 'municipio_residencia'), 0.33),
            ("Poblado", _get(d, 'poblado'), 0.33),
        ])

        # Row 5: Direccion exacta
        self._field_row([("Direccion exacta", _get(d, 'direccion'), 1.0)])

        # Row 6: Pueblo pertinencia | Comunidad linguistica
        self._field_row([
            ("Pueblo de pertinencia", _get(d, 'pueblo_pertinencia'), 0.50),
            ("Comunidad linguistica", _get(d, 'comunidad_linguistica'), 0.50),
        ])

        # Row 7: Fecha Nacimiento | Anos | Meses | Dias
        fn = _parse_date(_get(d, 'fecha_nacimiento'))
        x = MARGIN_L
        w_fn = CONTENT_W * 0.50
        w_a = CONTENT_W * 0.17
        w_m = CONTENT_W * 0.17
        w_d = CONTENT_W * 0.16
        ry = _y(self.y + ROW_H)
        self._rect(x, ry, w_fn, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + 2, ry + ROW_H - 5, "Fecha de Nacimiento")
        self._draw_date_boxes(x + 72, self.y + 2, fn)
        self._draw_field(x + w_fn, self.y, w_a, "Anos", _get(d, 'edad_anos'))
        self._draw_field(x + w_fn + w_a, self.y, w_m, "Meses", _get(d, 'edad_meses'))
        self._draw_field(x + w_fn + w_a + w_m, self.y, w_d, "Dias", _get(d, 'edad_dias'))
        self.y += ROW_H

        # Row 8: Nombre Madre/Padre/Encargado | Telefono
        self._field_row([
            ("Nombre de la Madre, Padre o Encargado", _get(d, 'nombre_encargado'), 0.75),
            ("Telefono", _get(d, 'telefono_encargado'), 0.25),
        ])

    def _draw_antecedente_vacunal(self):
        """ANTECEDENTE VACUNAL section."""
        d = self.data
        self._draw_section_header("ANTECEDENTE VACUNAL")

        vacunado = _get(d, 'vacunado', '').upper()
        fuente = _get(d, 'fuente_info_vacuna', '').upper()

        # Row 1: Vacunado SI/NO | Fuente de informacion checkboxes
        x = MARGIN_L
        w1 = CONTENT_W * 0.35
        w2 = CONTENT_W * 0.65
        ry = _y(self.y + ROW_H)

        self._rect(x, ry, w1, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + 2, ry + ROW_H - 5, "Vacunado (SR/SPR)")
        cx = x + 68
        self._draw_checkbox(cx, self.y + 3, checked=(vacunado == 'SI'))
        self._text(cx + 10, _y(self.y + 3 + CHECKBOX_SZ) + 1.5, "SI", FONT_LABEL)
        self._draw_checkbox(cx + 28, self.y + 3, checked=(vacunado == 'NO'))
        self._text(cx + 38, _y(self.y + 3 + CHECKBOX_SZ) + 1.5, "NO", FONT_LABEL)

        # Fuente
        self._rect(x + w1, ry, w2, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + w1 + 2, ry + ROW_H - 5, "Fuente de Informacion")
        fx = x + w1 + 75
        for lbl, kw in [("Carne", "CARNE"), ("SIGSA 5a", "SIGSA"), ("Cuadernillo", "CUADERNILLO"), ("Verbal", "VERBAL")]:
            self._draw_checkbox(fx, self.y + 3, checked=(kw in fuente))
            self._text(fx + 10, _y(self.y + 3 + CHECKBOX_SZ) + 1.5, lbl, FONT_LABEL)
            fx += 55 if lbl != "Cuadernillo" else 60
        self.y += ROW_H

        # Row 2: No. dosis | Fecha ultima dosis | Observaciones
        fd = _parse_date(_get(d, 'fecha_ultima_dosis'))
        x = MARGIN_L
        w_d = CONTENT_W * 0.15
        w_f = CONTENT_W * 0.40
        w_o = CONTENT_W * 0.45
        ry = _y(self.y + ROW_H)
        self._draw_field(x, self.y, w_d, "No. dosis", _get(d, 'numero_dosis'))
        self._rect(x + w_d, ry, w_f, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + w_d + 2, ry + ROW_H - 5, "Fecha ultima dosis")
        self._draw_date_boxes(x + w_d + 65, self.y + 2, fd)
        self._draw_field(x + w_d + w_f, self.y, w_o, "Observaciones", _get(d, 'observaciones_vacuna'))
        self.y += ROW_H

    def _draw_informacion_clinica(self):
        """INFORMACION CLINICA section."""
        d = self.data
        self._draw_section_header("INFORMACION CLINICA")

        # --- Conocimiento de caso ---
        ry = _y(self.y + 10)
        self._text(MARGIN_L + 2, ry, "Conocimiento de caso", FONT_SUBTITLE)
        self.y += 10

        # Fecha inicio sintomas | Semana epidemiologica
        fi = _parse_date(_get(d, 'fecha_inicio_sintomas'))
        x = MARGIN_L
        w1 = CONTENT_W * 0.55
        w2 = CONTENT_W * 0.45
        ry = _y(self.y + ROW_H)
        self._rect(x, ry, w1, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + 2, ry + ROW_H - 5, "Fecha inicio sintomas")
        self._draw_date_boxes(x + 75, self.y + 2, fi)
        self._draw_field(x + w1, self.y, w2, "Semana Epidemiologica", _get(d, 'semana_epidemiologica'))
        self.y += ROW_H

        # Fecha captacion | Fuente notificacion
        fc = _parse_date(_get(d, 'fecha_captacion'))
        ry = _y(self.y + ROW_H)
        w_fc = CONTENT_W * 0.30
        w_fn = CONTENT_W * 0.70
        self._rect(x, ry, w_fc, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + 2, ry + ROW_H - 5, "Fecha de Captacion")
        self._draw_date_boxes(x + 65, self.y + 2, fc)

        self._rect(x + w_fc, ry, w_fn, ROW_H)
        self.c.drawString(x + w_fc + 2, ry + ROW_H - 5, "Fuente de notificacion")
        fuente_not = _get(d, 'fuente_notificacion', '').upper()
        fx = x + w_fc + 75
        for lbl, kw in [("Serv. salud", "SERVICIO"), ("Rumor", "RUMOR"),
                         ("Lab", "LABORATORIO"), ("Contacto", "CONTACTO"),
                         ("Visita dom.", "VISITA")]:
            self._draw_checkbox(fx, self.y + 3, checked=(kw in fuente_not))
            self._text(fx + 10, _y(self.y + 3 + CHECKBOX_SZ) + 1.5, lbl, FONT_SMALL)
            fx += 48
        self.y += ROW_H

        # Fecha planificada investigacion | Paciente embarazada
        fp = _parse_date(_get(d, 'fecha_inicio_investigacion'))
        emb = _get(d, 'paciente_embarazada', '').upper()
        ry = _y(self.y + ROW_H)
        w1 = CONTENT_W * 0.60
        w2 = CONTENT_W * 0.40
        self._rect(x, ry, w1, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + 2, ry + ROW_H - 5, "Fecha planificada inicio investigacion")
        self._draw_date_boxes(x + 130, self.y + 2, fp)
        self._rect(x + w1, ry, w2, ROW_H)
        self.c.drawString(x + w1 + 2, ry + ROW_H - 5, "Paciente embarazada")
        ex = x + w1 + 70
        self._draw_checkbox(ex, self.y + 3, checked=(emb == 'SI'))
        self._text(ex + 10, _y(self.y + 3 + CHECKBOX_SZ) + 1.5, "SI", FONT_LABEL)
        self._draw_checkbox(ex + 30, self.y + 3, checked=(emb == 'NO'))
        self._text(ex + 40, _y(self.y + 3 + CHECKBOX_SZ) + 1.5, "NO", FONT_LABEL)
        self._draw_checkbox(ex + 60, self.y + 3, checked=(emb == 'NA' or emb == 'N/A'))
        self._text(ex + 70, _y(self.y + 3 + CHECKBOX_SZ) + 1.5, "NA", FONT_LABEL)
        self.y += ROW_H

        # --- Signos y sintomas ---
        ry = _y(self.y + 10)
        self._text(MARGIN_L + 2, ry, "Signos y sintomas", FONT_SUBTITLE)
        self.y += 10

        # Grid of symptoms
        signos = {
            'Tos': _get(d, 'signo_tos'),
            'Coriza': _get(d, 'signo_coriza'),
            'Adenopatias': _get(d, 'signo_adenopatias'),
            'Artralgia o artritis': _get(d, 'signo_artralgia'),
            'Conjuntivitis': _get(d, 'signo_conjuntivitis'),
            'Fiebre': _get(d, 'signo_fiebre'),
        }
        ry = _y(self.y + ROW_H * 2)
        self._rect(MARGIN_L, ry, CONTENT_W, ROW_H * 2)

        # Left column
        left_signos = ['Tos', 'Coriza', 'Adenopatias']
        right_signos = ['Artralgia o artritis', 'Conjuntivitis', 'Fiebre']

        sy = self.y + 1
        for i, s in enumerate(left_signos):
            val = signos[s].upper()
            marked = val in ('SI', 'S', '1', 'TRUE', 'X')
            self._draw_checkbox(MARGIN_L + 10, sy + i * 8, checked=marked)
            self._text(MARGIN_L + 22, _y(sy + i * 8 + CHECKBOX_SZ) + 1.5, s, FONT_LABEL)

        for i, s in enumerate(right_signos):
            val = signos[s].upper()
            marked = val in ('SI', 'S', '1', 'TRUE', 'X')
            self._draw_checkbox(MARGIN_L + CONTENT_W * 0.40, sy + i * 8, checked=marked)
            self._text(MARGIN_L + CONTENT_W * 0.40 + 12, _y(sy + i * 8 + CHECKBOX_SZ) + 1.5, s, FONT_LABEL)

        # Asintomatico
        asint = _get(d, 'asintomatico', '').upper()
        ax = MARGIN_L + CONTENT_W * 0.75
        self._set_font(FONT_LABEL)
        self.c.drawString(ax, _y(sy + 2), "Asintomatico")
        self._draw_checkbox(ax + 42, sy + 1, checked=(asint == 'SI'))
        self._text(ax + 52, _y(sy + 1 + CHECKBOX_SZ) + 1.5, "SI", FONT_LABEL)
        self._draw_checkbox(ax + 66, sy + 1, checked=(asint == 'NO'))
        self._text(ax + 76, _y(sy + 1 + CHECKBOX_SZ) + 1.5, "No", FONT_LABEL)

        self.y += ROW_H * 2

        # Fecha erupcion | Fecha fiebre | Temperatura
        fe = _parse_date(_get(d, 'fecha_inicio_erupcion'))
        ff = _parse_date(_get(d, 'fecha_inicio_fiebre'))
        x = MARGIN_L
        w1 = CONTENT_W * 0.38
        w2 = CONTENT_W * 0.38
        w3 = CONTENT_W * 0.24
        ry = _y(self.y + ROW_H)
        self._rect(x, ry, w1, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + 2, ry + ROW_H - 5, "Fecha Inicio Erupcion")
        self._draw_date_boxes(x + 72, self.y + 2, fe)
        self._rect(x + w1, ry, w2, ROW_H)
        self.c.drawString(x + w1 + 2, ry + ROW_H - 5, "Fecha inicio fiebre")
        self._draw_date_boxes(x + w1 + 68, self.y + 2, ff)
        self._draw_field(x + w1 + w2, self.y, w3, "T grados C", _get(d, 'temperatura'))
        self.y += ROW_H

        # --- Hospitalizacion y defuncion ---
        ry = _y(self.y + 10)
        self._text(MARGIN_L + 2, ry, "Hospitalizacion y defuncion", FONT_SUBTITLE)
        self.y += 10

        hosp = _get(d, 'hospitalizado', '').upper()
        # Row: Hospitalizacion SI/NO | Nombre Hospital
        x = MARGIN_L
        w1 = CONTENT_W * 0.35
        w2 = CONTENT_W * 0.65
        ry = _y(self.y + ROW_H)
        self._rect(x, ry, w1, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + 2, ry + ROW_H - 5, "Hospitalizacion")
        hx = x + 55
        self._draw_checkbox(hx, self.y + 3, checked=(hosp == 'SI'))
        self._text(hx + 10, _y(self.y + 3 + CHECKBOX_SZ) + 1.5, "SI", FONT_LABEL)
        self._draw_checkbox(hx + 28, self.y + 3, checked=(hosp == 'NO'))
        self._text(hx + 38, _y(self.y + 3 + CHECKBOX_SZ) + 1.5, "NO", FONT_LABEL)
        self._draw_field(x + w1, self.y, w2, "Nombre del Hospital", _get(d, 'nombre_hospital'))
        self.y += ROW_H

        # Row: Fecha hospitalizacion | Numero registro medico
        fh = _parse_date(_get(d, 'fecha_hospitalizacion'))
        w1 = CONTENT_W * 0.50
        w2 = CONTENT_W * 0.50
        ry = _y(self.y + ROW_H)
        self._rect(x, ry, w1, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + 2, ry + ROW_H - 5, "Fecha de Hospitalizacion")
        self._draw_date_boxes(x + 80, self.y + 2, fh)
        self._draw_field(x + w1, self.y, w2, "Numero de Registro Medico", _get(d, 'registro_medico'))
        self.y += ROW_H

        # Row: Condicion egreso | Fecha defuncion
        egreso = _get(d, 'condicion_egreso', '').upper()
        fd = _parse_date(_get(d, 'fecha_defuncion'))
        w1 = CONTENT_W * 0.55
        w2 = CONTENT_W * 0.45
        ry = _y(self.y + ROW_H)
        self._rect(x, ry, w1, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + 2, ry + ROW_H - 5, "Condicion de Egreso")
        ex = x + 65
        for lbl, kw in [("Mejorado", "MEJOR"), ("Grave", "GRAVE"), ("Muerto", "MUERT")]:
            self._draw_checkbox(ex, self.y + 3, checked=(kw in egreso))
            self._text(ex + 10, _y(self.y + 3 + CHECKBOX_SZ) + 1.5, lbl, FONT_LABEL)
            ex += 50
        self._rect(x + w1, ry, w2, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + w1 + 2, ry + ROW_H - 5, "Fecha de defuncion")
        self._draw_date_boxes(x + w1 + 65, self.y + 2, fd)
        self.y += ROW_H

    def _draw_factores_riesgo(self):
        """FACTORES DE RIESGO section."""
        d = self.data
        self._draw_section_header("FACTORES DE RIESGO")

        factores = [
            ("Tuvo contacto con otro sospechoso de 7-23 dias previos al inicio de la erupcion",
             _get(d, 'contacto_sospechoso_7_23', '').upper()),
            ("Hubo algun caso sospechoso en la comunidad en los ultimos 3 meses",
             _get(d, 'caso_sospechoso_comunidad_3m', '').upper()),
            ("Viajo durante los 7-23 dias previos al inicio de la erupcion",
             _get(d, 'viajo_7_23_previo', '').upper()),
        ]

        # Header row
        x = MARGIN_L
        wf = CONTENT_W * 0.80
        ws = CONTENT_W * 0.10
        wn = CONTENT_W * 0.10
        ry = _y(self.y + ROW_H)
        self._rect(x, ry, wf, ROW_H)
        self._text(x + 2, ry + 4, "Factor", FONT_BOLD)
        self._rect(x + wf, ry, ws, ROW_H)
        self._text_centered(x + wf + ws / 2, ry + 4, "SI", FONT_BOLD)
        self._rect(x + wf + ws, ry, wn, ROW_H)
        self._text_centered(x + wf + ws + wn / 2, ry + 4, "NO", FONT_BOLD)
        self.y += ROW_H

        for texto, val in factores:
            ry = _y(self.y + ROW_H)
            self._rect(x, ry, wf, ROW_H)
            self._set_font(FONT_LABEL)
            # Truncate text to fit
            max_c = int((wf - 4) / 3.2)
            self.c.drawString(x + 2, ry + 4, texto[:max_c])
            self._rect(x + wf, ry, ws, ROW_H)
            self._rect(x + wf + ws, ry, wn, ROW_H)
            # SI/NO checkboxes centered in their cells
            si_x = x + wf + (ws - CHECKBOX_SZ) / 2
            no_x = x + wf + ws + (wn - CHECKBOX_SZ) / 2
            self._draw_checkbox(si_x, self.y + 3, checked=(val == 'SI'))
            self._draw_checkbox(no_x, self.y + 3, checked=(val == 'NO'))
            self.y += ROW_H

    # ---------------------------------------------------------------------------
    # PAGE 2
    # ---------------------------------------------------------------------------

    def draw_page2(self):
        self.y = 0
        self._draw_datos_laboratorio()
        self._draw_clasificacion_final()
        self._draw_listado_contactos()

    def _draw_datos_laboratorio(self):
        """DATOS DE LABORATORIO section."""
        d = self.data
        self._draw_section_header("DATOS DE LABORATORIO")

        # Row: No se recolecto muestra | Por que
        recolecto = _get(d, 'recolecto_muestra', '').upper()
        no_recolecto = (recolecto == 'NO')
        x = MARGIN_L
        w1 = CONTENT_W * 0.35
        w2 = CONTENT_W * 0.65
        ry = _y(self.y + ROW_H)
        self._rect(x, ry, w1, ROW_H)
        self._draw_checkbox(x + 4, self.y + 3, checked=no_recolecto)
        self._text(x + 16, ry + 4, "No se recolecto la muestra", FONT_LABEL)
        self._draw_field(x + w1, self.y, w2, "Por que no se recolecto la muestra?",
                         _get(d, 'motivo_no_muestra'))
        self.y += ROW_H

        # Lab table header
        col_tipo = CONTENT_W * 0.22
        col_fecha = (CONTENT_W - col_tipo) / 3  # 3 date columns

        ry = _y(self.y + ROW_H)
        # Header cells
        hx = x
        headers = [
            ("Tipo de Muestra", col_tipo),
            ("Fecha de recoleccion", col_fecha),
            ("Fecha de recepcion (LNS)", col_fecha),
            ("Fecha Resultado (LNS)", col_fecha),
        ]
        for lbl, w in headers:
            self._rect(hx, ry, w, ROW_H)
            self._text(hx + 2, ry + 4, lbl, FONT_BOLD)
            hx += w
        self.y += ROW_H

        # Lab rows
        muestras = [
            ("Suero", 'muestra_suero_fecha', 'muestra_suero_recepcion', 'muestra_suero_resultado'),
            ("Hisopado Nasofaringeo", 'muestra_hisopado_fecha', 'muestra_hisopado_recepcion', 'muestra_hisopado_resultado'),
            ("Orina", 'muestra_orina_fecha', 'muestra_orina_recepcion', 'muestra_orina_resultado'),
            ("Otra", 'muestra_otra_fecha', 'muestra_otra_recepcion', 'muestra_otra_resultado'),
        ]

        for tipo, f1, f2, f3 in muestras:
            ry = _y(self.y + ROW_H)
            # Tipo
            self._rect(x, ry, col_tipo, ROW_H)
            self._text(x + 2, ry + 4, tipo, FONT_LABEL)
            # Three date columns
            dx = x + col_tipo
            for fkey in [f1, f2, f3]:
                self._rect(dx, ry, col_fecha, ROW_H)
                dt = _parse_date(_get(d, fkey))
                if any(dt):
                    self._draw_date_boxes(dx + 4, self.y + 2, dt)
                dx += col_fecha
            self.y += ROW_H

    def _draw_clasificacion_final(self):
        """CLASIFICACION FINAL section."""
        d = self.data
        self.y += 4
        self._draw_section_header("CLASIFICACION FINAL")

        clasif = _get(d, 'clasificacion_caso', '').upper()
        x = MARGIN_L

        # Row: Clasificacion Final | checkboxes
        w_lbl = CONTENT_W * 0.25
        w_rest = CONTENT_W * 0.75
        ry = _y(self.y + ROW_H)
        self._rect(x, ry, w_lbl, ROW_H)
        self._text(x + 2, ry + 4, "Clasificacion Final", FONT_BOLD)
        self._rect(x + w_lbl, ry, w_rest, ROW_H)
        cx = x + w_lbl + 8
        checks = [
            ("Confirmado", "CONFIRM"),
            ("Descartado", "DESCART"),
            ("Confirmado por nexo epidemiologico", "NEXO"),
        ]
        for lbl, kw in checks:
            self._draw_checkbox(cx, self.y + 3, checked=(kw in clasif))
            self._text(cx + 10, _y(self.y + 3 + CHECKBOX_SZ) + 1.5, lbl, FONT_LABEL)
            cx += len(lbl) * 4 + 20
        self.y += ROW_H

        # Row: Fecha clasificacion final | Responsable clasificacion
        fc = _parse_date(_get(d, 'fecha_clasificacion'))
        w1 = CONTENT_W * 0.50
        w2 = CONTENT_W * 0.50
        ry = _y(self.y + ROW_H)
        self._rect(x, ry, w1, ROW_H)
        self._set_font(FONT_LABEL)
        self.c.drawString(x + 2, ry + ROW_H - 5, "Fecha de clasificacion final")
        self._draw_date_boxes(x + 95, self.y + 2, fc)
        self._draw_field(x + w1, self.y, w2, "Responsable clasificacion", _get(d, 'responsable_clasificacion'))
        self.y += ROW_H

        # Row: Cargo | Telefono
        self._field_row([
            ("Cargo", _get(d, 'cargo_clasificacion'), 0.50),
            ("Telefono", _get(d, 'telefono_clasificacion'), 0.50),
        ])

        # Row: Observaciones
        self._field_row([("Observaciones", _get(d, 'observaciones'), 1.0)], h=ROW_H * 2)

    def _draw_listado_contactos(self):
        """LISTADO DE CONTACTOS DIRECTOS section."""
        d = self.data
        self.y += 4
        self._draw_section_header("LISTADO DE CONTACTOS DIRECTOS")

        x = MARGIN_L
        # Column widths
        cols = [
            ("No", 0.05),
            ("Nombres y Apellidos del contacto", 0.25),
            ("Edad", 0.07),
            ("Sexo", 0.07),
            ("Telefono", 0.12),
            ("Direccion", 0.28),
            ("Fecha de contacto", 0.16),
        ]

        # Header
        ry = _y(self.y + ROW_H)
        hx = x
        for lbl, frac in cols:
            w = CONTENT_W * frac
            self._rect(hx, ry, w, ROW_H)
            self._text(hx + 2, ry + 4, lbl, FONT_BOLD)
            hx += w
        self.y += ROW_H

        # Data rows from contactos list, or empty
        contactos = d.get('contactos', []) or []
        num_rows = max(10, len(contactos))

        for i in range(num_rows):
            ry = _y(self.y + ROW_H)
            hx = x
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
            for j, (lbl, frac) in enumerate(cols):
                w = CONTENT_W * frac
                self._rect(hx, ry, w, ROW_H)
                if vals[j]:
                    self._set_font(FONT_VALUE)
                    max_c = int((w - 4) / 4)
                    self.c.drawString(hx + 2, ry + 3, vals[j][:max_c])
                hx += w
            self.y += ROW_H

            # Avoid going past page bottom
            if _y(self.y + ROW_H) < MARGIN_B:
                break


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generar_ficha_pdf(data: dict) -> bytes:
    """
    Generate a single ficha epidemiologica PDF from a data dict.

    Args:
        data: Dictionary with case field values (see field mapping in module docstring).

    Returns:
        PDF file content as bytes.
    """
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=LETTER)
    c.setTitle("Ficha Epidemiologica - Sarampion/Rubeola")
    c.setAuthor("IGSS Epidemiologia")

    drawer = FichaDrawer(c, data)

    # Page 1
    drawer.draw_page1()
    c.showPage()

    # Page 2
    drawer.draw_page2()
    c.showPage()

    c.save()
    buf.seek(0)
    return buf.read()


def generar_fichas_bulk(records: list, merge: bool = True) -> bytes:
    """
    Generate multiple fichas epidemiologicas.

    Args:
        records: List of data dicts, one per case.
        merge: If True, returns a single merged PDF. If False, returns a ZIP
               with individual PDFs named by index and patient name.

    Returns:
        PDF bytes (if merge=True) or ZIP bytes (if merge=False).
    """
    if not records:
        raise ValueError("No records provided")

    if merge:
        buf = io.BytesIO()
        c = Canvas(buf, pagesize=LETTER)
        c.setTitle("Fichas Epidemiologicas - Sarampion/Rubeola")
        c.setAuthor("IGSS Epidemiologia")

        for i, data in enumerate(records):
            drawer = FichaDrawer(c, data)
            drawer.draw_page1()
            c.showPage()
            drawer.draw_page2()
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

if __name__ == '__main__':
    # Generate a sample ficha with test data
    sample = {
        'diagnostico_registrado': 'B05 - Sarampion',
        'unidad_medica': 'Hospital General de Enfermedades - Zona 9',
        'fecha_notificacion': '2026-03-15',
        'fecha_registro': '2026-03-15',
        'municipio_unidad': 'Guatemala',
        'departamento_unidad': 'Guatemala',
        'responsable': 'Dr. Juan Perez',
        'cargo_responsable': 'Epidemiologo',
        'telefono_responsable': '2412-1224',
        'nombres': 'Maria Isabel',
        'apellidos': 'Lopez Garcia',
        'sexo': 'F',
        'afiliacion': '1234567890101',
        'ocupacion': 'Ama de casa',
        'escolaridad': 'Primaria',
        'departamento_residencia': 'Guatemala',
        'municipio_residencia': 'Mixco',
        'poblado': 'Zona 1',
        'direccion': '4ta Avenida 12-34 Zona 1',
        'pueblo_pertinencia': 'Ladino',
        'comunidad_linguistica': 'Espanol',
        'fecha_nacimiento': '1990-05-20',
        'edad_anos': '35',
        'edad_meses': '',
        'edad_dias': '',
        'nombre_encargado': 'Pedro Lopez',
        'telefono_encargado': '5555-1234',
        'vacunado': 'SI',
        'fuente_info_vacuna': 'Carne',
        'numero_dosis': '2',
        'fecha_ultima_dosis': '2015-03-10',
        'fecha_inicio_sintomas': '2026-03-10',
        'semana_epidemiologica': '11',
        'fecha_captacion': '2026-03-12',
        'fuente_notificacion': 'Servicio de salud',
        'signo_tos': 'SI',
        'signo_coriza': 'NO',
        'signo_adenopatias': 'NO',
        'signo_artralgia': 'NO',
        'signo_conjuntivitis': 'SI',
        'signo_fiebre': 'SI',
        'fecha_inicio_erupcion': '2026-03-11',
        'fecha_inicio_fiebre': '2026-03-10',
        'temperatura': '38.5',
        'hospitalizado': 'SI',
        'nombre_hospital': 'Hospital General de Enfermedades',
        'fecha_hospitalizacion': '2026-03-13',
        'registro_medico': '12345',
        'condicion_egreso': 'Mejorado',
        'contacto_sospechoso_7_23': 'SI',
        'caso_sospechoso_comunidad_3m': 'NO',
        'viajo_7_23_previo': 'NO',
        'recolecto_muestra': 'SI',
        'muestra_suero_fecha': '2026-03-13',
        'muestra_hisopado_fecha': '2026-03-13',
        'clasificacion_caso': 'Confirmado',
        'fecha_clasificacion': '2026-03-20',
        'responsable_clasificacion': 'Dra. Ana Martinez',
        'cargo_clasificacion': 'Coordinadora',
        'telefono_clasificacion': '2412-5678',
        'observaciones': 'Caso confirmado por laboratorio. PCR positivo para sarampion.',
        'contactos': [
            {'nombre': 'Carlos Lopez', 'edad': '40', 'sexo': 'M', 'telefono': '5555-0001',
             'direccion': '4ta Av 12-34 Z1', 'fecha_contacto': '2026-03-10'},
            {'nombre': 'Ana Lopez', 'edad': '12', 'sexo': 'F', 'telefono': '5555-0001',
             'direccion': '4ta Av 12-34 Z1', 'fecha_contacto': '2026-03-10'},
        ],
    }

    pdf_bytes = generar_ficha_pdf(sample)
    out_path = '/tmp/ficha_sarampion_test.pdf'
    with open(out_path, 'wb') as f:
        f.write(pdf_bytes)
    print(f"Generated test PDF: {out_path} ({len(pdf_bytes)} bytes)")
