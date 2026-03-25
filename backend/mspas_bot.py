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

try:
    from mspas_field_map import (
        map_record_to_mspas as _field_map_record_to_mspas,
        get_code, FUENTE_NOTI_CODES, BUSQUEDA_ACTIVA_CODES, FUENTE_VACUNA_CODES,
        VACUNA_TIPO_CODES, DOSIS_CODES, EGRESO_CODES, SEX_CODES, ETNIA_CODES,
        ESCOLARIDAD_CODES, ERUPCION_CODES, ANTIGENO_CODES, RESULTADO_CODES,
        DEPT_CODES, normalize_si_no, get_occupation_search_text, get_centro_search_text,
        CLASIFICACION_FINAL_CODES, CONFIRMADO_POR_CODES, FUENTE_INFECCION_CODES,
        CRITERIO_DESCARTE_CODES,
    )
    HAS_FIELD_MAP = True
except ImportError:
    HAS_FIELD_MAP = False
    _field_map_record_to_mspas = None

logger = logging.getLogger(__name__)

# ── Safety gate ──────────────────────────────────────────────────────────────
PRODUCTION_MODE = os.environ.get("MSPAS_PRODUCTION_MODE", "false").lower() == "true"

EPIWEB_URL = "https://cne.mspas.gob.gt/epiweb/"
SCREENSHOT_DIR = os.environ.get(
    "MSPAS_SCREENSHOT_DIR",
    "/opt/vigilancia-sarampion/data/mspas_screenshots"
)

# Default timeouts (ms)
NAV_TIMEOUT = 30_000
ACTION_TIMEOUT = 10_000
AJAX_WAIT = 800  # after dept/muni selects (optimized from 1500)
PAGE_SETTLE = 800  # optimized from 2000 (tabs load fast)


# ── Field mapping: IGSS DB → MSPAS form ─────────────────────────────────────

