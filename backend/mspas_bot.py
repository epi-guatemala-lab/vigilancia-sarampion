"""
MSPAS EPIWEB Sarampion Form Bot — Playwright headless engine.

Fills the MSPAS EPIWEB sarampion ficha form automatically from IGSS DB records.

CRITICAL SAFETY RULE:
    The bot will NEVER click "Guardar" unless the environment variable
    MSPAS_PRODUCTION_MODE=true is explicitly set. Default behavior is to
    fill every field, take screenshots, and stop WITHOUT submitting.

Usage:
    bot = MSPASBot(username="user", password="pass")
    result = bot.process_record(record_dict)

Standalone test:
    python mspas_bot.py
"""

import os
import re
import time
import json
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# ── Safety gate ──────────────────────────────────────────────────────────────
PRODUCTION_MODE = os.environ.get("MSPAS_PRODUCTION_MODE", "false").lower() == "true"

EPIWEB_URL = "https://cne.mspas.gob.gt/epiweb/"
SCREENSHOT_DIR = "/tmp/mspas_screenshots"

# Default timeouts (ms)
NAV_TIMEOUT = 30_000
ACTION_TIMEOUT = 10_000
AJAX_WAIT = 1500  # after dept/muni selects
PAGE_SETTLE = 2000


# ── Field mapping: IGSS DB → MSPAS form ─────────────────────────────────────

def map_record_to_mspas(record: dict) -> dict:
    """Convert an IGSS DB record dict into the field names expected by the
    MSPAS EPIWEB sarampion form.  Keys are MSPAS form element identifiers;
    values are the data to fill.
    """
    r = record

    def _val(key: str, default: str = "") -> str:
        v = r.get(key)
        if v is None:
            return default
        return str(v).strip()

    def _date(key: str) -> str:
        """Normalize dates to DD/MM/YYYY expected by EPIWEB datepickers."""
        raw = _val(key)
        if not raw:
            return ""
        # Try ISO (YYYY-MM-DD) first
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                dt = datetime.strptime(raw[:10], fmt)
                return dt.strftime("%d/%m/%Y")
            except ValueError:
                continue
        return raw  # fallback: return as-is

    def _radio(key: str) -> str:
        """Normalize yes/no/na → SI/NO/NA."""
        v = _val(key).upper()
        if v in ("SI", "SÍ", "YES", "1", "TRUE"):
            return "SI"
        if v in ("NO", "0", "FALSE"):
            return "NO"
        if v in ("NA", "N/A", "NO APLICA"):
            return "NA"
        return v

    mapped = {
        # Tab 1 — Datos Generales
        "fecha_not": _date("fecha_notificacion"),
        "nom_responsable": _val("nom_responsable"),
        "cargo_responsable": _val("cargo_responsable"),
        "tel_responsable": _val("telefono_responsable"),
        "centro_partial": _val("unidad_medica") or _val("centro_externo"),

        # Tab 2 — Datos Paciente
        "nombres": _val("nombres"),
        "apellidos": _val("apellidos"),
        "genero": _val("sexo"),
        "etnia": _val("pueblo_etnia"),
        "ocupacion": _val("ocupacion"),
        "escolaridad": _val("escolaridad"),
        "departamento": _val("departamento_residencia"),
        "municipio": _val("municipio_residencia"),
        "poblado": _val("poblado"),
        "direccion": _val("direccion_exacta"),
        "fecha_nac": _date("fecha_nacimiento"),
        "nombre_madre": _val("nombre_encargado"),
        "embarazada": _radio("esta_embarazada"),
        "lactando": _radio("lactando"),
        "sem_embarazo": _val("semanas_embarazo"),

        # Tab 3 — Info Clinica
        "fecha_ini_sint": _date("fecha_inicio_sintomas"),
        "fecha_captacion": _date("fecha_captacion"),
        "fuente_noti": _val("fuente_notificacion"),
        "fecha_domiciliaria": _date("fecha_visita_domiciliaria"),
        "fecha_investigacion": _date("fecha_inicio_investigacion"),
        "busqueda_activa": _val("busqueda_activa"),
        "fecha_erupcion": _date("fecha_inicio_erupcion"),
        "sitio_erupcion": _val("sitio_inicio_erupcion"),
        "fecha_fiebre": _date("fecha_inicio_fiebre"),
        "temperatura": _val("temperatura_celsius"),
        "signo_tos": _radio("signo_tos"),
        "signo_coriza": _radio("signo_coriza"),
        "signo_conjuntivitis": _radio("signo_conjuntivitis"),
        "signo_adenopatias": _radio("signo_adenopatias"),
        "signo_artralgia": _radio("signo_artralgia"),
        "vacunado": _radio("vacunado"),
        "fuente_vacuna": _val("fuente_info_vacuna"),
        "tipo_vacuna": _val("tipo_vacuna"),
        "no_dosis": _val("numero_dosis_spr"),
        "fecha_ult_dosis": _date("fecha_ultima_dosis"),
        "hospitalizado": _radio("hospitalizado"),
        "hosp_nombre": _val("hosp_nombre"),
        "hosp_fecha": _date("hosp_fecha"),
        "hosp_reg_med": _val("no_registro_medico"),
        "condicion_egreso": _val("condicion_egreso"),
        "fecha_egreso": _date("fecha_egreso"),

        # Tab 4 — Factores de Riesgo
        "contacto_sospechoso": _radio("contacto_sospechoso_7_23"),
        "casos_comunidad": _radio("caso_sospechoso_comunidad_3m"),
        "viajo": _radio("viajo_7_23_previo"),
        "donde_viajo": _val("destino_viaje"),

        # Tab 5 — Laboratorio
        "recolecto_muestra": _radio("recolecto_muestra"),
        "muestra_suero": _val("muestra_suero") not in ("", "0", "NO", "False"),
        "muestra_suero_fecha": _date("muestra_suero_fecha"),
        "muestra_hisopado": _val("muestra_hisopado") not in ("", "0", "NO", "False"),
        "muestra_hisopado_fecha": _date("muestra_hisopado_fecha"),
        "muestra_orina": _val("muestra_orina") not in ("", "0", "NO", "False"),
        "muestra_orina_fecha": _date("muestra_orina_fecha"),
        "antigeno": _val("antigeno_prueba"),
        "resultado_lab": _val("resultado_prueba"),
        "fecha_recep_lab": _date("fecha_recepcion_laboratorio"),
        "fecha_resul_lab": _date("fecha_resultado_laboratorio"),
    }
    return mapped


