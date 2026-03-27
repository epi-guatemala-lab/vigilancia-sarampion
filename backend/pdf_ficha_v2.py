"""
PDF Generator for MSPAS Sarampion/Rubeola Epidemiological Form - Version 2026.

Generates an EXACT replica of the official MSPAS ficha epidemiologica 2026
(GoData version) using reportlab Canvas with absolute coordinate positioning.

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
PAGE_W, PAGE_H = LETTER  # 612 x 792 pt
MARGIN = 18
CONTENT_W = PAGE_W - 2 * MARGIN  # ~576 pt
RIGHT = MARGIN + CONTENT_W

# Colors
SECTION_BG = Color(0.102, 0.137, 0.494, 1)   # #1a237e dark blue
LIGHT_GRAY = Color(0.92, 0.92, 0.92, 1)
MED_GRAY   = Color(0.75, 0.75, 0.75, 1)

# Row heights
SEC_H   = 13     # section header bar
RH      = 15     # standard row
RH_MD   = 18     # medium row (with date boxes)
RH_LG   = 22     # large row
RH_SM   = 12     # small row
RH_XS   = 10     # extra small

# Sizes
CB   = 6.0       # checkbox square side
DB   = 7.5       # date digit box side

# Fonts
F_SEC    = ("Helvetica-Bold", 7)
F_LBL    = ("Helvetica-Bold", 5.5)
F_LBL_SM = ("Helvetica-Bold", 5)
F_LBL_XS = ("Helvetica-Bold", 4.5)
F_VAL    = ("Helvetica", 6)
F_VAL_SM = ("Helvetica", 5.5)
F_VAL_XS = ("Helvetica", 5)
F_VAL_4  = ("Helvetica", 4.5)
F_BOLD6  = ("Helvetica-Bold", 6)
F_BOLD5  = ("Helvetica-Bold", 5)
F_BOLD7  = ("Helvetica-Bold", 7)
F_CHECK  = ("Helvetica-Bold", 8)
F_DDIG   = ("Helvetica", 5.5)
F_TINY   = ("Helvetica", 3.5)
F_CB_LBL = ("Helvetica", 5)
F_CB_SM  = ("Helvetica", 4.5)
F_NOTE   = ("Helvetica-Bold", 5)
F_NOTE2  = ("Helvetica", 4.5)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get(data, key, default=''):
    val = data.get(key, '') or ''
    val = str(val).strip()
    if val.upper() in ('NONE', 'NULL', 'N/A', 'NAN', ''):
        return default
    return val


def _parse_date(val):
    if not val:
        return ('', '', '')
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S', '%d-%m-%Y'):
        try:
            dt = datetime.strptime(val.strip()[:10], fmt)
            return (f"{dt.day:02d}", f"{dt.month:02d}", f"{dt.year:04d}")
        except (ValueError, TypeError):
            continue
    return ('', '', '')


def _trunc(text, w, cw=3.2):
    mx = max(3, int(w / cw))
    if len(text) > mx:
        return text[:mx - 1] + '\u2026'
    return text


def _chk(v):
    return str(v).strip().upper() in ('SI', 'S', '1', 'TRUE', 'X', 'YES')


def _is_no(v):
    return str(v).strip().upper() == 'NO'


def _is_desc(v):
    return str(v).strip().upper() in ('DESCONOCIDO', 'DESC', 'NK', '?', 'D', 'U')


# ---------------------------------------------------------------------------
# FichaV2Builder
# ---------------------------------------------------------------------------

class FichaV2Builder:

    def __init__(self, c, data):
        self.c = c
        self.d = data
        self.y = PAGE_H - MARGIN

    def _g(self, key, default=''):
        return _get(self.d, key, default)

    def _sf(self, f):
        self.c.setFont(f[0], f[1])

    def _rect(self, x, y, w, h, lw=0.4):
        self.c.setStrokeColor(black)
        self.c.setLineWidth(lw)
        self.c.rect(x, y, w, h, fill=0, stroke=1)

    def _fill_rect(self, x, y, w, h, fc, lw=0.4):
        self.c.setFillColor(fc)
        self.c.setStrokeColor(black)
        self.c.setLineWidth(lw)
        self.c.rect(x, y, w, h, fill=1, stroke=1)
        self.c.setFillColor(black)

    def _cell(self, x, y, w, h, label='', value='', fl=None, fv=None, cv=False, bg=None):
        if bg:
            self._fill_rect(x, y, w, h, bg)
        else:
            self._rect(x, y, w, h)
        _fl = fl or F_LBL
        _fv = fv or F_VAL
        if label:
            self._sf(_fl)
            self.c.setFillColor(black)
            self.c.drawString(x + 1.5, y + h - _fl[1] - 1, _trunc(label, w - 3, 2.8))
        if value:
            self._sf(_fv)
            self.c.setFillColor(black)
            ty = y + 1.5 if label else y + (h - _fv[1]) / 2
            if cv:
                self.c.drawCentredString(x + w / 2, ty, _trunc(value, w - 3, 3.0))
            else:
                self.c.drawString(x + 1.5, ty, _trunc(value, w - 3, 3.0))

    def _cell_c(self, x, y, w, h, text='', font=None, bg=None):
        if bg:
            self._fill_rect(x, y, w, h, bg)
        else:
            self._rect(x, y, w, h)
        if text:
            f = font or F_VAL
            self._sf(f)
            self.c.setFillColor(black)
            self.c.drawCentredString(x + w / 2, y + (h - f[1]) / 2, _trunc(text, w - 2, 2.8))

    def _cell_l(self, x, y, w, h, text='', font=None, bg=None):
        if bg:
            self._fill_rect(x, y, w, h, bg)
        else:
            self._rect(x, y, w, h)
        if text:
            f = font or F_VAL
            self._sf(f)
            self.c.setFillColor(black)
            self.c.drawString(x + 1.5, y + (h - f[1]) / 2, _trunc(text, w - 3, 2.8))

    def _shdr(self, title):
        h = SEC_H
        y = self.y - h
        self._fill_rect(MARGIN, y, CONTENT_W, h, SECTION_BG)
        self.c.setFillColor(white)
        self._sf(F_SEC)
        self.c.drawCentredString(MARGIN + CONTENT_W / 2, y + (h - F_SEC[1]) / 2 + 0.5, title)
        self.c.setFillColor(black)
        self.y -= h

    def _cb(self, x, y, checked=False, sz=None):
        s = sz or CB
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.4)
        self.c.rect(x, y, s, s, fill=0, stroke=1)
        if checked:
            self._sf(F_CHECK)
            self.c.setFillColor(black)
            self.c.drawCentredString(x + s / 2, y + (s - 6) / 2, 'X')
        return x + s

    def _cbl(self, x, y, checked, label, font=None, sz=None, gap=1.5):
        s = sz or CB
        self._cb(x, y, checked, sz=s)
        f = font or F_CB_LBL
        self._sf(f)
        self.c.setFillColor(black)
        self.c.drawString(x + s + 1, y + 0.5, label)
        tw = self.c.stringWidth(label, f[0], f[1])
        return x + s + 1 + tw + gap

    def _tri(self, x, y, value, font=None, sz=None, gap=1.5):
        v = str(value).strip().upper()
        nx = self._cbl(x, y, v in ('SI', '1', 'TRUE', 'S', 'X', 'YES'), 'Si', font=font, sz=sz, gap=gap)
        nx = self._cbl(nx + 1, y, v == 'NO', 'No', font=font, sz=sz, gap=gap)
        nx = self._cbl(nx + 1, y, v in ('DESCONOCIDO', 'DESC', 'NK', '?', 'D', 'U'), 'Desconocido', font=font, sz=sz, gap=gap)
        return nx

    def _dboxes(self, x, y, date_str='', labels=True):
        dd, mm, yyyy = _parse_date(date_str)
        bs = DB
        bx = x
        if labels:
            self._sf(F_TINY)
            self.c.setFillColor(black)
            self.c.drawCentredString(bx + bs, y + bs + 1.5, 'Dia')
        for i, ch in enumerate(dd.ljust(2)):
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.3)
            self.c.rect(bx + i * bs, y, bs, bs)
            if ch.strip():
                self._sf(F_DDIG)
                self.c.setFillColor(black)
                self.c.drawCentredString(bx + i * bs + bs / 2, y + 1.2, ch)
        bx += 2 * bs + 2
        if labels:
            self._sf(F_TINY)
            self.c.setFillColor(black)
            self.c.drawCentredString(bx + bs, y + bs + 1.5, 'Mes')
        for i, ch in enumerate(mm.ljust(2)):
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.3)
            self.c.rect(bx + i * bs, y, bs, bs)
            if ch.strip():
                self._sf(F_DDIG)
                self.c.setFillColor(black)
                self.c.drawCentredString(bx + i * bs + bs / 2, y + 1.2, ch)
        bx += 2 * bs + 2
        if labels:
            self._sf(F_TINY)
            self.c.setFillColor(black)
            self.c.drawCentredString(bx + 2 * bs, y + bs + 1.5, 'Ano')
        for i, ch in enumerate(yyyy.ljust(4)):
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.3)
            self.c.rect(bx + i * bs, y, bs, bs)
            if ch.strip():
                self._sf(F_DDIG)
                self.c.setFillColor(black)
                self.c.drawCentredString(bx + i * bs + bs / 2, y + 1.2, ch)
        return (2 + 2 + 4) * bs + 4

    def _dcell(self, x, y, w, h, label='', ds=''):
        self._rect(x, y, w, h)
        if label:
            self._sf(F_LBL)
            self.c.setFillColor(black)
            self.c.drawString(x + 1.5, y + h - F_LBL[1] - 1, _trunc(label, w - 3, 2.8))
        self._dboxes(x + 2, y + 1.5, ds)

    # -----------------------------------------------------------------------
    # PAGE 1
    # -----------------------------------------------------------------------

    def draw_page1(self):
        self.y = PAGE_H - MARGIN
        self._p1_header()
        self._p1_instructions()
        self._p1_diag()
        self._s1()
        self._s2()
        self._s3()
        self._s4()

    def _p1_header(self):
        c = self.c
        top = self.y
        logo_sz = 44
        lx, ly = MARGIN, top - logo_sz
        # Logo
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        logo_path = None
        for fname in ('escudo_guatemala.png', 'mspas_logo.png'):
            cand = os.path.join(assets_dir, fname)
            if os.path.isfile(cand):
                logo_path = cand
                break
        if logo_path:
            try:
                c.drawImage(logo_path, lx, ly, width=logo_sz, height=logo_sz, preserveAspectRatio=True, mask='auto')
            except Exception:
                logo_path = None
        if not logo_path:
            c.setStrokeColor(black)
            c.setLineWidth(0.5)
            c.rect(lx, ly, logo_sz, logo_sz)
            self._sf(("Helvetica-Bold", 5))
            c.setFillColor(MED_GRAY)
            c.drawCentredString(lx + logo_sz / 2, ly + logo_sz / 2, 'MSPAS')
            c.setFillColor(black)

        mx = MARGIN + logo_sz + 4
        self._sf(("Helvetica-Bold", 7.5))
        c.setFillColor(black)
        c.drawString(mx, top - 10, "MINISTERIO DE SALUD PUBLICA")
        c.drawString(mx + 12, top - 19, "Y ASISTENCIA SOCIAL")

        tc = MARGIN + CONTENT_W / 2 + 20
        self._sf(("Helvetica-Bold", 9))
        c.drawCentredString(tc, top - 10, "FICHA EPIDEMIOLOGICA DE VIGILANCIA DE")
        c.drawCentredString(tc, top - 21, "SARAMPION RUBEOLA")
        self._sf(("Helvetica", 7))
        c.drawCentredString(tc, top - 30, "Direccion de Epidemiologia y Gestion del Riesgo")

        vbw, vbh = 45, 15
        vbx = RIGHT - vbw - 2
        vby = top - logo_sz + 2
        c.setStrokeColor(black)
        c.setLineWidth(0.3)
        c.rect(vbx, vby, vbw, vbh)
        self._sf(("Helvetica-Oblique", 5.5))
        c.drawCentredString(vbx + vbw / 2, vby + 4, "Version 2026")
        self.y = top - logo_sz - 1

    def _p1_instructions(self):
        c = self.c
        y = self.y - 20
        self._sf(("Helvetica", 4.5))
        c.setFillColor(black)
        c.drawString(MARGIN + 2, y + 12, "Llene esta ficha para todo paciente en quien un trabajador de salud sospeche sarampion o rubeola o que presente fiebre y exantema/rash. Durante el primer")
        c.drawString(MARGIN + 2, y + 7, "contacto con el paciente, el trabajador de salud debe hacer todo lo posible para obtener datos epidemiologicos, clinicos, una muestra de sangre y las dos muestras")
        c.drawString(MARGIN + 2, y + 2, "para deteccion viral (1), ya que este podria ser el unico contacto con el paciente. Antes de completar el instrumento, leer las instrucciones del llenado.")
        y -= 8
        self._sf(("Helvetica", 4))
        c.drawString(MARGIN + 2, y + 2, "(1)  Recolecte una muestra respiratoria hasta 14 dias y una muestra de orina hasta 10 dias, a partir de la fecha de inicio de exantema/ rash del caso sospechoso.")
        self.y = y

    def _p1_diag(self):
        c = self.c
        h = RH_LG
        y = self.y - h
        x = MARGIN
        self._rect(x, y, CONTENT_W, h)
        self._sf(F_LBL)
        c.setFillColor(black)
        c.drawString(x + 2, y + h - 7, "Diagnostico de")
        c.drawString(x + 2, y + h - 13, "Sospecha")

        diag = self._g('diagnostico_registrado', '').upper()
        is_sar = 'B05' in diag or 'SARAMP' in diag
        is_rub = 'B06' in diag or 'RUBEO' in diag
        is_den = 'A90' in diag or 'A91' in diag or 'DENGUE' in diag
        is_arbo = 'ARBO' in diag
        is_feb = 'FEBRIL' in diag or 'EXANT' in diag
        is_alt = 'ALTAMENTE' in diag or 'SOSPECHOSO' in diag
        if not any([is_sar, is_rub, is_den, is_arbo, is_feb, is_alt]):
            is_sar = True

        cy1 = y + h - 9
        cx = x + 55
        cx = self._cbl(cx, cy1, is_sar, 'Sarampion', font=F_CB_LBL, gap=4)
        cx = self._cbl(cx, cy1, is_rub, 'Rubeola', font=F_CB_LBL, gap=4)
        cx = self._cbl(cx, cy1, is_den, 'Dengue', font=F_CB_LBL, gap=4)
        cx = self._cbl(cx, cy1, is_arbo, 'Otra Arbovirosis', font=F_CB_LBL, gap=2)
        self._sf(F_VAL_XS)
        c.drawString(cx + 1, cy1 + 0.5, 'Especifique')

        cy2 = y + 3
        cx2 = x + 55
        cx2 = self._cbl(cx2, cy2, is_feb, 'Otra febril exantematica', font=F_CB_LBL, gap=2)
        self._sf(F_VAL_XS)
        c.drawString(cx2 + 1, cy2 + 0.5, 'Especifique')
        self._cbl(x + CONTENT_W * 0.58, cy2, is_alt, 'Caso altamente sospechoso de Sarampion', font=F_CB_LBL)
        self.y -= h

    # -- S1: DATOS DE LA UNIDAD NOTIFICADORA --
    def _s1(self):
        d = self.d
        self._shdr("1.    DATOS DE LA UNIDAD NOTIFICADORA")
        x = MARGIN

        h = RH_MD
        y = self.y - h
        w1 = CONTENT_W * 0.17; w2 = CONTENT_W * 0.33; w3 = CONTENT_W * 0.22; w4 = CONTENT_W * 0.28
        self._dcell(x, y, w1, h, 'Fecha de Notificacion', _get(d, 'fecha_notificacion'))
        self._cell(x + w1, y, w2, h, 'Direccion de Area de Salud', _get(d, 'area_salud'))
        self._cell(x + w1 + w2, y, w3, h, 'Distrito de Salud', _get(d, 'distrito'))
        self._cell(x + w1 + w2 + w3, y, w4, h, 'Servicio de Salud', _get(d, 'unidad_medica'))
        self.y -= h

        h = RH_MD
        y = self.y - h
        w1 = CONTENT_W * 0.14; w2 = CONTENT_W * 0.18; w3 = CONTENT_W * 0.28; w4 = CONTENT_W * 0.18; w5 = CONTENT_W * 0.22
        self._rect(x, y, w1, h)
        self._sf(F_LBL_XS)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + h - 5.5, 'Fecha de')
        self.c.drawString(x + 1.5, y + h - 10, 'Consulta')
        self._dboxes(x + 2, y + 1.5, _get(d, 'fecha_consulta'))

        self._rect(x + w1, y, w2, h)
        self._sf(F_LBL_XS)
        self.c.setFillColor(black)
        self.c.drawString(x + w1 + 1.5, y + h - 5.5, 'Fecha de investigacion')
        self.c.drawString(x + w1 + 1.5, y + h - 10, 'Domiciliaria')
        self._dboxes(x + w1 + 2, y + 1.5, _get(d, 'fecha_investigacion_domiciliaria'))

        self._cell(x + w1 + w2, y, w3, h, 'Nombre de quien investiga', _get(d, 'investigador'))
        self._cell(x + w1 + w2 + w3, y, w4, h, 'Cargo', _get(d, 'cargo_investigador'))
        self._cell(x + w1 + w2 + w3 + w4, y, w5, h, 'Telefono y correo', _get(d, 'telefono_investigador'))
        self.y -= h

        h = RH
        y = self.y - h
        wh = CONTENT_W / 2
        tipo = _get(d, 'tipo_establecimiento', '').upper()
        self._rect(x, y, wh, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + (h - 5) / 2, 'Seguro Social (IGSS)')
        self._cb(x + 70, y + (h - CB) / 2, checked=('IGSS' in tipo or 'SEGURO' in tipo))
        self._sf(F_LBL_XS)
        self.c.drawString(x + 78, y + h - 5, 'Especifique')

        self._rect(x + wh, y, wh, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(x + wh + 1.5, y + (h - 5) / 2, 'Establecimiento Privado')
        self._cb(x + wh + 80, y + (h - CB) / 2, checked=('PRIVADO' in tipo or 'PARTICULAR' in tipo))
        self._sf(F_LBL_XS)
        self.c.drawString(x + wh + 88, y + h - 5, 'Especifique')
        self.y -= h

        h = RH_LG + 2
        y = self.y - h
        self._rect(x, y, CONTENT_W, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + h - 7, 'Fuente de notificacion')
        fuente = _get(d, 'fuente_notificacion', '').upper()
        r1 = [('SERVICIO' in fuente or 'SALUD' in fuente, 'Servicio De Salud'),
              ('LABORATORIO' in fuente, 'Laboratorio'),
              ('ACTIVA INSTITUCIONAL' in fuente or 'BAI' in fuente, 'Busqueda Activa Institucional'),
              ('ACTIVA COMUNITARIA' in fuente or 'BAC' in fuente, 'Busqueda Activa Comunitaria'),
              ('LABORATORIAL' in fuente, 'Busqueda Activa Laboratorial')]
        cy = y + h - 14
        cx = x + 65
        for chk, lbl in r1:
            cx = self._cbl(cx, cy, chk, lbl, font=F_CB_SM, gap=3)
            cx += 2
        r2 = [('INVESTIGACION' in fuente or 'CONTACTO' in fuente, 'Investigacion De Contactos'),
              ('COMUNIDAD' in fuente or 'REPORTADO' in fuente, 'Caso Reportado Por La Comunidad'),
              ('AUTO' in fuente, 'Auto Notificacion Por Numero Gratuito'),
              ('OTRO' in fuente, 'Otro')]
        cy = y + 3
        cx = x + 65
        for chk, lbl in r2:
            cx = self._cbl(cx, cy, chk, lbl, font=F_CB_SM, gap=3)
            cx += 2
        self._sf(F_LBL_XS)
        self.c.drawString(RIGHT - 40, y + 3, 'Especifique')
        self.y -= h

    # -- S2: INFORMACION DEL PACIENTE --
    def _s2(self):
        d = self.d
        self._shdr("2.    INFORMACION DEL PACIENTE")
        x = MARGIN
        sexo = _get(d, 'sexo', '').upper()

        h = RH
        y = self.y - h
        wn = CONTENT_W * 0.32; wa = CONTENT_W * 0.28; wsx = CONTENT_W * 0.06; wm = CONTENT_W * 0.17; wf = CONTENT_W * 0.17
        self._cell(x, y, wn, h, 'Nombres', _get(d, 'nombres'))
        self._cell(x + wn, y, wa, h, 'Apellidos', _get(d, 'apellidos'))
        self._cell_c(x + wn + wa, y, wsx, h, 'Sexo', font=F_LBL)
        sx = x + wn + wa + wsx
        self._rect(sx, y, wm, h)
        self._cbl(sx + 3, y + (h - CB) / 2, sexo in ('M', 'MASCULINO'), 'Masculino', font=F_CB_LBL)
        self._rect(sx + wm, y, wf, h)
        self._cbl(sx + wm + 3, y + (h - CB) / 2, sexo in ('F', 'FEMENINO'), 'Femenino', font=F_CB_LBL)
        self.y -= h

        h = RH_MD
        y = self.y - h
        wfn = CONTENT_W * 0.22; we = CONTENT_W * 0.30; wc = CONTENT_W * 0.48
        self._rect(x, y, wfn, h)
        self._sf(F_LBL_XS)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + h - 5.5, 'Fecha De Nacimiento')
        self._dboxes(x + 2, y + 1.5, _get(d, 'fecha_nacimiento'))

        ex = x + wfn
        self._rect(ex, y, we, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(ex + 1.5, y + h - 6, 'Edad')
        ea = _get(d, 'edad_anios', ''); em = _get(d, 'edad_meses', ''); ed = _get(d, 'edad_dias', '')
        sw = we / 4
        for i, (lbl, val) in enumerate([('Anos', ea), ('Meses', em), ('Dias', ed)]):
            sx2 = ex + sw * (i + 1)
            self._sf(F_TINY)
            self.c.setFillColor(black)
            self.c.drawCentredString(sx2 + sw / 2, y + h - 5, lbl)
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.3)
            bx2 = sx2 + 2; by2 = y + 2; bw2 = sw - 4; bh2 = h - 10
            self.c.rect(bx2, by2, bw2, bh2)
            if val:
                self._sf(F_VAL)
                self.c.setFillColor(black)
                self.c.drawCentredString(bx2 + bw2 / 2, by2 + 1, val)
        self._cell(ex + we, y, wc, h, 'Codigo Unico de Identificacion (DPI, PASAPORTE, OTRO)', _get(d, 'afiliacion'))
        self.y -= h

        h = RH
        y = self.y - h
        self._cell(x, y, CONTENT_W * 0.35, h, 'Nombre del Tutor', _get(d, 'nombre_encargado'))
        self._cell(x + CONTENT_W * 0.35, y, CONTENT_W * 0.20, h, 'Parentesco', _get(d, 'parentesco_tutor'))
        self._cell(x + CONTENT_W * 0.55, y, CONTENT_W * 0.45, h, 'Codigo Unico de Identificacion', _get(d, 'dpi_tutor'))
        self.y -= h

        h = RH
        y = self.y - h
        pueblo = _get(d, 'pueblo_etnia', '').upper()
        wp = CONTENT_W * 0.38; wext = CONTENT_W * 0.13; wmig = CONTENT_W * 0.14; wemb = CONTENT_W * 0.20; wtri = CONTENT_W * 0.15
        self._rect(x, y, wp, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + (h - 5) / 2, 'Pueblo')
        cy = y + (h - CB) / 2
        px = x + 28
        for lbl, kw in [('Ladino', 'LADINO'), ('Maya', 'MAYA'), ('Garifuna', 'GARI'), ('Xinca', 'XINCA')]:
            px = self._cbl(px, cy, kw in pueblo, lbl, font=F_CB_SM, gap=2)
            px += 1

        ext2 = _get(d, 'extranjero', '').upper()
        self._rect(x + wp, y, wext, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(x + wp + 1.5, y + (h - 5) / 2, 'Extranjero')
        ex3 = x + wp + 38
        ex3 = self._cbl(ex3, cy, _chk(ext2), 'Si', font=F_CB_SM, gap=1)
        self._cbl(ex3 + 1, cy, _is_no(ext2), 'No', font=F_CB_SM)

        mig = _get(d, 'migrante', '').upper()
        mx2 = x + wp + wext
        self._rect(mx2, y, wmig, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(mx2 + 1.5, y + (h - 5) / 2, 'Migrante')
        mx3 = mx2 + 30
        mx3 = self._cbl(mx3, cy, _chk(mig), 'Si', font=F_CB_SM, gap=1)
        self._cbl(mx3 + 1, cy, _is_no(mig), 'No', font=F_CB_SM)

        emb = _get(d, 'esta_embarazada', '').upper()
        emx = x + wp + wext + wmig
        self._rect(emx, y, wemb, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(emx + 1.5, y + (h - 5) / 2, 'Embarazada')
        emx2 = emx + 40
        emx2 = self._cbl(emx2, cy, _chk(emb), 'Si', font=F_CB_SM, gap=1)
        self._cbl(emx2 + 1, cy, _is_no(emb), 'No', font=F_CB_SM)
        self.y -= h

        h = RH
        y = self.y - h
        self._cell(x, y, CONTENT_W * 0.15, h, 'Trimestre de Embarazo', _get(d, 'trimestre'))
        self._cell(x + CONTENT_W * 0.15, y, CONTENT_W * 0.25, h, 'Ocupacion', _get(d, 'ocupacion'))
        self._cell(x + CONTENT_W * 0.40, y, CONTENT_W * 0.30, h, 'Escolaridad', _get(d, 'escolaridad'))
        self._cell(x + CONTENT_W * 0.70, y, CONTENT_W * 0.30, h, 'Telefono', _get(d, 'telefono_paciente'))
        self.y -= h

        h = RH
        y = self.y - h
        self._cell(x, y, CONTENT_W * 0.22, h, 'Pais de Residencia', _get(d, 'pais_residencia', 'Guatemala'))
        self._cell(x + CONTENT_W * 0.22, y, CONTENT_W * 0.30, h, 'Departamento de Residencia', _get(d, 'departamento_residencia'))
        self._cell(x + CONTENT_W * 0.52, y, CONTENT_W * 0.48, h, 'Municipio de Residencia', _get(d, 'municipio_residencia'))
        self.y -= h

        h = RH
        y = self.y - h
        self._cell(x, y, CONTENT_W * 0.55, h, 'Direccion de Residencia', _get(d, 'direccion_exacta'))
        self._cell(x + CONTENT_W * 0.55, y, CONTENT_W * 0.45, h, 'Lugar Poblado', _get(d, 'poblado'))
        self.y -= h

    # -- S3: ANTECEDENTES MEDICOS Y DE VACUNACION --
    def _s3(self):
        d = self.d
        self._shdr("3.    ANTECEDENTES MEDICOS Y DE VACUNACION")
        x = MARGIN
        vacunado = _get(d, 'vacunado', '').upper()
        antec_med = _get(d, 'antecedentes_medicos_sn', '').upper()

        h = RH
        y = self.y - h
        w1 = CONTENT_W * 0.36; w2 = CONTENT_W * 0.64
        self._rect(x, y, w1, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + (h - 5) / 2, 'Paciente Vacunado')
        cy = y + (h - CB) / 2
        cx = x + 55
        cx = self._cbl(cx, cy, _chk(vacunado), 'Si', font=F_CB_LBL, gap=2)
        cx = self._cbl(cx + 2, cy, _is_no(vacunado), 'No', font=F_CB_LBL, gap=4)
        self._cbl(cx + 2, cy, _is_desc(vacunado), 'Desconocido/Verbal', font=F_CB_LBL)

        self._rect(x + w1, y, w2, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(x + w1 + 1.5, y + (h - 5) / 2, 'Antecedentes medicos')
        cx = x + w1 + 75
        cx = self._cbl(cx, cy, _chk(antec_med), 'Si', font=F_CB_LBL, gap=4)
        cx = self._cbl(cx + 2, cy, _is_no(antec_med), 'No', font=F_CB_LBL, gap=8)
        self._cbl(cx + 2, cy, _is_desc(antec_med), 'Desconocido', font=F_CB_LBL)
        self.y -= h

        h = RH_SM
        y = self.y - h
        self._rect(x, y, CONTENT_W, h)
        antec = _get(d, 'antecedentes_medicos', '').upper()
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + (h - 5) / 2, 'Antecedentes Medicos')
        cy = y + (h - CB) / 2
        cx = x + 60
        self._sf(F_LBL_XS)
        self.c.drawString(cx, y + (h - 4) / 2, 'Especifique:')
        cx += 32
        cx = self._cbl(cx, cy, 'DESNUTRI' in antec, 'Desnutricion', font=F_CB_LBL, gap=4)
        cx = self._cbl(cx + 2, cy, 'INMUNO' in antec, 'Inmunocompromiso', font=F_CB_LBL, gap=4)
        self._cbl(cx + 2, cy, 'CRONIC' in antec, 'Enfermedad Cronica', font=F_CB_LBL)
        self.y -= h

        # Vaccine table
        fuente = _get(d, 'fuente_info_vacuna', '').upper()
        ct = CONTENT_W * 0.20; cd = CONTENT_W * 0.10; cf = CONTENT_W * 0.18; ci = CONTENT_W * 0.30; cs = CONTENT_W * 0.22

        h2 = RH_SM
        y = self.y - h2
        for w, lbl in [(ct, 'Tipo De Vacuna Recibida'), (cd, 'Numero De Dosis'), (cf, 'Fecha De La Ultima Dosis'), (ci, 'Fuente De La Informacion Sobre La Vacunacion'), (cs, 'Vacunacion En El Sector')]:
            self._cell_c(x, y, w, h2, lbl, font=F_BOLD5, bg=LIGHT_GRAY)
            x += w
        self.y -= h2
        x = MARGIN

        fuente_labels = ['Carne De Vacunacion', 'SIGSA 5a Cuaderno', 'SIGSA 5B Otros Grupos', 'Registro Unico De Vacunacion']
        sector_labels = ['MSPAS', 'IGSS', 'Privado']
        vr = RH_MD
        for vi, (vlbl, dk, fk) in enumerate([('SPR - Sarampion Paperas Rubeola', 'dosis_spr', 'fecha_spr'), ('SR - Sarampion Rubeola', 'dosis_sr', 'fecha_sr'), ('SPRV - Sarampion Paperas Rubeola Varicela', 'dosis_sprv', 'fecha_sprv')]):
            vy = self.y - vr
            cx2 = x
            self._cell_l(cx2, vy, ct, vr, vlbl, font=F_VAL_SM)
            cx2 += ct
            self._cell(cx2, vy, cd, vr, '', _get(d, dk), cv=True)
            cx2 += cd
            self._dcell(cx2, vy, cf, vr, '', _get(d, fk))
            cx2 += cf
            self._rect(cx2, vy, ci, vr)
            if vi == 0:
                for fi, fl in enumerate(fuente_labels):
                    self._sf(F_CB_SM)
                    self.c.setFillColor(black)
                    self.c.drawString(cx2 + 8, vy + vr - 7 - fi * 4.5, fl)
            cx2 += ci
            self._rect(cx2, vy, cs, vr)
            if vi == 0:
                for si, sl in enumerate(sector_labels):
                    self._sf(F_CB_SM)
                    self.c.setFillColor(black)
                    self.c.drawCentredString(cx2 + cs / 2, vy + vr - 7 - si * 5, sl)
            self.y -= vr

    # -- S4: DATOS CLINICOS --
    def _s4(self):
        d = self.d
        self._shdr("4.    DATOS CLINICOS")
        x = MARGIN

        h = RH_MD
        y = self.y - h
        w1 = CONTENT_W * 0.24; w2 = CONTENT_W * 0.22; w3 = CONTENT_W * 0.28; w4 = CONTENT_W - w1 - w2 - w3
        self._rect(x, y, w1, h)
        self._sf(F_LBL_XS)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + h - 5, 'Fecha de Inicio de Sintomas')
        self._dboxes(x + 2, y + 1.5, _get(d, 'fecha_inicio_sintomas'))

        self._rect(x + w1, y, w2, h)
        self._sf(F_LBL_XS)
        self.c.setFillColor(black)
        self.c.drawString(x + w1 + 1.5, y + h - 5, 'Fecha de Inicio de Fiebre')
        self._dboxes(x + w1 + 2, y + 1.5, _get(d, 'fecha_inicio_fiebre'))

        self._rect(x + w1 + w2, y, w3, h)
        self._sf(F_LBL_XS)
        self.c.setFillColor(black)
        self.c.drawString(x + w1 + w2 + 1.5, y + h - 5, 'Fecha de inicio de Exantema / Rash')
        self._dboxes(x + w1 + w2 + 2, y + 1.5, _get(d, 'fecha_inicio_erupcion'))

        self._dcell(x + w1 + w2 + w3, y, w4, h, '', '')
        self.y -= h

        # Signs table
        sl = [('Fiebre', 'signo_fiebre'), ('Exantema/ Rash', 'signo_erupcion'), ('Tos', 'signo_tos'), ('Conjuntivitis', 'signo_conjuntivitis')]
        sr = [('Coriza / Catarro', 'signo_coriza'), ('Manchas de Koplik', 'signo_koplik'), ('Artralgia / Artritis', 'signo_artralgia'), ('Adenopatias', 'signo_adenopatias')]
        h2 = RH_SM
        cw = CONTENT_W / 2
        wn2 = cw * 0.40; wsi = cw * 0.12; wno = cw * 0.12; wde = cw * 0.36
        for ri in range(4):
            y = self.y - h2
            for ci, signs in enumerate([sl, sr]):
                lbl, key = signs[ri]
                val = _get(d, key, '').upper()
                bx2 = x + ci * cw
                self._rect(bx2, y, wn2, h2)
                self._sf(F_VAL)
                self.c.setFillColor(black)
                self.c.drawString(bx2 + 1.5, y + (h2 - 5) / 2, _trunc(lbl, wn2 - 3, 2.8))
                self._rect(bx2 + wn2, y, wsi, h2)
                self._sf(F_CB_SM)
                self.c.drawString(bx2 + wn2 + 1, y + (h2 - 4) / 2, 'Si')
                self._cb(bx2 + wn2 + wsi - CB - 2, y + (h2 - CB) / 2, checked=val in ('SI', '1', 'TRUE', 'S', 'X'))
                self._rect(bx2 + wn2 + wsi, y, wno, h2)
                self._sf(F_CB_SM)
                self.c.drawString(bx2 + wn2 + wsi + 1, y + (h2 - 4) / 2, 'No')
                self._cb(bx2 + wn2 + wsi + wno - CB - 2, y + (h2 - CB) / 2, checked=val == 'NO')
                self._rect(bx2 + wn2 + wsi + wno, y, wde, h2)
                self._sf(F_CB_SM)
                self.c.drawString(bx2 + wn2 + wsi + wno + 1, y + (h2 - 4) / 2, 'Desconocido')
                self._cb(bx2 + wn2 + wsi + wno + wde - CB - 2, y + (h2 - CB) / 2, checked=val in ('DESCONOCIDO', 'DESC', 'NK', '?'))
            self.y -= h2

        # Hospitalizacion
        h = RH
        y = self.y - h
        hosp = _get(d, 'hospitalizado', '').upper()
        w_h1 = CONTENT_W * 0.18
        self._rect(x, y, w_h1, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + (h - 5) / 2, 'Hospitalizacion')
        cy = y + (h - CB) / 2
        cx2 = x + w_h1
        sw2 = CONTENT_W * 0.04
        self._rect(cx2, y, sw2, h)
        self._cbl(cx2 + 1, cy, _chk(hosp), 'Si', font=F_CB_SM)
        cx2 += sw2
        self._rect(cx2, y, sw2, h)
        self._cbl(cx2 + 1, cy, _is_no(hosp), 'No', font=F_CB_SM)
        cx2 += sw2
        wd2 = CONTENT_W * 0.10
        self._rect(cx2, y, wd2, h)
        self._cbl(cx2 + 1, cy, _is_desc(hosp), 'Desconocido', font=F_CB_SM)
        cx2 += wd2
        wh2 = CONTENT_W * 0.42
        self._cell(cx2, y, wh2, h, 'Nombre del Hospital', _get(d, 'hosp_nombre'))
        cx2 += wh2
        self._dcell(cx2, y, RIGHT - cx2, h, 'Fecha de Hospitalizacion', _get(d, 'hosp_fecha'))
        self.y -= h

        # Complicaciones
        h = RH
        y = self.y - h
        comp = _get(d, 'complicaciones', '').upper()
        dc = _get(d, 'descripcion_complicaciones', '').upper()
        w_c1 = CONTENT_W * 0.18
        self._rect(x, y, w_c1, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + (h - 5) / 2, 'Complicaciones')
        cy = y + (h - CB) / 2
        cx2 = x + w_c1
        sw2 = CONTENT_W * 0.04
        self._rect(cx2, y, sw2, h)
        self._cbl(cx2 + 1, cy, _chk(comp), 'Si', font=F_CB_SM)
        cx2 += sw2
        self._rect(cx2, y, sw2, h)
        self._cbl(cx2 + 1, cy, _is_no(comp), 'No', font=F_CB_SM)
        cx2 += sw2
        wd2 = CONTENT_W * 0.10
        self._rect(cx2, y, wd2, h)
        self._cbl(cx2 + 1, cy, _is_desc(comp), 'Desconocido', font=F_CB_SM)
        cx2 += wd2
        wca = RIGHT - cx2
        self._rect(cx2, y, wca, h)
        self._sf(F_LBL_XS)
        self.c.drawString(cx2 + 2, y + h - 5, 'Especifique Complicaciones')
        cc = cx2 + 45
        for clbl, ckw in [('Neumonia', 'NEUMON'), ('Encefalitis', 'ENCEFAL'), ('Diarrea', 'DIARREA'), ('Trombocitopenia', 'TROMBOCIT')]:
            cc = self._cbl(cc, cy, ckw in dc, clbl, font=F_CB_SM, gap=2)
            cc += 1
        self.y -= h

        h = RH_SM
        y = self.y - h
        self._rect(x, y, CONTENT_W, h)
        cy = y + (h - CB) / 2
        cx2 = x + CONTENT_W * 0.36
        cx2 = self._cbl(cx2, cy, 'OTITIS' in dc, 'Otitis Media Aguda', font=F_CB_SM, gap=5)
        cx2 = self._cbl(cx2 + 3, cy, 'CEGUERA' in dc, 'Ceguera', font=F_CB_SM, gap=5)
        self._sf(F_CB_SM)
        self.c.drawString(cx2 + 5, y + (h - 4) / 2, 'Otra (especifique)')
        self.y -= h

        # Aislamiento
        h = RH_MD
        y = self.y - h
        aisla = _get(d, 'aislamiento', '').upper()
        w_a1 = CONTENT_W * 0.18
        self._rect(x, y, w_a1, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + h - 6, 'Aislamiento')
        self.c.drawString(x + 1.5, y + h - 11, 'Respiratorio')
        cy = y + 3
        cx2 = x + w_a1
        sw2 = CONTENT_W * 0.04
        self._rect(cx2, y, sw2, h)
        self._cbl(cx2 + 1, cy, _chk(aisla), 'Si', font=F_CB_SM)
        cx2 += sw2
        wd2 = CONTENT_W * 0.18
        self._dcell(cx2, y, wd2, h, '', _get(d, 'fecha_aislamiento'))
        cx2 += wd2
        wno2 = CONTENT_W * 0.06
        self._rect(cx2, y, wno2, h)
        self._cbl(cx2 + 1, cy, _is_no(aisla), 'No', font=F_CB_SM)
        cx2 += wno2
        wde2 = CONTENT_W * 0.10
        self._rect(cx2, y, wde2, h)
        self._cbl(cx2 + 1, cy, _is_desc(aisla), 'Desconocido', font=F_CB_SM)
        cx2 += wde2
        wr = RIGHT - cx2
        if wr > 0:
            self._rect(cx2, y, wr, h)
        self.y -= h

    # -----------------------------------------------------------------------
    # PAGE 2
    # -----------------------------------------------------------------------

    def draw_page2(self):
        self.y = PAGE_H - MARGIN
        self._s5()
        self._s6()
        self._s7()
        self._s8()

    # -- S5: FACTORES DE RIESGO --
    def _s5(self):
        d = self.d
        self._shdr("5.    FACTORES DE RIESGO")
        x = MARGIN
        wq = CONTENT_W * 0.58; ws = CONTENT_W * 0.08; wn = CONTENT_W * 0.08; wd = CONTENT_W * 0.26

        def _fr(text, vk):
            h = RH
            yr = self.y - h
            val = _get(d, vk, '').upper()
            self._rect(x, yr, wq, h)
            self._sf(F_VAL)
            self.c.setFillColor(black)
            self.c.drawString(x + 1.5, yr + (h - 5) / 2, _trunc(text, wq - 3, 2.8))
            cy = yr + (h - CB) / 2
            self._cell_c(x + wq, yr, ws, h, 'Si', font=F_CB_SM)
            self._cb(x + wq + ws - CB - 2, cy, checked=_chk(val))
            self._cell_c(x + wq + ws, yr, wn, h, 'No', font=F_CB_SM)
            self._cb(x + wq + ws + wn - CB - 2, cy, checked=_is_no(val))
            self._cell_c(x + wq + ws + wn, yr, wd, h, 'Desconocido', font=F_CB_SM)
            self._cb(x + wq + ws + wn + wd - CB - 2, cy, checked=_is_desc(val))
            self.y -= h

        _fr('Existe algun caso confirmado en la comunidad o municipio de residencia', 'caso_confirmado_comunidad_3m')
        _fr('Tuvo contacto con un caso sospechoso o confirmado entre 7-23 dias antes del inicio del exantema/rash', 'contacto_sospechoso_7_23')

        h = RH
        y = self.y - h
        viajo = _get(d, 'viajo_previo', '').upper()
        wvq = CONTENT_W * 0.42
        self._rect(x, y, wvq, h)
        self._sf(F_VAL)
        self.c.setFillColor(black)
        self.c.drawString(x + 5, y + (h - 5) / 2, 'Viajo durante los 7-23 dias previos al inicio del')
        cy = y + (h - CB) / 2
        sw2 = CONTENT_W * 0.04
        self._rect(x + wvq, y, sw2, h)
        self._cbl(x + wvq + 1, cy, _chk(viajo), 'Si', font=F_CB_SM)
        wp2 = CONTENT_W - wvq - sw2
        self._cell(x + wvq + sw2, y, wp2, h, 'Pais, Departamento y Municipio', _get(d, 'lugar_viaje'))
        self._sf(F_CB_SM)
        self.c.drawString(RIGHT - 15, y + (h - 4) / 2, 'No')
        self._cb(RIGHT - CB - 2, cy, checked=_is_no(viajo))
        self.y -= h

        h = RH_MD
        y = self.y - h
        wfs = CONTENT_W * 0.20; wfe = CONTENT_W * 0.20; wex = CONTENT_W * 0.30; wfr = CONTENT_W * 0.30
        self._rect(x, y, wfs, h)
        self._sf(F_LBL_XS)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + h - 5, 'Fecha de Salida')
        self._dboxes(x + 2, y + 1.5, _get(d, 'fecha_inicio_viaje'))
        self._rect(x + wfs, y, wfe, h)
        self._sf(F_LBL_XS)
        self.c.drawString(x + wfs + 1.5, y + h - 5, 'Fecha de Entrada')
        self._dboxes(x + wfs + 2, y + 1.5, _get(d, 'fecha_fin_viaje'))
        rx = x + wfs + wfe
        ev = _get(d, 'persona_viajo_exterior', '').upper()
        self._rect(rx, y, wex, h)
        self._sf(F_VAL_SM)
        self.c.setFillColor(black)
        self.c.drawString(rx + 1.5, y + h - 6, 'Alguna persona de su casa ha viajado al exterior?')
        self._cbl(rx + 2, y + 2, _chk(ev), 'Si', font=F_CB_SM, gap=3)
        rx2 = x + wfs + wfe + wex
        self._rect(rx2, y, wfr, h)
        self._sf(F_LBL_XS)
        self.c.drawString(rx2 + 1.5, y + h - 5, 'Fecha de Retorno')
        self._dboxes(rx2 + 2, y + 1.5, _get(d, 'fecha_retorno'))
        self._sf(F_CB_SM)
        self.c.drawString(RIGHT - 15, y + 2, 'No')
        self._cb(RIGHT - CB - 2, y + 2, checked=_is_no(ev))
        self.y -= h

        h = RH
        y = self.y - h
        ec = _get(d, 'contacto_embarazada', '').upper()
        self._rect(x, y, CONTENT_W * 0.58, h)
        self._sf(F_VAL)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + (h - 5) / 2, 'El Paciente Estuvo En Contacto Con Una Mujer Embarazada?')
        cy = y + (h - CB) / 2
        cx2 = x + CONTENT_W * 0.58
        sw3 = CONTENT_W * 0.08
        self._rect(cx2, y, sw3, h)
        self._cbl(cx2 + 1, cy, _chk(ec), 'Si', font=F_CB_SM)
        cx2 += sw3
        self._rect(cx2, y, sw3, h)
        self._cbl(cx2 + 1, cy, _is_no(ec), 'No', font=F_CB_SM)
        cx2 += sw3
        self._rect(cx2, y, RIGHT - cx2, h)
        self._cbl(cx2 + 1, cy, _is_desc(ec), 'Desconocido', font=F_CB_SM)
        self.y -= h

        h = RH_LG
        y = self.y - h
        self._rect(x, y, CONTENT_W, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + h - 7, 'Fuente Posible de Contagio')
        fc = _get(d, 'fuente_contagio', '').upper()
        c1 = [('Contacto en el hogar', 'HOGAR'), ('Servicio de Salud', 'SERVICIO'), ('Institucion Educativa', 'EDUCATIVA'), ('Espacio Publico', 'PUBLICO'), ('Comunidad', 'COMUNIDAD')]
        c2 = [('Evento Masivo', 'MASIVO'), ('Transporte Internacional', 'TRANSPORTE'), ('Desconocido', 'DESCONOCIDO'), ('Otro', 'OTRO')]
        cy1 = y + h - 10
        cx2 = x + 30
        for lbl, kw in c1:
            cx2 = self._cbl(cx2, cy1, kw in fc, lbl, font=F_CB_SM, gap=3)
            cx2 += 3
        cy2 = y + 3
        cx2 = x + 30
        for lbl, kw in c2:
            cx2 = self._cbl(cx2, cy2, kw in fc, lbl, font=F_CB_SM, gap=3)
            cx2 += 3
        self._sf(F_CB_SM)
        self.c.drawString(cx2 + 3, cy2 + 0.5, '(especifique)')
        self.y -= h

    # -- S6: ACCIONES DE RESPUESTA --
    def _s6(self):
        d = self.d
        self._shdr("6.    ACCIONES DE RESPUESTA")
        x = MARGIN
        acciones = [
            ('Se realizo busqueda activa institucional de casos (BAI)?', 'accion_bai', 'Numero de casos sospechosos identificados en BAI', 'num_bai'),
            ('Se realizo busqueda activa comunitaria de casos (BAC)?', 'accion_bac', 'Numero de casos sospechosos identificados en BAC', 'num_bac'),
            ('Hubo vacunacion de bloqueo en las primeras 48 a 72hrs?', 'accion_vacunacion', 'Se realizo monitoreo rapido de vacunacion?', 'accion_monitoreo'),
            ('Hubo vacunacion con barrido documentado?', 'accion_barrido', '', ''),
            ('Se le administro vitamina A?', 'accion_vitamina_a', 'Numero de dosis de vitamina A recibidas (1,2,3,4 o mas, 99 Desconocido)', 'num_vitamina_a'),
        ]
        for texto, ka, rt, rk in acciones:
            h = RH
            y = self.y - h
            val = _get(d, ka, '').upper()
            wq = CONTENT_W * 0.38
            self._cell_l(x, y, wq, h, texto, font=F_VAL_SM)
            cy = y + (h - CB) / 2
            sw2 = CONTENT_W * 0.06
            cx2 = x + wq
            self._rect(cx2, y, sw2, h)
            self._cbl(cx2 + 1, cy, _chk(val), 'Si', font=F_CB_SM)
            cx2 += sw2
            self._rect(cx2, y, sw2, h)
            self._cbl(cx2 + 1, cy, _is_no(val), 'No', font=F_CB_SM)
            cx2 += sw2
            wr = RIGHT - cx2
            if rt:
                self._cell(cx2, y, wr, h, rt, _get(d, rk) if rk else '', fl=F_VAL_4, fv=F_VAL_SM)
                if 'monitoreo' in rt.lower():
                    mv = _get(d, 'accion_monitoreo', '').upper()
                    mc = RIGHT - 35
                    self._cbl(mc, cy, _chk(mv), 'Si', font=F_CB_SM, gap=2)
                    self._cbl(mc + 18, cy, _is_no(mv), 'No', font=F_CB_SM)
            else:
                self._rect(cx2, y, wr, h)
            self.y -= h

    # -- S7: LABORATORIO --
    def _s7(self):
        d = self.d
        self._parse_lab()
        self._shdr("7.    LABORATORIO")
        x = MARGIN

        h = RH
        y = self.y - h
        w1 = CONTENT_W * 0.45; w2 = CONTENT_W * 0.55
        self._rect(x, y, w1, h)
        self._sf(F_LBL)
        self.c.setFillColor(black)
        self.c.drawString(x + 1.5, y + (h - 5) / 2, 'Tipo de Muestra')
        tm = _get(d, 'tipo_muestra', '').upper()
        cy = y + (h - CB) / 2
        cx2 = x + 55
        cx2 = self._cbl(cx2, cy, 'SUERO' in tm, 'Suero', font=F_CB_LBL, gap=3)
        cx2 = self._cbl(cx2 + 2, cy, 'ORINA' in tm, 'Orina', font=F_CB_LBL, gap=3)
        self._cbl(cx2 + 2, cy, 'HISOPADO' in tm or 'NASO' in tm, 'Hisopado Nasofaringeo', font=F_CB_LBL)
        self._cell(x + w1, y, w2, h, 'Por que no se recolecto las 3 muestra de laboratorio?', _get(d, 'motivo_no_recoleccion'))
        self.y -= h

        self._s7_matrix()

        h = RH_SM
        y = self.y - h
        self._rect(x, y, CONTENT_W, h)
        self._sf(F_NOTE)
        self.c.setFillColor(black)
        self.c.drawString(x + 2, y + (h - 4) / 2, '* RESULTADOS 0 = Negativo, 1 = Positivo, 2 = Muestra inadecuada, 3= Indeterminado, 4 = No fue procesada, 5 = Alta, 6 = Baja')
        self.y -= h

    def _parse_lab(self):
        import json as _json
        d = self.d
        lj = _get(d, 'lab_muestras_json')
        if not lj:
            return
        try:
            samples = _json.loads(lj)
            if not isinstance(samples, list):
                return
            sm = {'suero_1': 'suero1', 'suero_2': 'suero2', 'orina_1': 'orina1', 'hisopado_1': 'hisopado1', 'otro': 'otra'}
            for s in samples:
                slot = s.get('slot', '')
                pfx = sm.get(slot)
                if not pfx:
                    continue
                for k in ['fecha_toma', 'fecha_envio', 'fecha_resultado']:
                    if s.get(k):
                        d[f'muestra_{pfx}_{k.split("_", 1)[1] if "_" in k else k}'] = s[k]
                for virus, vs in [('sarampion', 'sar'), ('rubeola', 'rub')]:
                    for t in ['igm', 'igg']:
                        v = s.get(f'{virus}_{t}', '')
                        if v:
                            d[f'{pfx}_{vs}_{t}'] = v
                    va = s.get(f'{virus}_avidez', '')
                    if va:
                        d[f'{pfx}_{vs}_av'] = va
                if s.get('secuenciacion_genotipo'):
                    d[f'{pfx}_secuencia'] = s['secuenciacion_genotipo']
        except Exception:
            pass

    def _s7_matrix(self):
        d = self.d
        x = MARGIN
        cn = CONTENT_W * 0.04; ct = CONTENT_W * 0.09; cft = CONTENT_W * 0.12; cfe = CONTENT_W * 0.12
        cr = CONTENT_W * 0.045; cs = cr * 3; crb = cr * 3; cfr = CONTENT_W * 0.14; csr = CONTENT_W * 0.09
        csf = CONTENT_W - (cn + ct + cft + cfe + cs + crb + cfr + csr)

        hg = RH_SM
        y = self.y - hg
        cx2 = x
        for w in [cn, ct, cft, cfe]:
            self._rect(cx2, y, w, hg)
            cx2 += w
        self._fill_rect(cx2, y, cs, hg, SECTION_BG)
        self.c.setFillColor(white)
        self._sf(F_BOLD5)
        self.c.drawCentredString(cx2 + cs / 2, y + (hg - 5) / 2, 'Sarampion')
        self.c.setFillColor(black)
        cx2 += cs
        self._fill_rect(cx2, y, crb, hg, SECTION_BG)
        self.c.setFillColor(white)
        self._sf(F_BOLD5)
        self.c.drawCentredString(cx2 + crb / 2, y + (hg - 5) / 2, 'Rubeola')
        self.c.setFillColor(black)
        cx2 += crb
        self._rect(cx2, y, cfr, hg)
        cx2 += cfr
        self._fill_rect(cx2, y, csr + csf, hg, LIGHT_GRAY)
        self._sf(F_BOLD5)
        self.c.drawCentredString(cx2 + (csr + csf) / 2, y + (hg - 5) / 2, 'Secuenciacion')
        self.y -= hg

        hs = RH_SM + 2
        y = self.y - hs
        cx2 = x
        for w, lbl in [(cn, 'No. Muestra'), (ct, 'Tipo Muestra y Prueba'), (cft, 'Fecha de Toma'), (cfe, 'Fecha de Envio')]:
            self._cell_c(cx2, y, w, hs, lbl, font=F_VAL_4, bg=LIGHT_GRAY)
            cx2 += w
        for lbl in ['IgM', 'IgG', 'Avidez']:
            self._cell_c(cx2, y, cr, hs, lbl, font=F_VAL_4, bg=LIGHT_GRAY)
            cx2 += cr
        for lbl in ['IgM', 'IgG', 'Avidez']:
            self._cell_c(cx2, y, cr, hs, lbl, font=F_VAL_4, bg=LIGHT_GRAY)
            cx2 += cr
        self._cell_c(cx2, y, cfr, hs, 'Dia  Mes  Ano', font=F_VAL_4, bg=LIGHT_GRAY)
        cx2 += cfr
        self._cell_c(cx2, y, csr, hs, 'Resultado', font=F_VAL_4, bg=LIGHT_GRAY)
        cx2 += csr
        self._cell_c(cx2, y, csf, hs, 'Fecha', font=F_VAL_4, bg=LIGHT_GRAY)
        self.y -= hs

        muestras = [('1a', 'Suero (Anticuerpo)', 'suero1'), ('2da', 'Suero (Anticuerpo)', 'suero2'), ('1a', 'Orina (ARN viral)', 'orina1'), ('1a', 'Hisopado Nasofaringeo (ARN viral)', 'hisopado1'), ('Otro', '', 'otra')]
        sh = RH_XS
        for mno, mtp, pfx in muestras:
            th = sh * 2
            yt = self.y - th
            cx2 = x
            self._cell_c(cx2, yt, cn, th, mno, font=F_VAL_XS)
            cx2 += cn
            self._cell_c(cx2, yt, ct, th, mtp, font=F_VAL_4)
            cx2 += ct
            ft2 = _get(d, f'muestra_{pfx}_fecha', '')
            self._rect(cx2, yt, cft, th)
            if ft2:
                self._dboxes(cx2 + 1, yt + (th - DB) / 2, ft2, labels=False)
            cx2 += cft
            fe2 = _get(d, f'muestra_{pfx}_fecha_envio', '')
            self._rect(cx2, yt, cfe, th)
            if fe2:
                self._dboxes(cx2 + 1, yt + (th - DB) / 2, fe2, labels=False)
            cx2 += cfe
            for vi, (vl, vs) in enumerate([('Sarampion', 'sar'), ('Rubeola', 'rub')]):
                vy = yt + (1 - vi) * sh
                for ri, test in enumerate(['igm', 'igg', 'av']):
                    vk = f'{pfx}_{vs}_{test}'
                    val = _get(d, vk, '')
                    rx2 = cx2 + ri * cr + (0 if vs == 'sar' else cs)
                    self._cell_c(rx2, vy, cr, sh, val, font=F_VAL_XS)
            rx3 = cx2 + cs + crb
            self._rect(rx3, yt, cfr, th)
            fres = _get(d, f'{pfx}_fecha_resultado', '')
            if fres:
                self._dboxes(rx3 + 1, yt + (th - DB) / 2, fres, labels=False)
            sx2 = rx3 + cfr
            sv = _get(d, f'{pfx}_secuencia', '')
            self._cell_c(sx2, yt, csr, th, sv, font=F_VAL_XS)
            self._rect(sx2 + csr, yt, csf, th)
            self.y -= th

    # -- S8: CLASIFICACION --
    def _s8(self):
        d = self.d
        self._shdr("8.    CLASIFICACION")
        x = MARGIN
        clasif = _get(d, 'clasificacion_caso', '').upper()
        cconf = _get(d, 'criterio_clasificacion', '').upper()
        cdesc = _get(d, 'criterio_descarte', '').upper()
        finf = _get(d, 'fuente_infeccion', '').upper()

        h = RH
        y = self.y - h
        wl = CONTENT_W * 0.15
        self._cell_l(x, y, wl, h, 'Clasificacion Final', font=F_LBL)
        cx2 = x + wl
        cy = y + (h - CB) / 2
        for lbl, kw in [('Sarampion', 'SARAMP'), ('Rubeola', 'RUBEO'), ('Descartado', 'DESCART'), ('Pendiente', 'PENDIENTE'), ('No cumple con la definicion de caso', 'NO CUMPLE')]:
            wi = (CONTENT_W - wl) / 5
            self._rect(cx2, y, wi, h)
            self._cbl(cx2 + 2, cy, kw in clasif, lbl, font=F_CB_SM, gap=1)
            cx2 += wi
        self.y -= h

        h = RH
        y = self.y - h
        self._cell_l(x, y, wl, h, 'Criterio de Confirmacion', font=F_LBL)
        cx2 = x + wl
        cy = y + (h - CB) / 2
        for lbl, kw, w in [('Laboratorio', 'LAB', 0.15), ('Nexo epidemiologico', 'NEXO', 0.20), ('Clinico', 'CLINICO', 0.12)]:
            w2 = CONTENT_W * w
            self._rect(cx2, y, w2, h)
            self._cbl(cx2 + 2, cy, kw in cconf, lbl, font=F_CB_SM)
            cx2 += w2
        wr2 = RIGHT - cx2
        self._rect(cx2, y, wr2, h)
        co = _get(d, 'contacto_otro_caso', '').upper()
        self._sf(F_LBL_XS)
        self.c.drawString(cx2 + 2, y + h - 5, 'Contacto de Otro Caso')
        self._cbl(cx2 + 60, cy, _chk(co), 'Si', font=F_CB_SM, gap=3)
        self._cbl(cx2 + 80, cy, _is_no(co), 'No', font=F_CB_SM)
        self.y -= h

        h = RH
        y = self.y - h
        self._cell_l(x, y, wl, h, 'Criterio para descartar', font=F_LBL)
        cx2 = x + wl
        cy = y + (h - CB) / 2
        for lbl, kw, w in [('Laboratorial', 'LAB', 0.15), ('Relacionado con la Vacuna', 'VACUNA', 0.25), ('Clinico', 'CLINICO', 0.12)]:
            w2 = CONTENT_W * w
            self._rect(cx2, y, w2, h)
            self._cbl(cx2 + 2, cy, kw in cdesc, lbl, font=F_CB_SM)
            cx2 += w2
        self._rect(cx2, y, RIGHT - cx2, h)
        self.y -= h

        h = RH
        y = self.y - h
        self._cell_l(x, y, wl, h, 'Fuente de infeccion de los casos confirmados', font=F_LBL_XS)
        cx2 = x + wl
        cy = y + (h - CB) / 2
        for lbl, kw, w in [('Importado', 'IMPORTADO', 0.12), ('Relacionado con la importacion', 'RELACIONADO', 0.18)]:
            w2 = CONTENT_W * w
            self._rect(cx2, y, w2, h)
            self._cbl(cx2 + 2, cy, kw in finf, lbl, font=F_CB_SM)
            cx2 += w2
        w3 = CONTENT_W * 0.18
        self._cell(cx2, y, w3, h, 'Pais de Importacion', _get(d, 'pais_importacion'))
        cx2 += w3
        for lbl, kw, w in [('Endemico', 'ENDEMICO', 0.13)]:
            w2 = CONTENT_W * w
            self._rect(cx2, y, w2, h)
            self._cbl(cx2 + 2, cy, kw in finf, lbl, font=F_CB_SM)
            cx2 += w2
        wr2 = RIGHT - cx2
        self._rect(cx2, y, wr2, h)
        self._cbl(cx2 + 2, cy, 'DESCONOCIDA' in finf, 'Fuente desconocida', font=F_CB_SM)
        self.y -= h

        h = RH
        y = self.y - h
        self._cell_l(x, y, wl, h, 'Caso Analizado Por', font=F_LBL)
        cx2 = x + wl
        cy = y + (h - CB) / 2
        anal = _get(d, 'responsable_clasificacion', '').upper()
        for lbl, kw, w in [('CONAPI', 'CONAPI', 0.10), ('DEGR*', 'DEGR', 0.12), ('Comision Nacional**', 'COMISION', 0.18), ('Otros', 'OTRO', 0.10)]:
            w2 = CONTENT_W * w
            self._rect(cx2, y, w2, h)
            self._cbl(cx2 + 2, cy, kw in anal, lbl, font=F_CB_SM)
            cx2 += w2
        self._cell(cx2, y, RIGHT - cx2, h, 'Especifique', _get(d, 'especifique_analizado'))
        self.y -= h

        h = RH_MD
        y = self.y - h
        wfc = CONTENT_W * 0.30
        self._dcell(x, y, wfc, h, 'Fecha de Clasificacion', _get(d, 'fecha_clasificacion'))
        cx2 = x + wfc
        cond = _get(d, 'condicion_final', '').upper()
        wcl = CONTENT_W * 0.14
        self._cell_l(cx2, y, wcl, h, 'Condicion Final del Paciente', font=F_LBL_XS)
        cx2 += wcl
        cy = y + (h - CB) / 2
        for lbl, kw, w in [('Recuperado', 'RECUPERADO', 0.12), ('Con Secuelas', 'SECUELA', 0.12), ('Fallecido*', 'FALLEC', 0.12), ('Desconocido', 'DESC', 0.20)]:
            w2 = CONTENT_W * w
            if cx2 + w2 > RIGHT:
                w2 = RIGHT - cx2
            if w2 <= 0:
                break
            self._rect(cx2, y, w2, h)
            self._cbl(cx2 + 2, cy, kw in cond, lbl, font=F_CB_SM)
            cx2 += w2
        self.y -= h

        h = RH_MD
        y = self.y - h
        wfd = CONTENT_W * 0.22
        self._dcell(x, y, wfd, h, 'Fecha de Defuncion*', _get(d, 'fecha_defuncion'))
        wcml = CONTENT_W * 0.18
        self._cell_l(x + wfd, y, wcml, h, 'Causa De Muerte Segun Certificado De Defuncion', font=F_LBL_XS)
        self._cell(x + wfd + wcml, y, RIGHT - x - wfd - wcml, h, '', _get(d, 'causa_muerte'))
        self.y -= h

        h = 30
        y = self.y - h
        if y >= MARGIN:
            self._cell(x, y, CONTENT_W, h, 'Observaciones', _get(d, 'observaciones'))
            self.y -= h

        yn = MARGIN + 10
        if self.y > yn + 10:
            self._sf(F_NOTE2)
            self.c.setFillColor(black)
            self.c.drawString(MARGIN, yn + 5, '* Direccion de Epidemiologia y Gestion del Riesgo')
            self.c.drawString(MARGIN, yn, '* Comision Nacional para verificar la interrupcion de la transmision endemica Sarampion, Rubeola y Sindrome de Rubeola congenita.')


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generar_ficha_v2_pdf(data):
    """Genera PDF de ficha epidemiologica formato MSPAS 2026 (GoData)."""
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=LETTER)
    c.setTitle("Ficha Epidemiologica Sarampion/Rubeola - MSPAS 2026")
    c.setAuthor("IGSS Epidemiologia")
    c.setSubject("Version 2026")
    builder = FichaV2Builder(c, data)
    builder.draw_page1()
    c.showPage()
    builder.draw_page2()
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


def generar_fichas_v2_bulk(records, merge=True):
    """Genera multiples fichas v2. merge=True -> 1 PDF, merge=False -> ZIP."""
    if not records:
        raise ValueError("No se proporcionaron registros")
    if merge:
        buf = io.BytesIO()
        c = Canvas(buf, pagesize=LETTER)
        c.setTitle("Fichas Epidemiologicas Sarampion/Rubeola - MSPAS 2026")
        c.setAuthor("IGSS Epidemiologia")
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
        zb = io.BytesIO()
        with zipfile.ZipFile(zb, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, data in enumerate(records):
                pb = generar_ficha_v2_pdf(data)
                nm = _get(data, 'nombres', 'caso')
                ap = _get(data, 'apellidos', '')
                fn2 = f"{i + 1:03d}_{nm}_{ap}.pdf".replace(' ', '_')
                zf.writestr(fn2, pb)
        zb.seek(0)
        return zb.read()


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

def _test():
    sample = {
        'diagnostico_registrado': 'B05 - Sarampion',
        'numero_caso': '2026-GT-0042',
        'codigo_caso': 'GT-SAR-2026-042',
        'area_salud': 'Guatemala Central',
        'folio': '0042',
        'fecha_notificacion': '2026-03-15',
        'fecha_consulta': '2026-03-14',
        'fecha_investigacion_domiciliaria': '2026-03-16',
        'distrito': 'Guatemala Sur',
        'unidad_medica': 'Hospital General IGSS Zona 9',
        'investigador': 'Dr. Carlos Mendez',
        'cargo_investigador': 'Epidemiologo',
        'telefono_investigador': '5555-1234 / cmendez@igss.gob.gt',
        'tipo_establecimiento': 'IGSS',
        'fuente_notificacion': 'Servicio de Salud',
        'nombres': 'Maria Isabel',
        'apellidos': 'Lopez Hernandez',
        'sexo': 'F',
        'fecha_nacimiento': '1995-06-20',
        'edad_anios': '30',
        'edad_meses': '9',
        'edad_dias': '5',
        'afiliacion': '1234567890101',
        'nombre_encargado': 'Juan Lopez',
        'parentesco_tutor': 'Padre',
        'dpi_tutor': '9876543210101',
        'pueblo_etnia': 'Ladino',
        'extranjero': 'No',
        'migrante': 'No',
        'esta_embarazada': 'No',
        'ocupacion': 'Maestra',
        'escolaridad': 'Universitaria',
        'telefono_paciente': '5555-9876',
        'pais_residencia': 'Guatemala',
        'departamento_residencia': 'Guatemala',
        'municipio_residencia': 'Guatemala',
        'direccion_exacta': '12 Calle 5-20 Zona 1',
        'poblado': 'Centro',
        'vacunado': 'Si',
        'antecedentes_medicos_sn': 'No',
        'dosis_spr': '2',
        'fecha_spr': '2000-01-15',
        'fuente_info_vacuna': 'Carne',
        'fecha_inicio_sintomas': '2026-03-10',
        'fecha_inicio_fiebre': '2026-03-10',
        'fecha_inicio_erupcion': '2026-03-12',
        'signo_fiebre': 'Si',
        'signo_erupcion': 'Si',
        'signo_tos': 'Si',
        'signo_conjuntivitis': 'No',
        'signo_coriza': 'Si',
        'signo_koplik': 'Desconocido',
        'signo_artralgia': 'No',
        'signo_adenopatias': 'No',
        'temperatura_celsius': '38.5',
        'hospitalizado': 'Si',
        'hosp_nombre': 'Hospital General IGSS Zona 9',
        'hosp_fecha': '2026-03-14',
        'complicaciones': 'No',
        'aislamiento': 'Si',
        'fecha_aislamiento': '2026-03-14',
        'caso_confirmado_comunidad_3m': 'No',
        'contacto_sospechoso_7_23': 'Si',
        'viajo_previo': 'No',
        'contacto_embarazada': 'No',
        'fuente_contagio': 'Servicio de Salud',
        'accion_bai': 'Si',
        'accion_bac': 'Si',
        'accion_vacunacion': 'Si',
        'accion_monitoreo': 'Si',
        'accion_barrido': 'No',
        'accion_vitamina_a': 'No',
        'tipo_muestra': 'Suero, Orina',
        'muestra_suero1_fecha': '2026-03-14',
        'suero1_sar_igm': '1',
        'suero1_sar_igg': '0',
        'suero1_rub_igm': '0',
        'suero1_rub_igg': '0',
        'clasificacion_caso': 'Pendiente',
        'condicion_final': 'Recuperado',
        'observaciones': 'Caso en seguimiento epidemiologico.',
    }
    pdf_bytes = generar_ficha_v2_pdf(sample)
    out_path = '/tmp/ficha_v2_test.pdf'
    with open(out_path, 'wb') as f:
        f.write(pdf_bytes)
    print(f"PDF generado: {out_path} ({len(pdf_bytes):,} bytes)")
    return out_path


if __name__ == '__main__':
    _test()