def map_record_to_mspas(record: dict) -> dict:
    """Convert an IGSS DB record dict into the field names expected by the
    MSPAS EPIWEB sarampion form.

    Delegates to the canonical mspas_field_map.map_record_to_mspas() for
    all field conversion logic, then adds bot-specific alias keys that the
    fill_tab*() methods expect (e.g. 'genero', 'centro_partial', etc.).
    """
    # Use canonical field_map as single source of truth
    if HAS_FIELD_MAP and _field_map_record_to_mspas is not None:
        canonical = _field_map_record_to_mspas(record)
    else:
        canonical = {}

    def _val(key, default=""):
        v = record.get(key)
        if v is None:
            return default
        return str(v).strip() or default

    def _radio(key):
        v = _val(key).upper()
        if v in ("SI", "SÍ", "YES", "1", "TRUE"):
            return "SI"
        if v in ("NO", "0", "FALSE"):
            return "NO"
        if v in ("NA", "N/A", "NO APLICA"):
            return "NA"
        return v

    # Start with all canonical fields
    mapped = dict(canonical)

    # Add bot-specific alias keys that fill_tab methods reference
    # Extract key search text from IGSS unit name for MSPAS dropdown partial matching
    _raw_centro = _val("unidad_medica") or _val("centro_externo")
    if HAS_FIELD_MAP:
        mapped["centro_partial"] = get_centro_search_text(_raw_centro)
    else:
        mapped["centro_partial"] = _raw_centro
    mapped["genero"] = _val("sexo")
    mapped["genero_code"] = canonical.get("cbox_genero", "")
    mapped["etnia"] = _val("pueblo_etnia")
    mapped["etnia_code"] = canonical.get("cbox_etnia", "")
    mapped["ocupacion"] = _val("ocupacion")
    mapped["escolaridad"] = _val("escolaridad")
    mapped["escolaridad_code"] = canonical.get("cbox_escolar", "")
    mapped["departamento"] = _val("departamento_residencia")
    mapped["departamento_code"] = canonical.get("cbox_iddep", "")
    mapped["municipio"] = _val("municipio_residencia")
    mapped["poblado"] = _val("poblado")
    mapped["direccion"] = _val("direccion_exacta")
    mapped["fecha_nac"] = canonical.get("fecha_nac", "")
    mapped["nombre_madre"] = _val("nombre_encargado")
    mapped["embarazada"] = _radio("esta_embarazada")
    mapped["lactando"] = _radio("lactando")
    mapped["sem_embarazo"] = _val("semanas_embarazo")

    # Tab 3 aliases
    mapped["fecha_ini_sint"] = canonical.get("fecha_ini_sint", "")
    mapped["fecha_captacion"] = canonical.get("fecha_captacion", "")
    mapped["fuente_noti"] = _val("fuente_notificacion")
    mapped["fuente_noti_code"] = canonical.get("cb_fuente_noti", "")
    mapped["fecha_domiciliaria"] = canonical.get("fecha_domiciliaria", "")
    mapped["fecha_investigacion"] = canonical.get("fecha_investigacion", "")
    mapped["busqueda_activa"] = _val("busqueda_activa")
    mapped["busqueda_activa_code"] = canonical.get("slc_activa", "")
    mapped["fecha_erupcion"] = canonical.get("txt_fecha_erupcion", "")
    mapped["sitio_erupcion"] = _val("sitio_inicio_erupcion")
    mapped["sitio_erupcion_code"] = canonical.get("cbox_erupciones", "")
    mapped["fecha_fiebre"] = canonical.get("txt_fecha_fiebre", "")
    mapped["temperatura"] = canonical.get("txt_temperatura", "")
    mapped["signo_tos"] = _radio("signo_tos")
    mapped["signo_coriza"] = _radio("signo_coriza")
    mapped["signo_conjuntivitis"] = _radio("signo_conjuntivitis")
    mapped["signo_adenopatias"] = _radio("signo_adenopatias")
    mapped["signo_artralgia"] = _radio("signo_artralgia")
    mapped["vacunado"] = _radio("vacunado")
    mapped["fuente_vacuna"] = _val("fuente_info_vacuna")
    mapped["fuente_vacuna_code"] = canonical.get("cb_fuente", "")
    mapped["tipo_vacuna"] = _val("tipo_vacuna")
    mapped["tipo_vacuna_code"] = canonical.get("cb_vacuna", "")
    mapped["no_dosis"] = _val("numero_dosis_spr")
    mapped["no_dosis_code"] = canonical.get("no_dosis", "")
    mapped["fecha_ult_dosis"] = canonical.get("fecha_ult_dosis", "")
    mapped["observaciones_vacuna"] = canonical.get("observaciones", "")
    mapped["hospitalizado"] = _radio("hospitalizado")
    mapped["hosp_nombre"] = _val("hosp_nombre")
    mapped["hosp_fecha"] = canonical.get("hosp_fecha", "")
    mapped["hosp_reg_med"] = _val("no_registro_medico")
    mapped["condicion_egreso"] = _val("condicion_egreso")
    mapped["condicion_egreso_code"] = canonical.get("cb_egreso_condicion", "")
    mapped["fecha_egreso"] = canonical.get("egreso_fecha", "")

    # Tab 4 aliases
    mapped["contacto_sospechoso"] = _radio("contacto_sospechoso_7_23")
    mapped["casos_comunidad"] = _radio("caso_sospechoso_comunidad_3m")
    mapped["viajo"] = _radio("viajo_7_23_previo")
    mapped["donde_viajo"] = _val("destino_viaje")

    # Tab 5 aliases
    mapped["recolecto_muestra"] = _radio("recolecto_muestra")
    mapped["muestra_suero"] = _val("muestra_suero") not in ("", "0", "NO", "False")
    mapped["muestra_suero_fecha"] = canonical.get("fecha_suero", "")
    mapped["muestra_hisopado"] = _val("muestra_hisopado") not in ("", "0", "NO", "False")
    mapped["muestra_hisopado_fecha"] = canonical.get("fecha_HN", "")
    mapped["muestra_orina"] = _val("muestra_orina") not in ("", "0", "NO", "False")
    mapped["muestra_orina_fecha"] = canonical.get("fecha_orina", "")
    mapped["antigeno"] = _val("antigeno_prueba")
    mapped["antigeno_code"] = canonical.get("slc_antigeno", "")
    mapped["resultado_lab"] = _val("resultado_prueba")
    mapped["resultado_lab_code"] = canonical.get("slc_resul_lab", "")
    mapped["fecha_recep_lab"] = canonical.get("fecha_recep", "")
    mapped["fecha_resul_lab"] = canonical.get("fecha_resul_lab", "")

    # Tab 6 — Clasificacion Final (from canonical field_map)
    mapped["clasificacion_code"] = canonical.get("slc_clas_final", "")
    mapped["clasificacion_fecha"] = canonical.get("txt_fecha_final", "")
    mapped["clasificacion_responsable"] = canonical.get("txt_nom_resp_clas", "")
    mapped["clasificacion_observaciones"] = canonical.get("observaciones_clas", "")

    # Tab 6 — Conditional fields (confirmado_por, fuente_infeccion)
    if HAS_FIELD_MAP:
        mapped["confirmado_por_code"] = get_code(
            CONFIRMADO_POR_CODES, _val("confirmado_por"), "")
        mapped["fuente_infeccion_code"] = get_code(
            FUENTE_INFECCION_CODES, _val("fuente_infeccion"), "")
        mapped["criterio_descarte_code"] = get_code(
            CRITERIO_DESCARTE_CODES, _val("criterio_descarte"), "")
    else:
        mapped["confirmado_por_code"] = ""
        mapped["fuente_infeccion_code"] = ""
        mapped["criterio_descarte_code"] = ""

    mapped["investigador_nombre"] = _val("responsable_clasificacion")
    mapped["investigador_cargo"] = _val("cargo_responsable")

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

    def _enrich_result(self, result: dict) -> dict:
        """Inject mapped_data and record_data into every result dict for UI display."""
        result["mapped_data"] = getattr(self, '_mapped_data', {})
        result["record_data"] = getattr(self, '_record_data', {})
        return result

    def _screenshot(self, page, name: str) -> str:
        """Take a screenshot and add it to the list."""
        target_dir = getattr(self, '_record_screenshot_dir', SCREENSHOT_DIR)
        os.makedirs(target_dir, exist_ok=True)
        path = os.path.join(target_dir, f"{name}.png")
        try:
            page.screenshot(path=path, full_page=True)
            self.screenshots.append(path)
            logger.info("Screenshot saved: %s", path)
        except Exception as e:
            logger.warning("Screenshot failed (%s): %s", name, e)
        return path

    def _dismiss_datepicker(self, page):
        """Dismiss any open jQuery UI datepicker overlay."""
        try:
            page.evaluate("""
                () => {
                    const dp = document.getElementById('ui-datepicker-div');
                    if (dp) dp.style.display = 'none';
                    // Also blur any focused element to close datepicker
                    if (document.activeElement) document.activeElement.blur();
                }
            """)
        except Exception:
            pass

    def _safe_fill(self, page, selector: str, value: str, label: str = ""):
        """Fill a text input, logging errors instead of crashing.

        Dismisses any open datepicker before interacting to avoid overlay
        blocking the click.
        """
        if not value:
            return
        try:
            # Dismiss any datepicker that might be covering the element
            self._dismiss_datepicker(page)

            el = page.query_selector(selector)
            if el:
                # For datepicker fields, use JS to set value directly
                is_datepicker = page.evaluate(f"""
                    () => {{
                        const el = document.querySelector('{selector.split(",")[0]}');
                        return el ? el.classList.contains('hasDatepicker') : false;
                    }}
                """)
                if is_datepicker:
                    # Set value via JS (bypasses datepicker overlay issues)
                    page.evaluate(f"""
                        (val) => {{
                            const el = document.querySelector('{selector.split(",")[0]}');
                            if (!el) return;
                            el.removeAttribute('readonly');
                            el.removeAttribute('disabled');
                            el.value = val;
                            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            el.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                            // Hide datepicker
                            const dp = document.getElementById('ui-datepicker-div');
                            if (dp) dp.style.display = 'none';
                        }}
                    """, value)
                    logger.debug("Filled %s = %s (via JS/datepicker)", label or selector, value)
                else:
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

    def _safe_select(self, page, selector: str, value: str, label: str = "",
                     code: str = ""):
        """Select an option from a <select> element.

        Args:
            selector: CSS selector for the <select> element.
            value: Text value for label-based or partial matching (fallback).
            label: Human-readable label for logging.
            code: MSPAS numeric code (e.g. '1', '2'). If provided, select by
                  option value first (most reliable).
        """
        if not value and not code:
            return
        try:
            el = page.query_selector(selector)
            if not el:
                msg = f"Select not found: {selector} ({label})"
                logger.warning(msg)
                self.errors.append(msg)
                return

            # Enable the select if disabled (some fields are disabled until a
            # radio or other field triggers JS to enable them)
            is_disabled = el.get_attribute("disabled") is not None
            if is_disabled:
                css_sel = selector.split(",")[0].strip()
                page.evaluate(f"""
                    () => {{
                        const el = document.querySelector('{css_sel}');
                        if (el) el.removeAttribute('disabled');
                    }}
                """)
                logger.debug("Enabled disabled select: %s", label or selector)

            # Strategy 1: Select by numeric code (most reliable for MSPAS forms)
            if code:
                try:
                    page.select_option(selector, value=code, timeout=3000)
                    logger.debug("Selected %s = code '%s' (by value)", label or selector, code)
                    return
                except Exception:
                    pass
                # Fallback: set via JS if Playwright can't interact
                try:
                    css_sel = selector.split(",")[0].strip()
                    page.evaluate(f"""
                        (code) => {{
                            const el = document.querySelector('{css_sel}');
                            if (el) {{
                                el.removeAttribute('disabled');
                                el.value = code;
                                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            }}
                        }}
                    """, code)
                    logger.debug("Selected %s = code '%s' (via JS)", label or selector, code)
                    return
                except Exception:
                    pass

            # Strategy 2: Select by exact label text
            if value:
                try:
                    page.select_option(selector, label=value, timeout=3000)
                    logger.debug("Selected %s = %s (by label)", label or selector, value)
                    return
                except Exception:
                    pass

                # Strategy 3: Partial match on option text
                options = el.query_selector_all("option")
                val_upper = value.upper().strip()
                for opt in options:
                    text = (opt.text_content() or "").strip().upper()
                    if val_upper in text or text in val_upper:
                        opt_value = opt.get_attribute("value")
                        if opt_value:
                            try:
                                page.select_option(selector, value=opt_value, timeout=3000)
                            except Exception:
                                # JS fallback for partial match
                                css_sel = selector.split(",")[0].strip()
                                page.evaluate(f"""
                                    (val) => {{
                                        const el = document.querySelector('{css_sel}');
                                        if (el) {{
                                            el.removeAttribute('disabled');
                                            el.value = val;
                                            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                        }}
                                    }}
                                """, opt_value)
                            logger.debug("Selected %s = %s (partial match)", label or selector, text)
                            return

            msg = f"No matching option for {label or selector} = {value} (code={code})"
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
        """Click a radio button by name and value.

        Handles MSPAS forms where radios may be hidden behind conditional divs.
        Uses page.check() for reliable checking, with el.click(force=True) and
        JS .click() fallbacks. Also tries alternate value formats (SI/1, NO/2, s/n).
        """
        if not value:
            return

        def _try_check(selector_str: str, desc: str) -> bool:
            """Try multiple strategies to check a radio."""
            # Strategy A: Scroll into view, then use Playwright's click
            # (NOT force=True, so it does real click with visual update)
            try:
                el = page.query_selector(selector_str)
                if el:
                    el.scroll_into_view_if_needed()
                    page.wait_for_timeout(100)
                    try:
                        el.click(timeout=2000)
                        logger.debug("Radio %s = %s (%s via el.click visible)", label or name, value, desc)
                        return True
                    except Exception:
                        pass
                    # Fallback: force click
                    el.click(force=True)
                    logger.debug("Radio %s = %s (%s via el.click force)", label or name, value, desc)
                    return True
            except Exception:
                pass
            # Strategy B: page.check
            try:
                page.check(selector_str, force=True, timeout=2000)
                logger.debug("Radio %s = %s (%s via page.check)", label or name, value, desc)
                return True
            except Exception:
                pass
            # Strategy C: JS — dispatch full MouseEvent for visual update
            try:
                css_sel = selector_str.replace("'", "\\'")
                result = page.evaluate(f"""
                    () => {{
                        const el = document.querySelector('{css_sel}');
                        if (el) {{
                            el.scrollIntoView({{block: 'center'}});
                            el.focus();
                            el.checked = true;
                            // Dispatch full mouse event sequence for visual rendering
                            ['mousedown', 'mouseup', 'click'].forEach(evName => {{
                                el.dispatchEvent(new MouseEvent(evName, {{
                                    bubbles: true, cancelable: true, view: window
                                }}));
                            }});
                            el.dispatchEvent(new Event('change', {{bubbles: true}}));
                            el.dispatchEvent(new Event('input', {{bubbles: true}}));
                            return true;
                        }}
                        return false;
                    }}
                """)
                if result:
                    logger.debug("Radio %s = %s (%s via JS MouseEvent)", label or name, value, desc)
                    return True
            except Exception:
                pass
            return False

        try:
            # Build list of (value_to_try, description) pairs
            alt_map = {"SI": ["si", "s", "S", "1", "Si"], "NO": ["no", "n", "N", "2", "No"],
                       "1": ["SI", "si", "s", "S"], "2": ["NO", "no", "n", "N"],
                       "S": ["SI", "si", "1"], "N": ["NO", "no", "2"],
                       "NA": ["na", "3"], "3": ["NA", "na"]}
            values_to_try = [value]
            # Add case-variants
            if value.upper() not in [v.upper() for v in values_to_try]:
                values_to_try.append(value.upper())
            if value.lower() not in [v.lower() for v in values_to_try]:
                values_to_try.append(value.lower())
            # Add alt mappings
            for alt in alt_map.get(value.upper(), []):
                if alt not in values_to_try:
                    values_to_try.append(alt)

            for try_val in values_to_try:
                selector = f'input[name="{name}"][value="{try_val}"]'
                el = page.query_selector(selector)
                if el:
                    if _try_check(selector, f"value={try_val}"):
                        return

            # No match found at all
            radios = page.query_selector_all(f'input[name="{name}"]')
            if radios:
                available = [radio.get_attribute("value") for radio in radios]
                msg = f"Radio not found: {name}={value} ({label}). Available values: {available}"
                logger.warning(msg)
                self.errors.append(msg)
            else:
                msg = f"No radio inputs found with name='{name}' ({label})"
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

    # ── Session check ────────────────────────────────────────────────────

    def _check_session_alive(self, page) -> bool:
        """Check if the MSPAS session is still active."""
        try:
            # Check if the form title or a known element is still present
            form = page.query_selector('#frm_general, form[name="frm_general"]')
            if form:
                return True
            # Check if we've been redirected to login
            if 'validarUsuario' in page.url or page.url.endswith('/epiweb/'):
                return False
            return True
        except Exception:
            return False

    # ── Login ────────────────────────────────────────────────────────────

    def login(self, page) -> bool:
        """Login to MSPAS EPIWEB. Returns True on success."""
        logger.info("Navigating to EPIWEB login: %s", EPIWEB_URL)
        page.goto(EPIWEB_URL, timeout=NAV_TIMEOUT, wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

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

        page.wait_for_timeout(2000)

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
        page.goto(f"{base_url}/fichas/paginas/fichas.php", timeout=NAV_TIMEOUT, wait_until="domcontentloaded")
        page.wait_for_timeout(1000)
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
            page.wait_for_timeout(1000)
            logger.info("Clicked sarampion entry")
        else:
            # Last resort: direct URL
            page.goto(f"{base_url}/fichas/paginas/sar/sarampion.php", timeout=NAV_TIMEOUT, wait_until="domcontentloaded")
            page.wait_for_timeout(1000)
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
            page.wait_for_timeout(1500)
            logger.info("Clicked create new form button")
        else:
            self.errors.append("'Crear Ficha Nueva' button not found")
            self._screenshot(page, "nav_create_error")
            return False

        self._screenshot(page, "nav_form_ready")
        return True

    # ── Duplicate check ──────────────────────────────────────────────────

    def _parse_date_loose(self, text: str) -> Optional[datetime]:
        """Try to parse a date string in common formats. Returns None on failure."""
        if not text:
            return None
        text = text.strip()
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        return None

    def check_duplicate_in_mspas(self, page, data: dict) -> dict:
        """Check if a patient already has a ficha in MSPAS (2-level detection).

        Searches by apellidos + nombres on the sarampion list page, then
        verifies any name match also has a fecha_notificacion within the same
        month AND matching departamento. Returns a dict with detection level:

        - {"status": "clean"} — no match found
        - {"status": "confirmed_duplicate", "details": "..."} — name+date+depto match
        - {"status": "possible_duplicate", "details": "..."} — name-only match

        Must be called BEFORE navigate_to_form() clicks "Crear Ficha Nueva".
        """
        nombres = (data.get("nombres") or "").strip()
        apellidos = (data.get("apellidos") or "").strip()
        our_fecha_str = (data.get("fecha_notificacion") or "").strip()
        our_fecha = self._parse_date_loose(our_fecha_str)
        our_depto = (data.get("departamento_residencia") or "").strip().upper()

        if not apellidos and not nombres:
            logger.warning("Duplicate check skipped: no name data available")
            return {"status": "clean"}

        logger.info("Checking for duplicate in MSPAS: %s %s", apellidos, nombres)

        try:
            # Navigate to the sarampion list page
            base_url = EPIWEB_URL.rstrip("/")
            page.goto(
                f"{base_url}/fichas/paginas/sar/sarampion.php",
                timeout=NAV_TIMEOUT,
                wait_until="domcontentloaded",
            )
            page.wait_for_timeout(1000)

            # Look for search/filter fields on the list page
            # Try apellidos search field
            apellidos_input = page.query_selector(
                'input[name="apellidos"], input[name="txt_apellidos"], '
                'input[name="apellido"], input#apellidos, input#txt_apellidos, '
                'input[placeholder*="pellido"]'
            )
            nombres_input = page.query_selector(
                'input[name="nombres"], input[name="txt_nombres"], '
                'input[name="nombre"], input#nombres, input#txt_nombres, '
                'input[placeholder*="ombre"]'
            )

            filled_any = False

            if apellidos_input and apellidos:
                apellidos_input.fill("")
                apellidos_input.fill(apellidos)
                filled_any = True
                logger.debug("Filled apellidos search: %s", apellidos)

            if nombres_input and nombres:
                nombres_input.fill("")
                nombres_input.fill(nombres)
                filled_any = True
                logger.debug("Filled nombres search: %s", nombres)

            if not filled_any:
                # No search fields found; try a general search box
                general_search = page.query_selector(
                    'input[type="search"], input[name="search"], '
                    'input[name="buscar"], input#buscar, '
                    'input.form-control[placeholder*="uscar"]'
                )
                if general_search:
                    search_term = f"{apellidos} {nombres}".strip()
                    general_search.fill("")
                    general_search.fill(search_term)
                    filled_any = True
                    logger.debug("Filled general search: %s", search_term)

            if not filled_any:
                logger.warning(
                    "Duplicate check: no search fields found on list page"
                )
                self._screenshot(page, "dup_check_no_fields")
                return {"status": "clean"}

            # Click search/filter button
            search_btn = page.query_selector(
                'button:has-text("Buscar"), input[type="submit"][value*="Buscar"], '
                'button:has-text("Filtrar"), button:has-text("buscar"), '
                'a:has-text("Buscar"), button.btn-primary[type="submit"], '
                'button#btn_buscar, input#btn_buscar'
            )
            if search_btn:
                search_btn.click()
            else:
                # Try pressing Enter on the last filled input
                if apellidos_input and apellidos:
                    apellidos_input.press("Enter")
                elif nombres_input and nombres:
                    nombres_input.press("Enter")

            # Wait for search results
            page.wait_for_timeout(3000)
            self._wait_for_ajax(page, 2000)

            self._screenshot(page, "dup_check_results")

            # Check results table for matching rows
            # Look for data rows in the results table (skip header row)
            result_rows = page.query_selector_all(
                'table tbody tr, table tr:not(:first-child)'
            )

            # Filter out header rows and empty rows
            data_rows = []
            for row in result_rows:
                text = (row.text_content() or "").strip()
                # Skip header-like rows and empty rows
                if not text or text.lower().startswith("no.") or "apellido" in text.lower():
                    continue
                # Skip "no results" message rows
                if "no se encontr" in text.lower() or "sin resultado" in text.lower():
                    continue
                data_rows.append(row)

            if data_rows:
                # Found potential matches — check if names actually match
                search_apellidos = apellidos.upper()
                search_nombres = nombres.upper()

                for row in data_rows:
                    row_text = (row.text_content() or "").upper()
                    # Check if both apellidos and nombres appear in the row
                    apellidos_match = search_apellidos and search_apellidos in row_text
                    nombres_match = search_nombres and search_nombres in row_text

                    if apellidos_match and nombres_match:
                        # Level 1 check: try to confirm with date + departamento
                        row_cells = row.query_selector_all("td")
                        row_fecha = None
                        row_depto = ""
                        for cell in row_cells:
                            cell_text = (cell.text_content() or "").strip()
                            # Try to extract a date
                            if not row_fecha:
                                parsed = self._parse_date_loose(cell_text)
                                if parsed:
                                    row_fecha = parsed
                                    continue
                            # Try to detect departamento (all-caps text, no digits)
                            upper_text = cell_text.upper()
                            if (len(cell_text) > 3 and not any(c.isdigit() for c in cell_text)
                                    and upper_text not in (search_apellidos, search_nombres)):
                                if not row_depto:
                                    row_depto = upper_text

                        # Determine match level
                        same_month = False
                        if row_fecha and our_fecha:
                            same_month = (row_fecha.year == our_fecha.year
                                          and row_fecha.month == our_fecha.month)

                        depto_match = False
                        if row_depto and our_depto:
                            depto_match = (row_depto in our_depto or our_depto in row_depto)

                        if same_month and depto_match:
                            # LEVEL 1: Confirmed duplicate — name + date + depto all match
                            details = (
                                f"Nombre+fecha+depto coinciden: {apellidos} {nombres}, "
                                f"fecha MSPAS={row_fecha.strftime('%d/%m/%Y')} vs nuestro={our_fecha_str}, "
                                f"depto MSPAS={row_depto} vs nuestro={our_depto}"
                            )
                            logger.warning(
                                "CONFIRMED DUPLICATE in MSPAS: %s", details,
                            )
                            self._screenshot(page, "dup_check_CONFIRMED")
                            return {"status": "confirmed_duplicate", "details": details}

                        elif same_month and not row_depto:
                            # Date matches but no depto visible — confirmed (conservative)
                            details = (
                                f"Nombre+fecha coinciden (depto no visible): {apellidos} {nombres}, "
                                f"fecha MSPAS={row_fecha.strftime('%d/%m/%Y')} vs nuestro={our_fecha_str}"
                            )
                            logger.warning(
                                "CONFIRMED DUPLICATE in MSPAS (no depto): %s", details,
                            )
                            self._screenshot(page, "dup_check_CONFIRMED")
                            return {"status": "confirmed_duplicate", "details": details}

                        else:
                            # LEVEL 2: Name matches but date/depto don't confirm
                            date_info = (
                                f"fecha MSPAS={row_fecha.strftime('%d/%m/%Y')}" if row_fecha
                                else "fecha no visible"
                            )
                            depto_info = (
                                f"depto MSPAS={row_depto}" if row_depto
                                else "depto no visible"
                            )
                            details = (
                                f"Solo nombre coincide: {apellidos} {nombres}, "
                                f"{date_info} vs nuestro={our_fecha_str}, "
                                f"{depto_info} vs nuestro={our_depto}"
                            )
                            logger.warning(
                                "POSSIBLE DUPLICATE in MSPAS: %s", details,
                            )
                            self._screenshot(page, "dup_check_POSSIBLE")
                            return {"status": "possible_duplicate", "details": details}

                    # Partial match: if only apellidos was searched and matches
                    if apellidos_match and not nombres:
                        details = f"Solo apellidos coinciden: {apellidos}"
                        logger.warning(
                            "POSSIBLE DUPLICATE in MSPAS (apellidos only): %s",
                            apellidos,
                        )
                        self._screenshot(page, "dup_check_POSSIBLE")
                        return {"status": "possible_duplicate", "details": details}

                logger.info(
                    "Search returned %d rows but no exact name match found",
                    len(data_rows),
                )

            logger.info("No duplicate found in MSPAS for: %s %s", apellidos, nombres)
            return {"status": "clean"}

        except Exception as e:
            logger.warning("Duplicate check failed (proceeding anyway): %s", e)
            self._screenshot(page, "dup_check_error")
            return {"status": "clean"}

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
            self._safe_select(page, '#cbox_genero, select[name="cbox_genero"]', data["genero"], "genero",
                              code=data.get("genero_code", ""))

        # Ethnicity
        if data.get("etnia"):
            self._safe_select(page, '#cbox_etnia, select[name="cbox_etnia"]', data["etnia"], "etnia",
                              code=data.get("etnia_code", ""))

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
            self._safe_select(page, '#cbox_escolar, select[name="cbox_escolar"]', data["escolaridad"], "escolaridad",
                              code=data.get("escolaridad_code", ""))

        # Department → Municipality → Poblado (cascading AJAX selects)
        if data.get("departamento"):
            self._safe_select(
                page,
                '#cbox_iddep, select[name="cbox_iddep"]',
                data["departamento"],
                "departamento",
                code=data.get("departamento_code", ""),
            )
            # CRITICAL: Wait for municipios to load via AJAX
            logger.info("Waiting for municipios AJAX load...")
            self._wait_for_ajax(page, 1200)

        if data.get("municipio"):
            self._safe_select(
                page,
                '#cbox_idmun, select[name="cbox_idmun"]',
                data["municipio"],
                "municipio"
            )
            # Wait for poblados to load via AJAX
            logger.info("Waiting for poblados AJAX load...")
            self._wait_for_ajax(page, 1000)

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
                "fuente_notificacion",
                code=data.get("fuente_noti_code", ""),
            )

        # Conditional "otra fuente" text (visible when fuente = Otra)
        if data.get("fuente_otros"):
            self._safe_fill(page, '#fuente_otros, input[name="fuente_otros"]', data['fuente_otros'], 'fuente_otros')

        # Active search
        if data.get("busqueda_activa"):
            self._safe_select(
                page,
                '#slc_activa, select[name="slc_activa"]',
                data["busqueda_activa"],
                "busqueda_activa",
                code=data.get("busqueda_activa_code", ""),
            )

        # Conditional "otra busqueda" text (visible when busqueda = Otras)
        if data.get("txt_activa_otros"):
            self._safe_fill(page, '#txt_activa_otros, input[name="txt_activa_otros"]', data['txt_activa_otros'], 'txt_activa_otros')

        # Eruption type/site
        if data.get("sitio_erupcion"):
            self._safe_select(
                page,
                '#cbox_erupciones, select[name="cbox_erupciones"]',
                data["sitio_erupcion"],
                "sitio_erupcion",
                code=data.get("sitio_erupcion_code", ""),
            )

        # Conditional "otra erupcion" text (visible when sitio = Otro)
        if data.get("txt_otra_erup"):
            self._safe_fill(page, '#txt_otra_erup, input[name="txt_otra_erup"]', data['txt_otra_erup'], 'txt_otra_erup')

        # Temperature
        self._safe_fill(
            page,
            '#txt_temperatura, input[name="txt_temperatura"]',
            data.get("temperatura", ""),
            "temperatura"
        )

        # Clinical signs (radio buttons: SI/NO)
        # Scroll signs section into view first to ensure clicks register
        page.evaluate("""
            () => {
                // Try to find the signs section and scroll it into view
                const labels = ['tos', 'coriza', 'conjuntivitis'];
                for (const name of labels) {
                    const el = document.querySelector('input[name="' + name + '"]')
                        || document.querySelector('input[name="rad_' + name + '"]');
                    if (el) { el.scrollIntoView({block: 'center'}); break; }
                }
            }
        """)
        page.wait_for_timeout(300)

        for sign_name, key in [
            ("tos", "signo_tos"),
            ("coriza", "signo_coriza"),
            ("conjuntivitis", "signo_conjuntivitis"),
            ("adenopatias", "signo_adenopatias"),
            ("artralgia", "signo_artralgia"),
            ("fiebre", "fiebre"),  # Fiebre radio in MSPAS signs grid
        ]:
            val = data.get(key, "")
            if val:
                filled = False
                # Try common MSPAS naming patterns
                for name_pattern in [sign_name, f"rad_{sign_name}", f"signo_{sign_name}"]:
                    el = page.query_selector(f'input[name="{name_pattern}"]')
                    if el:
                        # Scroll to the specific radio before clicking
                        page.evaluate(f'document.querySelector(\'input[name="{name_pattern}"]\')?.scrollIntoView({{block: "center"}})')
                        page.wait_for_timeout(100)
                        self._safe_radio(page, name_pattern, val, sign_name)
                        filled = True
                        break
                if not filled:
                    # JS fallback: find radio by name patterns and click directly
                    js_filled = page.evaluate(f"""
                        (val) => {{
                            const names = ['{sign_name}', 'rad_{sign_name}', 'signo_{sign_name}'];
                            const valMap = {{'SI': ['SI', 'S', 's', '1'], 'NO': ['NO', 'N', 'n', '2']}};
                            const tryVals = valMap[val.toUpperCase()] || [val];
                            for (const name of names) {{
                                for (const v of tryVals) {{
                                    const radio = document.querySelector('input[name="' + name + '"][value="' + v + '"]');
                                    if (radio) {{
                                        radio.scrollIntoView({{block: 'center'}});
                                        radio.checked = true;
                                        radio.dispatchEvent(new Event('change', {{bubbles: true}}));
                                        radio.dispatchEvent(new Event('click', {{bubbles: true}}));
                                        return true;
                                    }}
                                }}
                            }}
                            return false;
                        }}
                    """, val)
                    if js_filled:
                        logger.debug("Radio %s = %s (via JS fallback)", sign_name, val)
                    else:
                        # Last resort: try _safe_radio with original name
                        self._safe_radio(page, sign_name, val, sign_name)

        # Debug: log actual state of sign radios after filling
        sign_debug = page.evaluate("""
            () => {
                const names = ['tos', 'coriza', 'conjuntivitis', 'adenopatias', 'artralgia',
                               'rad_tos', 'rad_coriza', 'rad_conjuntivitis', 'rad_adenopatias', 'rad_artralgia'];
                const result = {};
                for (const name of names) {
                    const radios = document.querySelectorAll('input[name="' + name + '"]');
                    if (radios.length > 0) {
                        const info = [];
                        radios.forEach(r => info.push({
                            value: r.value, checked: r.checked, disabled: r.disabled,
                            visible: r.offsetParent !== null
                        }));
                        result[name] = info;
                    }
                }
                return result;
            }
        """)
        logger.debug("Signs radio state after fill: %s", json.dumps(sign_debug))

        # Vaccination section
        if data.get("vacunado"):
            self._safe_radio(page, "vacunado", data["vacunado"], "vacunado")

            if data["vacunado"] == "SI":
                page.wait_for_timeout(1000)
                # Force-enable vaccine selects in case the radio click didn't trigger JS
                page.evaluate("""
                    () => {
                        ['cb_fuente', 'cb_vacuna', 'no_dosis', 'fecha_ult_dosis'].forEach(id => {
                            const el = document.getElementById(id) || document.querySelector('[name="' + id + '"]');
                            if (el) el.removeAttribute('disabled');
                        });
                    }
                """)

                if data.get("fuente_vacuna"):
                    self._safe_select(
                        page,
                        '#cb_fuente, select[name="cb_fuente"]',
                        data["fuente_vacuna"],
                        "fuente_vacuna",
                        code=data.get("fuente_vacuna_code", ""),
                    )

                if data.get("tipo_vacuna"):
                    self._safe_select(
                        page,
                        '#cb_vacuna, select[name="cb_vacuna"]',
                        data["tipo_vacuna"],
                        "tipo_vacuna",
                        code=data.get("tipo_vacuna_code", ""),
                    )

                if data.get("no_dosis"):
                    self._safe_select(
                        page,
                        '#no_dosis, select[name="no_dosis"]',
                        data["no_dosis"],
                        "no_dosis",
                        code=data.get("no_dosis_code", ""),
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

        # Vaccine observations
        if data.get("observaciones_vacuna"):
            self._safe_fill(page, '#observaciones, input[name="observaciones"]', data['observaciones_vacuna'], 'observaciones_vacuna')

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
                "condicion_egreso",
                code=data.get("condicion_egreso_code", ""),
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

        # Death fields (conditional on condicion_egreso = Muerto/Fallecido)
        if data.get("txt_fecha_defuncion"):
            self._safe_fill(page, '#txt_fecha_defuncion, input[name="txt_fecha_defuncion"]', data['txt_fecha_defuncion'], 'fecha_defuncion')
        if data.get("txt_medic_defuncion"):
            self._safe_fill(page, '#txt_medic_defuncion, input[name="txt_medic_defuncion"]', data['txt_medic_defuncion'], 'medico_defuncion')

        # Pregnancy in clinical tab — only attempt if patient is female and
        # the radio is visible (some MSPAS forms duplicate this field here)
        if data.get("embarazada") and data.get("genero", "").upper() in ("F", "FEMENINO", "MUJER", "2"):
            try:
                el = page.query_selector('input[name="rad_embarazada"]')
                if el and el.is_visible():
                    self._safe_radio(page, "rad_embarazada", data["embarazada"], "embarazada_clinica")
            except Exception:
                pass  # Not critical — already set in tab2

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

        # Contact with sick person (always visible, not conditional on viajo)
        _enfermo = data.get("rad_enfermo") or data.get("contacto_enfermo", "")
        if _enfermo:
            self._safe_radio(page, "rad_enfermo", _enfermo, "contacto_enfermo")

        # Contact with pregnant woman
        _cont_emb = data.get("rad_cont_emb") or data.get("contacto_embarazada", "")
        if _cont_emb:
            self._safe_radio(page, "rad_cont_emb", _cont_emb, "contacto_embarazada")

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

                # Suero checkbox + date (try multiple MSPAS naming patterns)
                if data.get("muestra_suero"):
                    self._safe_checkbox(
                        page,
                        '#chk_suero, input[name="chk_suero"], #suero, input[name="suero"], input[type="checkbox"][value="suero"]',
                        True,
                        "muestra_suero"
                    )
                    if data.get("muestra_suero_fecha"):
                        self._safe_fill(
                            page,
                            '#fecha_suero, input[name="fecha_suero"], #suero_fecha, input[name="suero_fecha"]',
                            data["muestra_suero_fecha"],
                            "suero_fecha"
                        )

                # Hisopado checkbox + date
                if data.get("muestra_hisopado"):
                    self._safe_checkbox(
                        page,
                        '#chk_HN, input[name="chk_HN"], #hisopado, input[name="hisopado"], input[type="checkbox"][value="hisopado"]',
                        True,
                        "muestra_hisopado"
                    )
                    if data.get("muestra_hisopado_fecha"):
                        self._safe_fill(
                            page,
                            '#fecha_HN, input[name="fecha_HN"], #hisopado_fecha, input[name="hisopado_fecha"]',
                            data["muestra_hisopado_fecha"],
                            "hisopado_fecha"
                        )

                # Orina checkbox + date
                if data.get("muestra_orina"):
                    self._safe_checkbox(
                        page,
                        '#chk_orina, input[name="chk_orina"], #orina, input[name="orina"], input[type="checkbox"][value="orina"]',
                        True,
                        "muestra_orina"
                    )
                    if data.get("muestra_orina_fecha"):
                        self._safe_fill(
                            page,
                            '#fecha_orina, input[name="fecha_orina"], #orina_fecha, input[name="orina_fecha"]',
                            data["muestra_orina_fecha"],
                            "orina_fecha"
                        )

                # Otra muestra checkbox + description + date
                _chk_otra = data.get("chk_otra_m", "")
                if _chk_otra and str(_chk_otra).upper() in ('SI', 'S', '1', 'TRUE'):
                    self._safe_checkbox(page, '#chk_otra_m, input[name="chk_otra_m"]', True, 'otra_muestra')
                    if data.get("txt_otra_muestra"):
                        self._safe_fill(page, '#txt_otra_muestra, input[name="txt_otra_muestra"]', data['txt_otra_muestra'], 'otra_muestra_desc')
                    if data.get("fecha_otra_m"):
                        self._safe_fill(page, '#fecha_otra_m, input[name="fecha_otra_m"]', data['fecha_otra_m'], 'fecha_otra_muestra')

        # Antigen/test type
        if data.get("antigeno"):
            self._safe_select(
                page,
                '#slc_antigeno, select[name="slc_antigeno"]',
                data["antigeno"],
                "antigeno",
                code=data.get("antigeno_code", ""),
            )

        # Otro antigeno (conditional on antigeno = Otros)
        if data.get("txt_otro_ant"):
            self._safe_fill(page, '#txt_otro_ant, input[name="txt_otro_ant"]', data['txt_otro_ant'], 'otro_antigeno')

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
                "resultado_lab",
                code=data.get("resultado_lab_code", ""),
            )

        # ── Lab results table row: fill top selects then click "+" to add row ──
        # The MSPAS form has dropdowns (slc_muestras, slc_pruebas, slc_antigeno,
        # fecha_recep, fecha_resul_lab, slc_resul_lab) above a dynamic table.
        # Clicking the "+" button (agregar_fila) adds the current dropdown values
        # as a new row in the results table.
        # We attempt to add a row if we have antigeno + resultado data filled.
        has_lab_row_data = (
            data.get("antigeno_code") and data.get("resultado_lab_code")
        )
        logger.debug("Lab row data: antigeno_code=%s resultado_lab_code=%s",
                     data.get("antigeno_code"), data.get("resultado_lab_code"))
        if has_lab_row_data:
            try:
                # Determine muestra type from checkboxes (Suero=1, Hisopado=2, Orina=3)
                muestra_code = ""
                if data.get("muestra_suero"):
                    muestra_code = "1"  # Suero
                elif data.get("muestra_hisopado"):
                    muestra_code = "2"  # Hisopado Nasofaríngeo
                elif data.get("muestra_orina"):
                    muestra_code = "3"  # Orina

                # The slc_muestras and slc_pruebas dropdowns are populated dynamically
                # by MSPAS JS when checkboxes are checked. By the time we get here,
                # they may still be empty. We inject the options directly if needed,
                # then fill all selects and click the add button.

                # Muestra type names matching checkbox IDs
                _MUESTRA_MAP = {
                    "1": "Suero",
                    "2": "Hisopado Nasofaringeo",
                    "3": "Orina",
                }
                _PRUEBA_MAP = {
                    "1": "IgM ELISA",
                }

                muestra_text = _MUESTRA_MAP.get(muestra_code, "Suero")

                row_added = page.evaluate("""
                    (params) => {
                        const {muestra, muestraText, antigeno, resultado, fechaRecep, fechaResul} = params;

                        // Step 1: Ensure slc_muestras has options (inject if empty)
                        const selMuestra = document.querySelector('#slc_muestras, select[name="slc_muestras"]');
                        if (selMuestra) {
                            const hasOptions = Array.from(selMuestra.options).some(o => o.value !== '');
                            if (!hasOptions) {
                                // Inject muestra options based on checked checkboxes
                                const muestras = [
                                    {id: 'chk_suero', value: '1', text: 'Suero'},
                                    {id: 'chk_HN', value: '2', text: 'Hisopado Nasofaringeo'},
                                    {id: 'chk_orina', value: '3', text: 'Orina'},
                                ];
                                for (const m of muestras) {
                                    const chk = document.querySelector('#' + m.id) || document.querySelector('input[name="' + m.id + '"]');
                                    if (chk && chk.checked) {
                                        const opt = document.createElement('option');
                                        opt.value = m.value;
                                        opt.textContent = m.text;
                                        selMuestra.appendChild(opt);
                                    }
                                }
                            }
                            if (muestra) {
                                selMuestra.value = muestra;
                            } else {
                                // Select first non-empty option
                                for (const opt of selMuestra.options) {
                                    if (opt.value) { selMuestra.value = opt.value; break; }
                                }
                            }
                            selMuestra.dispatchEvent(new Event('change', {bubbles: true}));
                        }

                        // Step 2: Ensure slc_pruebas has options (inject IgM ELISA if empty)
                        const selPrueba = document.querySelector('#slc_pruebas, select[name="slc_pruebas"]');
                        if (selPrueba) {
                            const hasOptions = Array.from(selPrueba.options).some(o => o.value !== '');
                            if (!hasOptions) {
                                const opt = document.createElement('option');
                                opt.value = '1';
                                opt.textContent = 'IgM ELISA';
                                selPrueba.appendChild(opt);
                            }
                            // Select first non-empty
                            for (const opt of selPrueba.options) {
                                if (opt.value) { selPrueba.value = opt.value; break; }
                            }
                            selPrueba.dispatchEvent(new Event('change', {bubbles: true}));
                        }

                        // Step 3: Antigeno
                        const selAntigeno = document.querySelector('#slc_antigeno, select[name="slc_antigeno"]');
                        if (selAntigeno && antigeno) {
                            selAntigeno.value = antigeno;
                            selAntigeno.dispatchEvent(new Event('change', {bubbles: true}));
                        }

                        // Step 4: Dates
                        if (fechaRecep) {
                            const el = document.querySelector('#fecha_recep, input[name="fecha_recep"]');
                            if (el) { el.removeAttribute('readonly'); el.value = fechaRecep; }
                        }
                        if (fechaResul) {
                            const el = document.querySelector('#fecha_resul_lab, input[name="fecha_resul_lab"]');
                            if (el) { el.removeAttribute('readonly'); el.value = fechaResul; }
                        }

                        // Step 5: Result
                        const selResult = document.querySelector('#slc_resul_lab, select[name="slc_resul_lab"]');
                        if (selResult && resultado) {
                            selResult.value = resultado;
                            selResult.dispatchEvent(new Event('change', {bubbles: true}));
                        }

                        // Step 6: Click add button
                        const addBtn = document.querySelector(
                            'button[onclick*="agregar_fila"]'
                            + ', input[type="button"][onclick*="agregar_fila"]'
                            + ', a[onclick*="agregar_fila"]'
                        );
                        if (addBtn) {
                            addBtn.click();
                            return {ok: true, method: 'button',
                                muestra_val: selMuestra ? selMuestra.value : 'N/A',
                                prueba_val: selPrueba ? selPrueba.value : 'N/A'};
                        }
                        return {ok: false, error: 'no add button'};
                    }
                """, {
                    "muestra": muestra_code,
                    "muestraText": muestra_text,
                    "antigeno": data.get("antigeno_code", ""),
                    "resultado": data.get("resultado_lab_code", ""),
                    "fechaRecep": data.get("fecha_recep_lab", ""),
                    "fechaResul": data.get("fecha_resul_lab", ""),
                })
                logger.debug("Lab row add result: %s", row_added)

                if row_added and row_added.get("ok"):
                    page.wait_for_timeout(500)
                    logger.info("Lab results table: row add attempted")
                else:
                    self.errors.append(f"Lab results table: {row_added}")
            except Exception as e:
                logger.warning("Error adding lab results table row: %s", e)
                self.errors.append(f"Lab results table row: {e}")

        self._screenshot(page, "tab5_laboratorio")

    # ── Tab 6: Clasificacion Final ────────────────────────────────────────

    def fill_tab6_clasificacion(self, page, data: dict):
        """Fill Tab 6 — Clasificacion Final."""
        logger.info("Filling Tab 6: Clasificacion Final")
        self._click_tab(page, "Clasific")  # partial match: "Clasificación"

        # Ensure the tab content is actually visible (MSPAS uses display:none on inactive tabs)
        page.evaluate("""
            () => {
                // Force-show the clasificacion tab content
                const allPanes = document.querySelectorAll('.tab-pane');
                allPanes.forEach(p => {
                    if (p.textContent.includes('Clasificaci') || p.querySelector('#slc_clas_final')) {
                        p.classList.add('active', 'in', 'show');
                        p.style.display = 'block';
                    }
                });
                // Also ensure the select is scrolled into view
                const sel = document.querySelector('#slc_clas_final, select[name="slc_clas_final"]');
                if (sel) sel.scrollIntoView({block: 'center'});
            }
        """)
        page.wait_for_timeout(500)

        # Classification select — MSPAS uses TEXT values not numeric codes:
        #   "Sarampión", "Rubéola", "Descartado" (NOT "1", "2", "3")
        # Our CLASIFICACION_FINAL_CODES maps to "1"/"2"/"3" which don't match.
        # We need to map code -> actual MSPAS option text value.
        _CLAS_CODE_TO_TEXT = {
            "1": "Sarampión",
            "2": "Rubéola",
            "3": "Descartado",
        }
        if data.get("clasificacion_code"):
            code = data["clasificacion_code"]
            clas_text = _CLAS_CODE_TO_TEXT.get(code, "")

            # Strategy 1: Select by label text (most reliable for text-valued options)
            if clas_text:
                try:
                    page.select_option(
                        '#slc_clas_final, select[name="slc_clas_final"]',
                        label=clas_text, timeout=3000
                    )
                    logger.info("slc_clas_final selected by label: '%s'", clas_text)
                except Exception as e:
                    logger.warning("slc_clas_final select_option by label failed: %s", e)

            # Verify and force via JS if needed
            actual_val = page.evaluate("""
                () => {
                    const el = document.querySelector('#slc_clas_final, select[name="slc_clas_final"]');
                    return el ? el.value : '';
                }
            """)
            if not actual_val or actual_val == "":
                # JS fallback: set value by matching option text
                page.evaluate("""
                    (params) => {
                        const {code, text} = params;
                        const el = document.querySelector('#slc_clas_final')
                            || document.querySelector('select[name="slc_clas_final"]');
                        if (!el) return;
                        el.removeAttribute('disabled');

                        // Try setting by text value directly
                        if (text) {
                            el.value = text;
                            if (el.value === text) {
                                el.dispatchEvent(new Event('change', {bubbles: true}));
                                if (typeof jQuery !== 'undefined') jQuery(el).val(text).trigger('change');
                                return;
                            }
                        }

                        // Try numeric code
                        el.value = code;
                        if (el.value === code) {
                            el.dispatchEvent(new Event('change', {bubbles: true}));
                            if (typeof jQuery !== 'undefined') jQuery(el).val(code).trigger('change');
                            return;
                        }

                        // Fallback: iterate options and match by partial text
                        const opts = el.querySelectorAll('option');
                        for (const opt of opts) {
                            const optText = opt.textContent.trim();
                            if (text && optText.includes(text.substring(0, 5))) {
                                el.value = opt.value;
                                el.dispatchEvent(new Event('change', {bubbles: true}));
                                if (typeof jQuery !== 'undefined') jQuery(el).val(opt.value).trigger('change');
                                return;
                            }
                        }
                    }
                """, {"code": code, "text": clas_text})
                logger.info("slc_clas_final forced via JS with text='%s'", clas_text)

            page.wait_for_timeout(500)

            # Conditional fields based on classification
            clas_code = data["clasificacion_code"]

            # If confirmed (Sarampion=1 or Rubeola=2): show confirmado_por + fuente_infeccion
            if clas_code in ("1", "2"):
                if data.get("confirmado_por_code"):
                    self._safe_select(
                        page,
                        '#slc_confirmado, select[name="slc_confirmado"]',
                        "",
                        "confirmado_por",
                        code=data["confirmado_por_code"],
                    )
                if data.get("fuente_infeccion_code"):
                    self._safe_select(
                        page,
                        '#slc_fuente_infect, select[name="slc_fuente_infect"]',
                        "",
                        "fuente_infeccion",
                        code=data["fuente_infeccion_code"],
                    )

            # If discarded (3): show criterio_descarte
            if clas_code == "3" and data.get("criterio_descarte_code"):
                self._safe_select(
                    page,
                    '#slc_crit_desc, select[name="slc_crit_desc"]',
                    "",
                    "criterio_descarte",
                    code=data["criterio_descarte_code"],
                )

        # Classification date
        if data.get("clasificacion_fecha"):
            page.evaluate("""
                () => {
                    const el = document.querySelector('#txt_fecha_final, input[name="txt_fecha_final"]');
                    if (el) { el.removeAttribute('readonly'); }
                }
            """)
            self._safe_fill(
                page,
                '#txt_fecha_final, input[name="txt_fecha_final"]',
                data["clasificacion_fecha"],
                "fecha_clasificacion"
            )

        # Investigator name
        if data.get("investigador_nombre"):
            self._safe_fill(
                page,
                '#txt_nom_invest, input[name="txt_nom_invest"]',
                data["investigador_nombre"],
                "investigador_nombre"
            )

        # Investigator position
        if data.get("investigador_cargo"):
            self._safe_fill(
                page,
                '#txt_cargo_invest, input[name="txt_cargo_invest"]',
                data["investigador_cargo"],
                "investigador_cargo"
            )

        # Classification observations — try multiple selectors since MSPAS
        # form may use different field names/types across versions.
        # PERF: Use JS evaluate to fill (avoids click timeout on hidden
        # #observaciones input that exists but is not interactable — saved 30s).
        if data.get("clasificacion_observaciones"):
            obs_filled = False
            obs_text = data["clasificacion_observaciones"]

            # Fast path: fill via JS (avoids click timeout on hidden elements)
            try:
                obs_filled = page.evaluate("""
                    (text) => {
                        // Try specific clasificacion obs fields first
                        const selectors = [
                            '#observaciones_clas', 'textarea[name="observaciones_clas"]',
                            'input[name="observaciones_clas"]',
                        ];
                        for (const sel of selectors) {
                            const el = document.querySelector(sel);
                            if (el) {
                                el.value = text;
                                el.dispatchEvent(new Event('change', {bubbles: true}));
                                return true;
                            }
                        }
                        // Fallback: last textarea on page
                        const textareas = document.querySelectorAll('textarea');
                        if (textareas.length > 0) {
                            const ta = textareas[textareas.length - 1];
                            ta.value = text;
                            ta.dispatchEvent(new Event('change', {bubbles: true}));
                            return true;
                        }
                        return false;
                    }
                """, obs_text)
                if obs_filled:
                    logger.debug("Filled observaciones via JS evaluate (fast path)")
            except Exception as e:
                logger.debug("JS observaciones fill failed: %s", e)

            if not obs_filled:
                msg = "Could not find observaciones field in Tab 6"
                logger.warning(msg)
                self.errors.append(msg)

        # Responsible for classification
        if data.get("clasificacion_responsable"):
            self._safe_fill(
                page,
                '#txt_nom_resp_clas, input[name="txt_nom_resp_clas"]',
                data["clasificacion_responsable"],
                "responsable_clasificacion"
            )

        self._screenshot(page, "tab6_clasificacion")

    # ── Submit ───────────────────────────────────────────────────────────

    def submit_form(self, page) -> dict:
        """Click Guardar and capture result. ONLY called in PRODUCTION_MODE."""
        logger.info("PRODUCTION MODE: Submitting form...")

        # Double-check safety gate
        if not PRODUCTION_MODE:
            logger.error("submit_form() called but PRODUCTION_MODE is False. Aborting.")
            return self._enrich_result({
                "success": False,
                "production_mode": False,
                "submitted": False,
                "mspas_ficha_id": None,
                "screenshots": self.screenshots,
                "errors": ["submit_form() called without MSPAS_PRODUCTION_MODE=true"],
                "duration_seconds": time.time() - self._start_time,
            })

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
            return self._enrich_result({
                "success": False,
                "production_mode": True,
                "submitted": False,
                "mspas_ficha_id": None,
                "screenshots": self.screenshots,
                "errors": self.errors,
                "duration_seconds": time.time() - self._start_time,
            })

        guardar_btn.click()
        page.wait_for_timeout(3000)

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

        return self._enrich_result({
            "success": submitted_ok,
            "production_mode": True,
            "submitted": True,
            "mspas_ficha_id": mspas_ficha_id,
            "screenshots": self.screenshots,
            "errors": self.errors,
            "duration_seconds": time.time() - self._start_time,
        })

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

        # Create per-record screenshot directory
        raw_id = record.get('registro_id', 'unknown')
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', str(raw_id))
        self._record_screenshot_dir = os.path.join(SCREENSHOT_DIR, safe_id)
        os.makedirs(self._record_screenshot_dir, exist_ok=True)

        mapped = map_record_to_mspas(record)

        # Build extra data to include in every result for UI display
        self._mapped_data = {k: v for k, v in mapped.items() if v}
        self._record_data = {
            "registro_id": record.get("registro_id", ""),
            "nombres": record.get("nombres", ""),
            "apellidos": record.get("apellidos", ""),
            "afiliacion": record.get("afiliacion", ""),
            "departamento_residencia": record.get("departamento_residencia", ""),
            "municipio_residencia": record.get("municipio_residencia", ""),
            "fecha_notificacion": record.get("fecha_notificacion", ""),
            "clasificacion_caso": record.get("clasificacion_caso", ""),
            "unidad_medica": record.get("unidad_medica", ""),
            "sexo": record.get("sexo", ""),
            "edad_anios": record.get("edad_anios", ""),
        }

        logger.info(
            "Processing record. Production mode: %s. Fields mapped: %d",
            PRODUCTION_MODE, sum(1 for v in mapped.values() if v)
        )

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return self._enrich_result({
                "success": False,
                "production_mode": PRODUCTION_MODE,
                "submitted": False,
                "mspas_ficha_id": None,
                "screenshots": [],
                "errors": ["playwright not installed. Run: pip install playwright && playwright install chromium"],
                "duration_seconds": time.time() - self._start_time,
            })

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
                    return self._enrich_result({
                        "success": False,
                        "production_mode": PRODUCTION_MODE,
                        "submitted": False,
                        "mspas_ficha_id": None,
                        "screenshots": self.screenshots,
                        "errors": self.errors,
                        "duration_seconds": time.time() - self._start_time,
                    })

                # Step 2: Check for duplicates in MSPAS before creating ficha
                dup = self.check_duplicate_in_mspas(page, record)
                if dup["status"] == "confirmed_duplicate":
                    logger.warning(
                        "Confirmed duplicate in MSPAS for %s. Skipping.",
                        record.get("registro_id", "?"),
                    )
                    return self._enrich_result({
                        "success": False,
                        "production_mode": PRODUCTION_MODE,
                        "submitted": False,
                        "duplicate": True,
                        "duplicate_type": "confirmed",
                        "details": dup.get("details", ""),
                        "mspas_ficha_id": None,
                        "screenshots": self.screenshots,
                        "errors": ["Duplicado confirmado: paciente ya tiene ficha en MSPAS"],
                        "duration_seconds": time.time() - self._start_time,
                    })
                elif dup["status"] == "possible_duplicate":
                    logger.warning(
                        "Possible duplicate in MSPAS for %s. Flagging for review.",
                        record.get("registro_id", "?"),
                    )
                    return self._enrich_result({
                        "success": False,
                        "production_mode": PRODUCTION_MODE,
                        "submitted": False,
                        "duplicate": True,
                        "duplicate_type": "possible",
                        "details": dup.get("details", ""),
                        "mspas_ficha_id": None,
                        "screenshots": self.screenshots,
                        "errors": ["Posible duplicado: nombre coincide, requiere revisión humana"],
                        "duration_seconds": time.time() - self._start_time,
                    })

                # Step 3: Navigate to form
                if not self.navigate_to_form(page):
                    return self._enrich_result({
                        "success": False,
                        "production_mode": PRODUCTION_MODE,
                        "submitted": False,
                        "mspas_ficha_id": None,
                        "screenshots": self.screenshots,
                        "errors": self.errors,
                        "duration_seconds": time.time() - self._start_time,
                    })

                # Step 4: Fill all tabs (with session checks between each)
                if not self._fill_all_tabs(page, mapped):
                    return self._enrich_result({
                        "success": False, "production_mode": PRODUCTION_MODE,
                        "submitted": False, "mspas_ficha_id": None,
                        "screenshots": self.screenshots,
                        "errors": self.errors,
                        "duration_seconds": time.time() - self._start_time,
                    })

                # Step 5: Submit or stop
                # Don't submit if too many errors accumulated during form filling
                MAX_ERRORS_FOR_SUBMIT = 3
                if PRODUCTION_MODE and len(self.errors) > MAX_ERRORS_FOR_SUBMIT:
                    self.errors.append(f"Aborted: {len(self.errors)} errors exceed threshold of {MAX_ERRORS_FOR_SUBMIT}")
                    return self._enrich_result({
                        "success": False, "production_mode": True, "submitted": False,
                        "mspas_ficha_id": None, "screenshots": self.screenshots,
                        "errors": self.errors,
                        "duration_seconds": time.time() - self._start_time,
                    })

                if PRODUCTION_MODE:
                    return self.submit_form(page)
                else:
                    self._screenshot(page, "final_preview")
                    logger.info(
                        "DRY RUN complete. Form filled but NOT submitted. "
                        "Set MSPAS_PRODUCTION_MODE=true to submit."
                    )
                    return self._enrich_result({
                        "success": True,
                        "production_mode": False,
                        "submitted": False,
                        "mspas_ficha_id": None,
                        "screenshots": self.screenshots,
                        "errors": self.errors,
                        "duration_seconds": time.time() - self._start_time,
                    })

            except Exception as e:
                logger.exception("Fatal error during form processing")
                self._screenshot(page, "fatal_error")
                return self._enrich_result({
                    "success": False,
                    "production_mode": PRODUCTION_MODE,
                    "submitted": False,
                    "mspas_ficha_id": None,
                    "screenshots": self.screenshots,
                    "errors": self.errors + [f"Fatal: {e}"],
                    "duration_seconds": time.time() - self._start_time,
                })
            finally:
                context.close()
                browser.close()

    # ── Batch processing ─────────────────────────────────────────────────

    def _fill_all_tabs(self, page, mapped) -> bool:
        """Fill all 6 form tabs with session checks between each.

        Returns True if all tabs filled successfully, False if session expired
        and could not be recovered. On session recovery, restarts all tabs
        from scratch.
        """
        MAX_SESSION_RETRIES = 2
        session_retries = 0

        all_tab_fns = [
            self.fill_tab1_datos_generales,
            self.fill_tab2_datos_paciente,
            self.fill_tab3_info_clinica,
            self.fill_tab4_factores_riesgo,
            self.fill_tab5_laboratorio,
            self.fill_tab6_clasificacion,
        ]

        restart_needed = True
        while restart_needed:
            restart_needed = False
            for i, tab_fill_fn in enumerate(all_tab_fns):
                if i > 0 and not self._check_session_alive(page):
                    session_retries += 1
                    self.errors.append(
                        f"MSPAS session expired at tab {i+1}, restarting ALL tabs "
                        f"(retry {session_retries}/{MAX_SESSION_RETRIES})..."
                    )
                    if session_retries > MAX_SESSION_RETRIES:
                        self.errors.append(f"Max session retries ({MAX_SESSION_RETRIES}) exceeded")
                        return False
                    if not self.login(page):
                        self.errors.append("Re-login failed after session expiry")
                        return False
                    # Re-navigate to form
                    if not self.navigate_to_form(page):
                        self.errors.append("Re-navigation failed after session expiry")
                        return False
                    restart_needed = True
                    break  # break inner for-loop to restart from tab 1
                tab_fill_fn(page, mapped)

        return True

    def process_batch(self, records: list[dict],
                      on_complete: callable = None) -> list[dict]:
        """Process multiple records with a single browser session.

        Reuses login and browser across all records instead of launching
        a new browser per record. For N records this saves ~15s per record
        (1 login instead of N logins).

        Args:
            records: list of record dicts to process.
            on_complete: optional callback(registro_id, result_dict) called
                after each record is processed, enabling per-record state
                updates (e.g. marking sent/error in the queue immediately
                instead of waiting for the entire batch to finish).

        Returns list of result dicts (one per record), same format as
        process_record().
        """
        if not records:
            return []

        results: list[dict] = []

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return [self._enrich_result({
                "success": False,
                "production_mode": PRODUCTION_MODE,
                "submitted": False,
                "mspas_ficha_id": None,
                "screenshots": [],
                "errors": ["playwright not installed. Run: pip install playwright && playwright install chromium"],
                "duration_seconds": 0,
            }) for _ in records]

        batch_start = time.time()

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
                # Login ONCE for the entire batch
                self.screenshots = []
                self.errors = []
                if not self.login(page):
                    login_err = self.errors.copy()
                    return [self._enrich_result({
                        "success": False,
                        "production_mode": PRODUCTION_MODE,
                        "submitted": False,
                        "mspas_ficha_id": None,
                        "screenshots": self.screenshots.copy(),
                        "errors": login_err + ["Batch login failed"],
                        "duration_seconds": time.time() - batch_start,
                    }) for _ in records]

                logger.info("Batch mode: logged in. Processing %d records...", len(records))

                for i, record in enumerate(records):
                    record_start = time.time()
                    rid = record.get('registro_id', f'batch_{i}')
                    logger.info("Batch [%d/%d]: %s", i + 1, len(records), rid)

                    # Reset per-record state
                    self.screenshots = []
                    self.errors = []
                    self._start_time = record_start

                    # Setup per-record screenshot directory
                    safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', str(rid))
                    self._record_screenshot_dir = os.path.join(SCREENSHOT_DIR, safe_id)
                    os.makedirs(self._record_screenshot_dir, exist_ok=True)

                    try:
                        # Map fields
                        mapped = map_record_to_mspas(record)
                        self._mapped_data = {k: v for k, v in mapped.items() if v}
                        self._record_data = {
                            "registro_id": record.get("registro_id", ""),
                            "nombres": record.get("nombres", ""),
                            "apellidos": record.get("apellidos", ""),
                            "afiliacion": record.get("afiliacion", ""),
                            "departamento_residencia": record.get("departamento_residencia", ""),
                            "municipio_residencia": record.get("municipio_residencia", ""),
                            "fecha_notificacion": record.get("fecha_notificacion", ""),
                            "clasificacion_caso": record.get("clasificacion_caso", ""),
                            "unidad_medica": record.get("unidad_medica", ""),
                            "sexo": record.get("sexo", ""),
                            "edad_anios": record.get("edad_anios", ""),
                        }

                        # Check session is still alive; re-login if needed
                        if not self._check_session_alive(page):
                            logger.warning("Batch: session expired at record %d, re-logging in...", i + 1)
                            if not self.login(page):
                                result = self._enrich_result({
                                    "success": False,
                                    "production_mode": PRODUCTION_MODE,
                                    "submitted": False,
                                    "mspas_ficha_id": None,
                                    "screenshots": self.screenshots,
                                    "errors": self.errors + ["Re-login failed during batch"],
                                    "duration_seconds": time.time() - record_start,
                                })
                                results.append(result)
                                if on_complete:
                                    on_complete(rid, result)
                                continue

                        # Check for duplicates in MSPAS (2-level detection)
                        dup = self.check_duplicate_in_mspas(page, record)
                        if dup["status"] in ("confirmed_duplicate", "possible_duplicate"):
                            dup_type = "confirmed" if dup["status"] == "confirmed_duplicate" else "possible"
                            dup_label = "Duplicado confirmado" if dup_type == "confirmed" else "Posible duplicado"
                            logger.warning("Batch: %s detected for %s", dup_label.lower(), rid)
                            result = self._enrich_result({
                                "success": False,
                                "production_mode": PRODUCTION_MODE,
                                "submitted": False,
                                "duplicate": True,
                                "duplicate_type": dup_type,
                                "details": dup.get("details", ""),
                                "mspas_ficha_id": None,
                                "screenshots": self.screenshots,
                                "errors": [f"{dup_label}: {dup.get('details', 'paciente ya tiene ficha en MSPAS')}"],
                                "duration_seconds": time.time() - record_start,
                            })
                            results.append(result)
                            if on_complete:
                                on_complete(rid, result)
                            page.wait_for_timeout(500)
                            continue

                        # Navigate to form creation page (direct URL, skip list clicks)
                        base_url = EPIWEB_URL.rstrip("/")
                        if not self.navigate_to_form(page):
                            result = self._enrich_result({
                                "success": False,
                                "production_mode": PRODUCTION_MODE,
                                "submitted": False,
                                "mspas_ficha_id": None,
                                "screenshots": self.screenshots,
                                "errors": self.errors + ["Navigate to form failed"],
                                "duration_seconds": time.time() - record_start,
                            })
                            results.append(result)
                            if on_complete:
                                on_complete(rid, result)
                            continue

                        # Fill all 6 tabs (with session checks between each)
                        if not self._fill_all_tabs(page, mapped):
                            result = self._enrich_result({
                                "success": False,
                                "production_mode": PRODUCTION_MODE,
                                "submitted": False,
                                "mspas_ficha_id": None,
                                "screenshots": self.screenshots,
                                "errors": self.errors,
                                "duration_seconds": time.time() - record_start,
                            })
                            results.append(result)
                            if on_complete:
                                on_complete(rid, result)
                            continue

                        # Final screenshot
                        self._screenshot(page, "final_preview")

                        # Submit or dry-run
                        MAX_ERRORS_FOR_SUBMIT = 3
                        if PRODUCTION_MODE and len(self.errors) <= MAX_ERRORS_FOR_SUBMIT:
                            result = self.submit_form(page)
                        elif PRODUCTION_MODE and len(self.errors) > MAX_ERRORS_FOR_SUBMIT:
                            self.errors.append(
                                f"Aborted: {len(self.errors)} errors exceed threshold of {MAX_ERRORS_FOR_SUBMIT}"
                            )
                            result = self._enrich_result({
                                "success": False,
                                "production_mode": True,
                                "submitted": False,
                                "mspas_ficha_id": None,
                                "screenshots": self.screenshots,
                                "errors": self.errors,
                                "duration_seconds": time.time() - record_start,
                            })
                        else:
                            result = self._enrich_result({
                                "success": True,
                                "production_mode": PRODUCTION_MODE,
                                "submitted": False,
                                "mspas_ficha_id": None,
                                "screenshots": self.screenshots,
                                "errors": self.errors,
                                "duration_seconds": time.time() - record_start,
                            })

                        results.append(result)
                        if on_complete:
                            on_complete(rid, result)

                        # Navigate back to sarampion list (NOT submit again)
                        try:
                            page.goto(
                                f"{base_url}/fichas/paginas/sar/sarampion.php",
                                timeout=NAV_TIMEOUT,
                                wait_until="domcontentloaded",
                            )
                            page.wait_for_timeout(500)
                        except Exception as nav_err:
                            logger.warning("Batch: failed to navigate back after record %s: %s", rid, nav_err)

                    except Exception as e:
                        logger.error("Batch: error processing %s: %s", rid, e)
                        try:
                            self._screenshot(page, "batch_error")
                        except Exception:
                            pass
                        result = self._enrich_result({
                            "success": False,
                            "production_mode": PRODUCTION_MODE,
                            "submitted": False,
                            "mspas_ficha_id": None,
                            "screenshots": self.screenshots,
                            "errors": self.errors + [f"Fatal: {e}"],
                            "duration_seconds": time.time() - record_start,
                        })
                        results.append(result)
                        if on_complete:
                            on_complete(rid, result)

                    # Small delay between records
                    page.wait_for_timeout(500)

            finally:
                context.close()
                browser.close()

        total_time = time.time() - batch_start
        success_count = sum(1 for r in results if r.get("success"))
        logger.info(
            "Batch complete: %d/%d successful in %.1fs (avg %.1fs/record)",
            success_count, len(records), total_time,
            total_time / len(records) if records else 0,
        )

        return results


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
        "fuente_notificacion": "Pública",
        "fecha_visita_domiciliaria": "2026-03-18",
        "fecha_inicio_investigacion": "2026-03-18",
        "busqueda_activa": "Comunidad",
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
        "fuente_info_vacuna": "Verbal",
        "tipo_vacuna": "SRP Sarampión Rubéola Paperas",
        "numero_dosis_spr": "2",
        "fecha_ultima_dosis": "2020-01-10",

        "hospitalizado": "NO",
        "condicion_egreso": "",  # Not applicable when hospitalizado=NO

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
        "antigeno_prueba": "Sarampión",
        "resultado_prueba": "Negativo",
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