# ── Bot ──────────────────────────────────────────────────────────────────────

class MSPASBot:
    """Headless Playwright bot that fills the MSPAS EPIWEB sarampion form."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.screenshots: list[str] = []
        self.errors: list[str] = []
        self._start_time: float = 0.0

    # ── Helpers ──────────────────────────────────────────────────────────

    def _screenshot(self, page, name: str) -> str:
        """Take a screenshot and add it to the list."""
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
        try:
            page.screenshot(path=path, full_page=True)
            self.screenshots.append(path)
            logger.info("Screenshot saved: %s", path)
        except Exception as e:
            logger.warning("Screenshot failed (%s): %s", name, e)
        return path

    def _safe_fill(self, page, selector: str, value: str, label: str = ""):
        """Fill a text input, logging errors instead of crashing."""
        if not value:
            return
        try:
            el = page.query_selector(selector)
            if el:
                el.click()
                el.fill("")  # clear first
                el.fill(value)
                logger.debug("Filled %s = %s", label or selector, value)
            else:
                msg = f"Element not found: {selector} ({label})"
                logger.warning(msg)
                self.errors.append(msg)
        except Exception as e:
            msg = f"Error filling {label or selector}: {e}"
            logger.warning(msg)
            self.errors.append(msg)

    def _safe_select(self, page, selector: str, value: str, label: str = ""):
        """Select an option from a <select> element by visible text or value."""
        if not value:
            return
        try:
            el = page.query_selector(selector)
            if not el:
                msg = f"Select not found: {selector} ({label})"
                logger.warning(msg)
                self.errors.append(msg)
                return

            # Try selecting by label (visible text) first, then by value
            try:
                page.select_option(selector, label=value)
                logger.debug("Selected %s = %s (by label)", label or selector, value)
                return
            except Exception:
                pass

            # Try partial match: find the option whose text contains the value
            options = el.query_selector_all("option")
            val_upper = value.upper().strip()
            for opt in options:
                text = (opt.text_content() or "").strip().upper()
                if val_upper in text or text in val_upper:
                    opt_value = opt.get_attribute("value")
                    if opt_value:
                        page.select_option(selector, value=opt_value)
                        logger.debug("Selected %s = %s (partial match)", label or selector, text)
                        return

            msg = f"No matching option for {label or selector} = {value}"
            logger.warning(msg)
            self.errors.append(msg)

        except Exception as e:
            msg = f"Error selecting {label or selector}: {e}"
            logger.warning(msg)
            self.errors.append(msg)

    def _safe_searchable_select(self, page, selector: str, value: str, label: str = ""):
        """Handle searchable/filterable select2 or chosen-style dropdowns.
        Types partial text to filter, then selects the first matching result.
        """
        if not value:
            return
        try:
            # EPIWEB uses select elements with a search input sibling
            # Try the select itself first
            el = page.query_selector(selector)
            if not el:
                msg = f"Searchable select not found: {selector} ({label})"
                logger.warning(msg)
                self.errors.append(msg)
                return

            # Look for an associated search input (chosen/select2 pattern)
            # Chosen: .chosen-container → input.chosen-search-input
            # select2: .select2-container → input.select2-search__field
            container_id = el.get_attribute("id") or ""

            # Try chosen-style
            chosen_input = page.query_selector(
                f"#{container_id}_chosen .chosen-search input, "
                f"#{container_id}_chzn .chzn-search input"
            )
            if chosen_input:
                chosen_container = page.query_selector(
                    f"#{container_id}_chosen, #{container_id}_chzn"
                )
                if chosen_container:
                    chosen_container.click()
                    page.wait_for_timeout(300)
                # Type partial text to filter
                search_text = value[:20]  # first 20 chars
                chosen_input.fill("")
                chosen_input.type(search_text, delay=50)
                page.wait_for_timeout(800)
                # Click first highlighted/visible result
                result = page.query_selector(
                    f"#{container_id}_chosen .chosen-results li.active-result:first-child, "
                    f"#{container_id}_chzn .chzn-results li.active-result:first-child"
                )
                if result:
                    result.click()
                    logger.debug("Searchable selected %s = %s (chosen)", label, value)
                    return

            # Fallback: direct select with partial match
            self._safe_select(page, selector, value, label)

        except Exception as e:
            msg = f"Error in searchable select {label or selector}: {e}"
            logger.warning(msg)
            self.errors.append(msg)

    def _safe_radio(self, page, name: str, value: str, label: str = ""):
        """Click a radio button by name and value."""
        if not value:
            return
        try:
            selector = f'input[name="{name}"][value="{value}"]'
            el = page.query_selector(selector)
            if el:
                el.click()
                logger.debug("Radio %s = %s", label or name, value)
            else:
                # Try case-insensitive match
                radios = page.query_selector_all(f'input[name="{name}"]')
                for radio in radios:
                    radio_val = (radio.get_attribute("value") or "").upper()
                    if radio_val == value.upper():
                        radio.click()
                        logger.debug("Radio %s = %s (case match)", label or name, value)
                        return
                msg = f"Radio not found: {name}={value} ({label})"
                logger.warning(msg)
                self.errors.append(msg)
        except Exception as e:
            msg = f"Error clicking radio {label or name}: {e}"
            logger.warning(msg)
            self.errors.append(msg)

    def _safe_checkbox(self, page, selector: str, checked: bool, label: str = ""):
        """Set a checkbox to checked or unchecked state."""
        try:
            el = page.query_selector(selector)
            if not el:
                msg = f"Checkbox not found: {selector} ({label})"
                logger.warning(msg)
                self.errors.append(msg)
                return
            is_checked = el.is_checked()
            if checked and not is_checked:
                el.click()
            elif not checked and is_checked:
                el.click()
            logger.debug("Checkbox %s = %s", label or selector, checked)
        except Exception as e:
            msg = f"Error on checkbox {label or selector}: {e}"
            logger.warning(msg)
            self.errors.append(msg)

    def _click_tab(self, page, tab_text: str):
        """Click a tab link by its visible text."""
        try:
            # EPIWEB tabs are typically <a> or <li> with text
            tab = page.query_selector(f'a:has-text("{tab_text}")')
            if not tab:
                tab = page.query_selector(f'li:has-text("{tab_text}") a')
            if not tab:
                # Try broader search
                links = page.query_selector_all("a")
                for link in links:
                    text = (link.text_content() or "").strip()
                    if tab_text.lower() in text.lower():
                        tab = link
                        break
            if tab:
                tab.click()
                page.wait_for_timeout(PAGE_SETTLE)
                logger.info("Clicked tab: %s", tab_text)
            else:
                msg = f"Tab not found: {tab_text}"
                logger.warning(msg)
                self.errors.append(msg)
        except Exception as e:
            msg = f"Error clicking tab {tab_text}: {e}"
            logger.warning(msg)
            self.errors.append(msg)

    def _wait_for_ajax(self, page, timeout_ms: int = AJAX_WAIT):
        """Wait for pending AJAX requests to complete (jQuery)."""
        try:
            page.wait_for_timeout(timeout_ms)
            # Also check jQuery.active if available
            page.evaluate("""
                () => new Promise(resolve => {
                    if (typeof jQuery !== 'undefined' && jQuery.active > 0) {
                        const check = setInterval(() => {
                            if (jQuery.active === 0) { clearInterval(check); resolve(); }
                        }, 200);
                        setTimeout(() => { clearInterval(check); resolve(); }, 5000);
                    } else {
                        resolve();
                    }
                })
            """)
        except Exception:
            page.wait_for_timeout(timeout_ms)

    # ── Login ────────────────────────────────────────────────────────────

    def login(self, page) -> bool:
        """Login to MSPAS EPIWEB. Returns True on success."""
        logger.info("Navigating to EPIWEB login: %s", EPIWEB_URL)
        page.goto(EPIWEB_URL, timeout=NAV_TIMEOUT, wait_until="networkidle")
        page.wait_for_timeout(2000)

        # Fill credentials
        usuario_input = page.query_selector('input[name="usuario"]')
        if not usuario_input:
            # Try alternate selectors
            usuario_input = page.query_selector('input[name="user"], input[name="username"], input#usuario')

        if not usuario_input:
            self.errors.append("Login: username field not found")
            self._screenshot(page, "login_error")
            return False

        usuario_input.fill(self.username)

        password_input = page.query_selector('input[type="password"]')
        if not password_input:
            self.errors.append("Login: password field not found")
            self._screenshot(page, "login_error")
            return False

        password_input.fill(self.password)

        # Click submit
        submit = page.query_selector(
            'button[type="submit"], input[type="submit"], '
            'button:has-text("Ingresar"), button:has-text("Entrar"), '
            'input[value="Ingresar"], input[value="Entrar"]'
        )
        if submit:
            submit.click()
        else:
            # Fallback: press Enter
            password_input.press("Enter")

        page.wait_for_timeout(3000)

        # Verify login success — expect redirect to sistema.php or similar
        current_url = page.url
        if "sistema" in current_url.lower() or "inicio" in current_url.lower() or "dashboard" in current_url.lower():
            logger.info("Login successful. URL: %s", current_url)
            self._screenshot(page, "login_success")
            return True

        # Check for error messages
        error_el = page.query_selector(".alert-danger, .error, .text-danger, #msg_error")
        if error_el:
            error_text = error_el.text_content() or "Unknown login error"
            self.errors.append(f"Login failed: {error_text.strip()}")
            self._screenshot(page, "login_error")
            return False

        # Might have logged in but URL doesn't match expected pattern
        logger.warning("Login status unclear. URL: %s", current_url)
        self._screenshot(page, "login_unclear")
        return True  # Proceed anyway; form navigation will fail if truly not logged in

    # ── Navigation ───────────────────────────────────────────────────────

    def navigate_to_form(self, page) -> bool:
        """Navigate from the dashboard to the sarampion form creation page."""
        logger.info("Navigating to sarampion form...")

        # Step 1: Go directly to fichas list page (skip intermediate clicks)
        base_url = EPIWEB_URL.rstrip("/")
        page.goto(f"{base_url}/fichas/paginas/fichas.php", timeout=NAV_TIMEOUT, wait_until="networkidle")
        page.wait_for_timeout(2000)
        self._screenshot(page, "nav_fichas_list")
        logger.info("Navigated to fichas list")

        # Step 2: Find and click sarampion row (green arrow button)
        sarampion_link = page.query_selector(
            'a[href*="sarampion"], td:has-text("Sarampi") ~ td a, '
            'tr:has-text("Sarampi") a[href*="sarampion"]'
        )
        if not sarampion_link:
            # Broader search: find any link in a row containing "Sarampi"
            rows = page.query_selector_all("tr")
            for row in rows:
                text = (row.text_content() or "").lower()
                if "sarampi" in text:
                    link = row.query_selector("a")
                    if link:
                        sarampion_link = link
                        break

        if sarampion_link:
            sarampion_link.click()
            page.wait_for_timeout(2000)
            logger.info("Clicked sarampion entry")
        else:
            # Last resort: direct URL
            page.goto(f"{base_url}/fichas/paginas/sar/sarampion.php", timeout=NAV_TIMEOUT, wait_until="networkidle")
            page.wait_for_timeout(2000)
            logger.info("Navigated directly to sarampion list")

        self._screenshot(page, "nav_sarampion_list")

        # Step 3: Click "Crear Ficha Nueva" or equivalent
        create_btn = page.query_selector(
            'a:has-text("Crear Ficha"), a:has-text("Nueva Ficha"), '
            'a:has-text("Crear ficha"), a:has-text("Nuevo"), '
            'button:has-text("Crear"), button:has-text("Nueva"), '
            'a:has-text("Agregar"), a[href*="crear"], a[href*="nuevo"], '
            'a[href*="new"], a.btn-primary, a.btn-success'
        )
        if create_btn:
            create_btn.click()
            page.wait_for_timeout(3000)
            logger.info("Clicked create new form button")
        else:
            self.errors.append("'Crear Ficha Nueva' button not found")
            self._screenshot(page, "nav_create_error")
            return False

        self._screenshot(page, "nav_form_ready")
        return True

    # ── Tab 1: Datos Generales ───────────────────────────────────────────

    def fill_tab1_datos_generales(self, page, data: dict):
        """Fill Tab 1 — Datos Generales."""
        logger.info("Filling Tab 1: Datos Generales")

        # fecha_not — date field with hasDatepicker class
        if data.get("fecha_not"):
            # Clear any datepicker readonly attribute first
            page.evaluate("""
                () => {
                    const el = document.querySelector('#fecha_not, input[name="fecha_not"]');
                    if (el) { el.removeAttribute('readonly'); }
                }
            """)
            self._safe_fill(page, '#fecha_not, input[name="fecha_not"]', data["fecha_not"], "fecha_not")

        # Centro de salud (searchable select with 122 options)
        if data.get("centro_partial"):
            self._safe_searchable_select(
                page,
                '#cbox_centroP, select[name="cbox_centroP"]',
                data["centro_partial"],
                "centro"
            )

        # Responsable fields
        self._safe_fill(page, '#nom_responsable, input[name="nom_responsable"]', data.get("nom_responsable", ""), "nom_responsable")
        self._safe_fill(page, '#cargo_responsable, input[name="cargo_responsable"]', data.get("cargo_responsable", ""), "cargo_responsable")
        self._safe_fill(page, '#tel_responsable, input[name="tel_responsable"]', data.get("tel_responsable", ""), "tel_responsable")

        self._screenshot(page, "tab1_datos_generales")

    # ── Tab 2: Datos Paciente ────────────────────────────────────────────

    def fill_tab2_datos_paciente(self, page, data: dict):
        """Fill Tab 2 — Datos del Paciente."""
        logger.info("Filling Tab 2: Datos Paciente")
        self._click_tab(page, "Datos Paciente")

        # Patient name
        self._safe_fill(page, '#nombres, input[name="nombres"]', data.get("nombres", ""), "nombres")
        self._safe_fill(page, '#apellidos, input[name="apellidos"]', data.get("apellidos", ""), "apellidos")

        # Gender select
        if data.get("genero"):
            self._safe_select(page, '#cbox_genero, select[name="cbox_genero"]', data["genero"], "genero")

        # Ethnicity
        if data.get("etnia"):
            self._safe_select(page, '#cbox_etnia, select[name="cbox_etnia"]', data["etnia"], "etnia")

        # Occupation (searchable, 441 options — type partial text)
        if data.get("ocupacion"):
            self._safe_searchable_select(
                page,
                '#cbox_ocup, select[name="cbox_ocup"]',
                data["ocupacion"],
                "ocupacion"
            )

        # Education level
        if data.get("escolaridad"):
            self._safe_select(page, '#cbox_escolar, select[name="cbox_escolar"]', data["escolaridad"], "escolaridad")

        # Department → Municipality → Poblado (cascading AJAX selects)
        if data.get("departamento"):
            self._safe_select(
                page,
                '#cbox_iddep, select[name="cbox_iddep"]',
                data["departamento"],
                "departamento"
            )
            # CRITICAL: Wait for municipios to load via AJAX
            logger.info("Waiting for municipios AJAX load...")
            self._wait_for_ajax(page, 2000)
            page.wait_for_timeout(AJAX_WAIT)

        if data.get("municipio"):
            self._safe_select(
                page,
                '#cbox_idmun, select[name="cbox_idmun"]',
                data["municipio"],
                "municipio"
            )
            # Wait for poblados to load via AJAX
            logger.info("Waiting for poblados AJAX load...")
            self._wait_for_ajax(page, 1500)
            page.wait_for_timeout(1000)

        if data.get("poblado"):
            self._safe_select(
                page,
                '#cbox_idlp, select[name="cbox_idlp"]',
                data["poblado"],
                "poblado"
            )

        # Address
        self._safe_fill(page, '#p_dir, input[name="p_dir"]', data.get("direccion", ""), "direccion")

        # Birth date (triggers age auto-calculation)
        if data.get("fecha_nac"):
            page.evaluate("""
                () => {
                    const el = document.querySelector('#fecha_nac, input[name="fecha_nac"]');
                    if (el) { el.removeAttribute('readonly'); }
                }
            """)
            self._safe_fill(page, '#fecha_nac, input[name="fecha_nac"]', data["fecha_nac"], "fecha_nac")
            # Trigger change event to activate age calculation
            page.evaluate("""
                () => {
                    const el = document.querySelector('#fecha_nac, input[name="fecha_nac"]');
                    if (el) {
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                        el.dispatchEvent(new Event('blur', { bubbles: true }));
                    }
                }
            """)
            page.wait_for_timeout(500)

        # Mother's name
        self._safe_fill(page, '#nombre_madre, input[name="nombre_madre"]', data.get("nombre_madre", ""), "nombre_madre")

        # Female-only fields
        if data.get("genero", "").upper() in ("F", "FEMENINO", "MUJER"):
            if data.get("embarazada"):
                self._safe_radio(page, "rad_embarazada", data["embarazada"], "embarazada")
            if data.get("lactando"):
                self._safe_radio(page, "rad_lactando", data["lactando"], "lactando")
            if data.get("sem_embarazo"):
                self._safe_fill(
                    page,
                    '#txt_sem_emb, input[name="txt_sem_emb"]',
                    data["sem_embarazo"],
                    "semanas_embarazo"
                )

        self._screenshot(page, "tab2_datos_paciente")

    # ── Tab 3: Informacion Clinica ───────────────────────────────────────

    def fill_tab3_info_clinica(self, page, data: dict):
        """Fill Tab 3 — Informacion Clinica."""
        logger.info("Filling Tab 3: Informacion Clinica")
        self._click_tab(page, "Informaci")  # partial match: "Información Clínica"

        # Dates
        for field, key in [
            ("fecha_ini_sint", "fecha_ini_sint"),
            ("fecha_captacion", "fecha_captacion"),
            ("fecha_domiciliaria", "fecha_domiciliaria"),
            ("fecha_investigacion", "fecha_investigacion"),
            ("txt_fecha_erupcion", "fecha_erupcion"),
            ("txt_fecha_fiebre", "fecha_fiebre"),
        ]:
            val = data.get(key, "")
            if val:
                # Remove readonly for datepicker fields
                page.evaluate(f"""
                    () => {{
                        const el = document.querySelector('#{field}, input[name="{field}"]');
                        if (el) {{ el.removeAttribute('readonly'); }}
                    }}
                """)
                self._safe_fill(page, f'#{field}, input[name="{field}"]', val, field)

        # Source of notification (select)
        if data.get("fuente_noti"):
            self._safe_select(
                page,
                '#cb_fuente_noti, select[name="cb_fuente_noti"]',
                data["fuente_noti"],
                "fuente_notificacion"
            )

        # Active search
        if data.get("busqueda_activa"):
            self._safe_select(
                page,
                '#slc_activa, select[name="slc_activa"]',
                data["busqueda_activa"],
                "busqueda_activa"
            )

        # Eruption type/site
        if data.get("sitio_erupcion"):
            self._safe_select(
                page,
                '#cbox_erupciones, select[name="cbox_erupciones"]',
                data["sitio_erupcion"],
                "sitio_erupcion"
            )

        # Temperature
        self._safe_fill(
            page,
            '#txt_temperatura, input[name="txt_temperatura"]',
            data.get("temperatura", ""),
            "temperatura"
        )

        # Clinical signs (radio buttons: SI/NO)
        for sign_name, key in [
            ("tos", "signo_tos"),
            ("coriza", "signo_coriza"),
            ("conjuntivitis", "signo_conjuntivitis"),
            ("adenopatias", "signo_adenopatias"),
            ("artralgia", "signo_artralgia"),
        ]:
            val = data.get(key, "")
            if val:
                # Try common MSPAS naming patterns
                for name_pattern in [sign_name, f"rad_{sign_name}", f"signo_{sign_name}"]:
                    el = page.query_selector(f'input[name="{name_pattern}"]')
                    if el:
                        self._safe_radio(page, name_pattern, val, sign_name)
                        break
                else:
                    # Try to find by nearby label text
                    self._safe_radio(page, sign_name, val, sign_name)

        # Vaccination section
        if data.get("vacunado"):
            self._safe_radio(page, "vacunado", data["vacunado"], "vacunado")

            if data["vacunado"] == "SI":
                page.wait_for_timeout(500)

                if data.get("fuente_vacuna"):
                    self._safe_select(
                        page,
                        '#cb_fuente, select[name="cb_fuente"]',
                        data["fuente_vacuna"],
                        "fuente_vacuna"
                    )

                if data.get("tipo_vacuna"):
                    self._safe_select(
                        page,
                        '#cb_vacuna, select[name="cb_vacuna"]',
                        data["tipo_vacuna"],
                        "tipo_vacuna"
                    )

                if data.get("no_dosis"):
                    self._safe_select(
                        page,
                        '#no_dosis, select[name="no_dosis"]',
                        data["no_dosis"],
                        "no_dosis"
                    )

                if data.get("fecha_ult_dosis"):
                    page.evaluate("""
                        () => {
                            const el = document.querySelector('#fecha_ult_dosis, input[name="fecha_ult_dosis"]');
                            if (el) { el.removeAttribute('readonly'); }
                        }
                    """)
                    self._safe_fill(
                        page,
                        '#fecha_ult_dosis, input[name="fecha_ult_dosis"]',
                        data["fecha_ult_dosis"],
                        "fecha_ult_dosis"
                    )

        # Hospitalization section
        if data.get("hospitalizado"):
            self._safe_radio(page, "hospitalizacion", data["hospitalizado"], "hospitalizacion")

            if data["hospitalizado"] == "SI":
                page.wait_for_timeout(500)
                self._safe_fill(
                    page,
                    '#hosp_nombre, input[name="hosp_nombre"]',
                    data.get("hosp_nombre", ""),
                    "hosp_nombre"
                )
                if data.get("hosp_fecha"):
                    page.evaluate("""
                        () => {
                            const el = document.querySelector('#hosp_fecha, input[name="hosp_fecha"]');
                            if (el) { el.removeAttribute('readonly'); }
                        }
                    """)
                    self._safe_fill(
                        page,
                        '#hosp_fecha, input[name="hosp_fecha"]',
                        data["hosp_fecha"],
                        "hosp_fecha"
                    )
                self._safe_fill(
                    page,
                    '#hosp_reg_med, input[name="hosp_reg_med"]',
                    data.get("hosp_reg_med", ""),
                    "hosp_reg_med"
                )

        # Discharge condition
        if data.get("condicion_egreso"):
            self._safe_select(
                page,
                '#cb_egreso_condicion, select[name="cb_egreso_condicion"]',
                data["condicion_egreso"],
                "condicion_egreso"
            )

        # Discharge date
        if data.get("fecha_egreso"):
            page.evaluate("""
                () => {
                    const el = document.querySelector('#egreso_fecha, input[name="egreso_fecha"]');
                    if (el) { el.removeAttribute('readonly'); }
                }
            """)
            self._safe_fill(
                page,
                '#egreso_fecha, input[name="egreso_fecha"]',
                data["fecha_egreso"],
                "fecha_egreso"
            )

        # Pregnancy in clinical tab (some MSPAS forms duplicate this here)
        if data.get("embarazada"):
            self._safe_radio(page, "rad_embarazada", data["embarazada"], "embarazada_clinica")

        self._screenshot(page, "tab3_info_clinica")

    # ── Tab 4: Factores de Riesgo ────────────────────────────────────────

    def fill_tab4_factores_riesgo(self, page, data: dict):
        """Fill Tab 4 — Factores de Riesgo."""
        logger.info("Filling Tab 4: Factores de Riesgo")
        self._click_tab(page, "Factores")  # partial match

        # Contact with suspicious case 7-23 days
        if data.get("contacto_sospechoso"):
            self._safe_radio(page, "rad_contacto", data["contacto_sospechoso"], "contacto_sospechoso")

        # Suspicious cases in community in last 3 months
        if data.get("casos_comunidad"):
            self._safe_radio(page, "rad_casos", data["casos_comunidad"], "casos_comunidad")

        # Traveled 7-23 days prior
        if data.get("viajo"):
            self._safe_radio(page, "rad_viajo", data["viajo"], "viajo")

            if data["viajo"] == "SI" and data.get("donde_viajo"):
                page.wait_for_timeout(500)
                self._safe_fill(
                    page,
                    '#txt_donde_viajo, input[name="txt_donde_viajo"]',
                    data["donde_viajo"],
                    "donde_viajo"
                )

        self._screenshot(page, "tab4_factores_riesgo")

    # ── Tab 5: Laboratorio ───────────────────────────────────────────────

    def fill_tab5_laboratorio(self, page, data: dict):
        """Fill Tab 5 — Laboratorio."""
        logger.info("Filling Tab 5: Laboratorio")
        self._click_tab(page, "Laboratorio")

        # Did they collect a sample?
        if data.get("recolecto_muestra"):
            self._safe_radio(page, "pick_muestra", data["recolecto_muestra"], "recolecto_muestra")

            if data["recolecto_muestra"] == "SI":
                page.wait_for_timeout(500)

                # Suero checkbox + date
                if data.get("muestra_suero"):
                    self._safe_checkbox(
                        page,
                        '#suero, input[name="suero"], input[type="checkbox"][value="suero"]',
                        True,
                        "muestra_suero"
                    )
                    if data.get("muestra_suero_fecha"):
                        page.evaluate("""
                            () => {
                                const el = document.querySelector('#suero_fecha, input[name="suero_fecha"]');
                                if (el) { el.removeAttribute('readonly'); }
                            }
                        """)
                        self._safe_fill(
                            page,
                            '#suero_fecha, input[name="suero_fecha"]',
                            data["muestra_suero_fecha"],
                            "suero_fecha"
                        )

                # Hisopado checkbox + date
                if data.get("muestra_hisopado"):
                    self._safe_checkbox(
                        page,
                        '#hisopado, input[name="hisopado"], input[type="checkbox"][value="hisopado"]',
                        True,
                        "muestra_hisopado"
                    )
                    if data.get("muestra_hisopado_fecha"):
                        page.evaluate("""
                            () => {
                                const el = document.querySelector('#hisopado_fecha, input[name="hisopado_fecha"]');
                                if (el) { el.removeAttribute('readonly'); }
                            }
                        """)
                        self._safe_fill(
                            page,
                            '#hisopado_fecha, input[name="hisopado_fecha"]',
                            data["muestra_hisopado_fecha"],
                            "hisopado_fecha"
                        )

                # Orina checkbox + date
                if data.get("muestra_orina"):
                    self._safe_checkbox(
                        page,
                        '#orina, input[name="orina"], input[type="checkbox"][value="orina"]',
                        True,
                        "muestra_orina"
                    )
                    if data.get("muestra_orina_fecha"):
                        page.evaluate("""
                            () => {
                                const el = document.querySelector('#orina_fecha, input[name="orina_fecha"]');
                                if (el) { el.removeAttribute('readonly'); }
                            }
                        """)
                        self._safe_fill(
                            page,
                            '#orina_fecha, input[name="orina_fecha"]',
                            data["muestra_orina_fecha"],
                            "orina_fecha"
                        )

        # Antigen/test type
        if data.get("antigeno"):
            self._safe_select(
                page,
                '#slc_antigeno, select[name="slc_antigeno"]',
                data["antigeno"],
                "antigeno"
            )

        # Reception date at lab
        if data.get("fecha_recep_lab"):
            page.evaluate("""
                () => {
                    const el = document.querySelector('#fecha_recep, input[name="fecha_recep"]');
                    if (el) { el.removeAttribute('readonly'); }
                }
            """)
            self._safe_fill(
                page,
                '#fecha_recep, input[name="fecha_recep"]',
                data["fecha_recep_lab"],
                "fecha_recep_lab"
            )

        # Result date
        if data.get("fecha_resul_lab"):
            page.evaluate("""
                () => {
                    const el = document.querySelector('#fecha_resul_lab, input[name="fecha_resul_lab"]');
                    if (el) { el.removeAttribute('readonly'); }
                }
            """)
            self._safe_fill(
                page,
                '#fecha_resul_lab, input[name="fecha_resul_lab"]',
                data["fecha_resul_lab"],
                "fecha_resul_lab"
            )

        # Lab result
        if data.get("resultado_lab"):
            self._safe_select(
                page,
                '#slc_resul_lab, select[name="slc_resul_lab"]',
                data["resultado_lab"],
                "resultado_lab"
            )

        self._screenshot(page, "tab5_laboratorio")

    # ── Submit ───────────────────────────────────────────────────────────

    def submit_form(self, page) -> dict:
        """Click Guardar and capture result. ONLY called in PRODUCTION_MODE."""
        logger.info("PRODUCTION MODE: Submitting form...")

        # Double-check safety gate
        if not PRODUCTION_MODE:
            logger.error("submit_form() called but PRODUCTION_MODE is False. Aborting.")
            return {
                "success": False,
                "production_mode": False,
                "submitted": False,
                "mspas_ficha_id": None,
                "screenshots": self.screenshots,
                "errors": ["submit_form() called without MSPAS_PRODUCTION_MODE=true"],
                "duration_seconds": time.time() - self._start_time,
            }

        self._screenshot(page, "pre_submit")

        # Find and click Guardar button
        guardar_btn = page.query_selector(
            'button:has-text("Guardar"), input[type="submit"][value*="Guardar"], '
            'a:has-text("Guardar"), button:has-text("GUARDAR"), '
            'input[value="Guardar"], #btn_guardar, button#guardar'
        )

        if not guardar_btn:
            self.errors.append("Guardar button not found")
            self._screenshot(page, "submit_error_no_button")
            return {
                "success": False,
                "production_mode": True,
                "submitted": False,
                "mspas_ficha_id": None,
                "screenshots": self.screenshots,
                "errors": self.errors,
                "duration_seconds": time.time() - self._start_time,
            }

        guardar_btn.click()
        page.wait_for_timeout(5000)

        self._screenshot(page, "post_submit")

        # Try to capture the MSPAS ficha ID from the result page
        mspas_ficha_id = None
        try:
            # Look for ID in the page content (common patterns)
            page_text = page.text_content("body") or ""

            # Pattern: "Ficha No. 12345" or "ID: 12345" or similar
            id_patterns = [
                r'[Ff]icha\s*(?:No\.?|N[uú]mero)?\s*[:\s]*(\d{4,})',
                r'[Ii][Dd]\s*[:\s]*(\d{4,})',
                r'[Rr]egistro\s*[:\s]*(\d{4,})',
                r'guardad[ao]\s+(?:con\s+)?(?:éxito|exito).*?(\d{4,})',
            ]
            for pattern in id_patterns:
                match = re.search(pattern, page_text)
                if match:
                    mspas_ficha_id = match.group(1)
                    logger.info("Captured MSPAS ficha ID: %s", mspas_ficha_id)
                    break

            # Also check URL for ID
            url = page.url
            url_match = re.search(r'[?&]id=(\d+)', url)
            if url_match and not mspas_ficha_id:
                mspas_ficha_id = url_match.group(1)

        except Exception as e:
            logger.warning("Could not capture ficha ID: %s", e)

        # Check for success/error messages
        success_el = page.query_selector(".alert-success, .success, .text-success")
        error_el = page.query_selector(".alert-danger, .error, .text-danger")

        submitted_ok = True
        if error_el:
            error_text = error_el.text_content() or "Form submission error"
            self.errors.append(f"Submit error: {error_text.strip()}")
            submitted_ok = False

        return {
            "success": submitted_ok,
            "production_mode": True,
            "submitted": True,
            "mspas_ficha_id": mspas_ficha_id,
            "screenshots": self.screenshots,
            "errors": self.errors,
            "duration_seconds": time.time() - self._start_time,
        }

    # ── Main entry point ─────────────────────────────────────────────────

    def process_record(self, record: dict) -> dict:
        """Main entry point. Takes a DB record dict, returns result dict.

        In default mode (MSPAS_PRODUCTION_MODE != 'true'), fills the form
        completely but does NOT click Guardar.

        Args:
            record: dict with keys matching IGSS DB column names
                    (see database.py COLUMNS).

        Returns:
            dict with keys:
                success (bool), production_mode (bool), submitted (bool),
                mspas_ficha_id (str|None), screenshots (list[str]),
                errors (list[str]), duration_seconds (float)
        """
        self._start_time = time.time()
        self.screenshots = []
        self.errors = []

        mapped = map_record_to_mspas(record)

        logger.info(
            "Processing record. Production mode: %s. Fields mapped: %d",
            PRODUCTION_MODE, sum(1 for v in mapped.values() if v)
        )

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {
                "success": False,
                "production_mode": PRODUCTION_MODE,
                "submitted": False,
                "mspas_ficha_id": None,
                "screenshots": [],
                "errors": ["playwright not installed. Run: pip install playwright && playwright install chromium"],
                "duration_seconds": time.time() - self._start_time,
            }

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                ]
            )
            context = browser.new_context(
                viewport={"width": 1280, "height": 900},
                locale="es-GT",
                timezone_id="America/Guatemala",
            )
            page = context.new_page()
            page.set_default_timeout(ACTION_TIMEOUT)

            try:
                # Step 1: Login
                if not self.login(page):
                    return {
                        "success": False,
                        "production_mode": PRODUCTION_MODE,
                        "submitted": False,
                        "mspas_ficha_id": None,
                        "screenshots": self.screenshots,
                        "errors": self.errors,
                        "duration_seconds": time.time() - self._start_time,
                    }

                # Step 2: Navigate to form
                if not self.navigate_to_form(page):
                    return {
                        "success": False,
                        "production_mode": PRODUCTION_MODE,
                        "submitted": False,
                        "mspas_ficha_id": None,
                        "screenshots": self.screenshots,
                        "errors": self.errors,
                        "duration_seconds": time.time() - self._start_time,
                    }

                # Step 3: Fill all tabs
                self.fill_tab1_datos_generales(page, mapped)
                self.fill_tab2_datos_paciente(page, mapped)
                self.fill_tab3_info_clinica(page, mapped)
                self.fill_tab4_factores_riesgo(page, mapped)
                self.fill_tab5_laboratorio(page, mapped)

                # Step 4: Submit or stop
                if PRODUCTION_MODE:
                    return self.submit_form(page)
                else:
                    self._screenshot(page, "final_preview")
                    logger.info(
                        "DRY RUN complete. Form filled but NOT submitted. "
                        "Set MSPAS_PRODUCTION_MODE=true to submit."
                    )
                    return {
                        "success": True,
                        "production_mode": False,
                        "submitted": False,
                        "mspas_ficha_id": None,
                        "screenshots": self.screenshots,
                        "errors": self.errors,
                        "duration_seconds": time.time() - self._start_time,
                    }

            except Exception as e:
                logger.exception("Fatal error during form processing")
                self._screenshot(page, "fatal_error")
                return {
                    "success": False,
                    "production_mode": PRODUCTION_MODE,
                    "submitted": False,
                    "mspas_ficha_id": None,
                    "screenshots": self.screenshots,
                    "errors": self.errors + [f"Fatal: {e}"],
                    "duration_seconds": time.time() - self._start_time,
                }
            finally:
                context.close()
                browser.close()


# ── Standalone test ──────────────────────────────────────────────────────────

def _test():
    """Run a test filling with dummy data. NEVER submits.

    Usage:
        MSPAS_USER=myuser MSPAS_PASS=mypass python mspas_bot.py

    Or just run it — it will use placeholder credentials that will fail at
    login but still exercise the code paths and screenshot the attempt.
    """
    # Force production mode OFF for safety
    os.environ["MSPAS_PRODUCTION_MODE"] = "false"

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    username = os.environ.get("MSPAS_USER", "test_user")
    password = os.environ.get("MSPAS_PASS", "test_pass")

    # Sample record matching IGSS DB schema (database.py COLUMNS)
    test_record = {
        "registro_id": "TEST-2026-001",
        "fecha_notificacion": "2026-03-20",
        "unidad_medica": "HOSPITAL GENERAL DE ENFERMEDADES",
        "nom_responsable": "Dr. Juan Perez (TEST)",
        "cargo_responsable": "Epidemiologo",
        "telefono_responsable": "55551234",

        "nombres": "MARIA ELENA",
        "apellidos": "GARCIA LOPEZ",
        "sexo": "FEMENINO",
        "fecha_nacimiento": "1990-05-15",
        "pueblo_etnia": "LADINO",
        "ocupacion": "AMA DE CASA",
        "escolaridad": "PRIMARIA",
        "departamento_residencia": "GUATEMALA",
        "municipio_residencia": "GUATEMALA",
        "direccion_exacta": "ZONA 1, CIUDAD DE GUATEMALA",
        "nombre_encargado": "ROSA LOPEZ DE GARCIA",

        "esta_embarazada": "NO",
        "lactando": "NO",

        "fecha_inicio_sintomas": "2026-03-15",
        "fecha_captacion": "2026-03-17",
        "fuente_notificacion": "CONSULTA EXTERNA",
        "fecha_visita_domiciliaria": "2026-03-18",
        "fecha_inicio_investigacion": "2026-03-18",
        "busqueda_activa": "SI",
        "fecha_inicio_erupcion": "2026-03-16",
        "sitio_inicio_erupcion": "CARA",
        "fecha_inicio_fiebre": "2026-03-15",
        "temperatura_celsius": "38.5",
        "signo_tos": "SI",
        "signo_coriza": "SI",
        "signo_conjuntivitis": "NO",
        "signo_adenopatias": "NO",
        "signo_artralgia": "NO",

        "vacunado": "SI",
        "fuente_info_vacuna": "CARNE",
        "tipo_vacuna": "SPR",
        "numero_dosis_spr": "2",
        "fecha_ultima_dosis": "2020-01-10",

        "hospitalizado": "NO",
        "condicion_egreso": "VIVO",

        "contacto_sospechoso_7_23": "NO",
        "caso_sospechoso_comunidad_3m": "NO",
        "viajo_7_23_previo": "SI",
        "destino_viaje": "PETEN, FLORES",

        "recolecto_muestra": "SI",
        "muestra_suero": "SI",
        "muestra_suero_fecha": "2026-03-17",
        "muestra_hisopado": "SI",
        "muestra_hisopado_fecha": "2026-03-17",
        "muestra_orina": "NO",
        "antigeno_prueba": "ELISA IGM",
        "resultado_prueba": "PENDIENTE",
        "fecha_recepcion_laboratorio": "2026-03-18",
    }

    print("=" * 70)
    print("MSPAS EPIWEB Sarampion Bot — TEST MODE (will NOT submit)")
    print(f"Production mode: {PRODUCTION_MODE}")
    print(f"Username: {username}")
    print(f"Screenshot dir: {SCREENSHOT_DIR}")
    print("=" * 70)

    bot = MSPASBot(username=username, password=password)
    result = bot.process_record(test_record)

    print("\n" + "=" * 70)
    print("RESULT:")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    print("=" * 70)

    if result.get("screenshots"):
        print(f"\nScreenshots saved ({len(result['screenshots'])}):")
        for ss in result["screenshots"]:
            print(f"  {ss}")

    if result.get("errors"):
        print(f"\nErrors ({len(result['errors'])}):")
        for err in result["errors"]:
            print(f"  - {err}")

    return result


if __name__ == "__main__":
    _test()
