"""
Cliente REST para GoData API (WHO/OPS).
Maneja autenticación OAuth, CRUD de casos, resultados de laboratorio.

GoData es la plataforma open-source de la OMS para vigilancia de brotes.
API docs: https://worldhealthorganization.github.io/godata/api-docs/
"""
import os
import logging
import time
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuración por defecto
_DEFAULT_TIMEOUT = 30


class GoDataClient:
    """Cliente para comunicación con GoData API."""

    def __init__(self, base_url=None, username=None, password=None, outbreak_id=None):
        self.base_url = (base_url or os.environ.get("GODATA_URL", "")).rstrip("/")
        self.username = username or os.environ.get("GODATA_USERNAME", "")
        self.password = password or os.environ.get("GODATA_PASSWORD", "")
        self.outbreak_id = outbreak_id or os.environ.get("GODATA_OUTBREAK_ID", "")
        self.production_mode = os.environ.get("GODATA_PRODUCTION_MODE", "false").lower() == "true"

        self._token = ""
        self._token_expires = 0
        self._session = requests.Session()
        self._session.headers["Content-Type"] = "application/json"
        self.timeout = _DEFAULT_TIMEOUT

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and self.username and self.password and self.outbreak_id)

    # ─── Autenticación ─────────────────────────────────────

    def _ensure_token(self):
        """Obtiene o renueva el token OAuth si es necesario."""
        if self._token and time.time() < self._token_expires - 30:
            return

        if not self.base_url or not self.username:
            raise ConnectionError("GoData no está configurado (falta URL o credenciales)")

        try:
            resp = requests.post(
                f"{self.base_url}/api/oauth/token",
                json={"username": self.username, "password": self.password},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            # GoData Guatemala uses {"access_token": "..."} format (OAuth2)
            # Standard GoData uses {"id": "..."} format
            self._token = data.get("access_token") or data.get("id", "")
            ttl = data.get("expires_in") or data.get("ttl", 600)
            self._token_expires = time.time() + ttl
            # Use Bearer header (works for both Guatemala and standard GoData)
            self._session.headers["Authorization"] = f"Bearer {self._token}"
            logger.info("GoData: token obtenido (TTL=%ds)", ttl)
        except requests.ConnectionError:
            raise ConnectionError(f"No se puede conectar a GoData en {self.base_url}")
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                raise PermissionError("Credenciales GoData inválidas")
            raise RuntimeError(f"Error autenticación GoData: {e.response.status_code}")

    def _api_url(self, path: str) -> str:
        """Construye URL completa de la API."""
        return f"{self.base_url}/api{path}"

    def _outbreak_url(self, path: str) -> str:
        """Construye URL dentro del outbreak activo."""
        return f"{self.base_url}/api/outbreaks/{self.outbreak_id}{path}"

    # ─── HTTP Methods ──────────────────────────────────────

    def _request_with_retry(self, method, url, max_retries=2, **kwargs):
        """Execute request with retry for transient errors (connection/timeout)."""
        for attempt in range(max_retries + 1):
            try:
                resp = method(url, **kwargs)
                resp.raise_for_status()
                return resp
            except (requests.ConnectionError, requests.Timeout) as e:
                if attempt < max_retries:
                    wait = 2 ** attempt  # 1s, 2s
                    logger.warning(
                        "GoData request failed (attempt %d/%d), retrying in %ds: %s",
                        attempt + 1, max_retries + 1, wait, e
                    )
                    time.sleep(wait)
                else:
                    if isinstance(e, requests.Timeout):
                        raise ConnectionError(f"GoData timeout after {max_retries + 1} attempts: {e}")
                    raise ConnectionError("No se puede conectar a GoData")
            except requests.HTTPError as e:
                self._handle_http_error(e)

    def _get(self, url: str, params: dict = None) -> dict:
        self._ensure_token()
        resp = self._request_with_retry(
            self._session.get, url, params=params, timeout=self.timeout
        )
        return resp.json()

    def _post(self, url: str, json_data: dict) -> dict:
        self._ensure_token()
        resp = self._request_with_retry(
            self._session.post, url, json=json_data, timeout=self.timeout
        )
        return resp.json()

    def _put(self, url: str, json_data: dict) -> dict:
        self._ensure_token()
        resp = self._request_with_retry(
            self._session.put, url, json=json_data, timeout=self.timeout
        )
        return resp.json()

    def _handle_http_error(self, e: requests.HTTPError):
        status = e.response.status_code
        detail = ""
        try:
            detail = e.response.json().get("error", {}).get("message", e.response.text)
        except Exception:
            detail = e.response.text
        if status == 401:
            self._token = ""
            raise PermissionError("Token GoData expirado o inválido")
        raise RuntimeError(f"GoData HTTP {status}: {detail}")

    # ─── Health ────────────────────────────────────────────

    def health(self) -> Dict:
        """Verifica conectividad con GoData."""
        if not self.base_url:
            return {"status": "not_configured"}
        try:
            resp = requests.get(f"{self.base_url}/api/system-settings/version", timeout=5)
            if resp.ok:
                return {"status": "ok", "version": resp.json()}
            return {"status": "error", "code": resp.status_code}
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    def test_connection(self) -> Dict:
        """Prueba autenticación completa."""
        try:
            self._ensure_token()
            outbreaks = self._get(self._api_url("/outbreaks"), params={"limit": 1})
            return {
                "status": "ok",
                "authenticated": True,
                "outbreak_count": len(outbreaks) if isinstance(outbreaks, list) else 0,
            }
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    # ─── Outbreaks ─────────────────────────────────────────

    def get_outbreaks(self) -> List[Dict]:
        """Lista todos los outbreaks."""
        return self._get(self._api_url("/outbreaks"))

    def get_outbreak(self) -> Dict:
        """Obtiene el outbreak activo."""
        return self._get(self._api_url(f"/outbreaks/{self.outbreak_id}"))

    # ─── Cases ─────────────────────────────────────────────

    def create_case(self, case_data: Dict) -> Dict:
        """Crea un caso en el outbreak activo.

        Args:
            case_data: Payload GoData completo (ver godata_field_map.map_record_to_godata)

        Returns:
            Dict con el caso creado (incluye 'id' = GoData UUID)
        """
        if not self.production_mode:
            logger.warning("GoData: modo prueba — NO se crea caso real")
            return {
                "id": f"DRYRUN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "dry_run": True,
                "would_send": case_data,
            }
        return self._post(self._outbreak_url("/cases"), case_data)

    def update_case(self, case_id: str, updates: Dict) -> Dict:
        """Actualiza un caso existente."""
        if not self.production_mode:
            logger.warning("GoData: modo prueba — NO se actualiza caso real")
            return {"id": case_id, "dry_run": True, "would_update": updates}
        return self._put(self._outbreak_url(f"/cases/{case_id}"), updates)

    def get_case(self, case_id: str) -> Dict:
        """Obtiene un caso por ID."""
        return self._get(self._outbreak_url(f"/cases/{case_id}"))

    def get_cases(self, limit: int = 100, offset: int = 0, filters: dict = None) -> List[Dict]:
        """Lista casos del outbreak activo."""
        params = {"limit": limit, "skip": offset}
        if filters:
            import json
            params["filter"] = json.dumps({"where": filters})
        return self._get(self._outbreak_url("/cases"), params=params)

    def get_cases_count(self) -> int:
        """Cuenta total de casos."""
        resp = self._get(self._outbreak_url("/cases/count"))
        return resp.get("count", 0)

    def find_case_by_visual_id(self, visual_id: str) -> Optional[Dict]:
        """Busca caso por visualId (nuestro registro_id)."""
        import json
        params = {"filter": json.dumps({"where": {"visualId": visual_id}, "limit": 1})}
        cases = self._get(self._outbreak_url("/cases"), params=params)
        return cases[0] if cases else None

    # ─── Lab Results ───────────────────────────────────────

    def add_lab_result(self, case_id: str, lab_data: Dict) -> Dict:
        """Agrega resultado de laboratorio a un caso.

        Args:
            case_id: GoData case UUID
            lab_data: {sampleType, dateSampleTaken, testType, testedFor, result, dateOfResult, ...}
        """
        if not self.production_mode:
            logger.warning("GoData: modo prueba — NO se agrega lab result real")
            return {"id": f"DRYRUN-LAB-{datetime.now().strftime('%H%M%S')}", "dry_run": True}
        return self._post(self._outbreak_url(f"/cases/{case_id}/lab-results"), lab_data)

    def get_lab_results(self, case_id: str) -> List[Dict]:
        """Obtiene resultados de laboratorio de un caso."""
        return self._get(self._outbreak_url(f"/cases/{case_id}/lab-results"))

    # ─── Contacts ──────────────────────────────────────────

    def create_contact(self, contact_data: Dict) -> Dict:
        """Crea un contacto."""
        if not self.production_mode:
            return {"id": f"DRYRUN-CONTACT", "dry_run": True}
        return self._post(self._outbreak_url("/contacts"), contact_data)

    # ─── Relationships ─────────────────────────────────────

    def create_relationship(self, relationship_data: Dict) -> Dict:
        """Crea relación caso-contacto."""
        if not self.production_mode:
            return {"id": f"DRYRUN-REL", "dry_run": True}
        return self._post(self._outbreak_url("/relationships"), relationship_data)

    # ─── Locations ─────────────────────────────────────────

    def get_locations(self, parent_id: str = None) -> List[Dict]:
        """Lista ubicaciones (jerarquía geográfica)."""
        params = {}
        if parent_id:
            import json
            params["filter"] = json.dumps({"where": {"parentLocationId": parent_id}})
        return self._get(self._api_url("/locations"), params=params)

    # ─── Reference Data ────────────────────────────────────

    def get_reference_data(self, category: str = None) -> List[Dict]:
        """Obtiene datos de referencia (códigos, opciones)."""
        params = {}
        if category:
            import json
            params["filter"] = json.dumps({"where": {"categoryId": category}})
        return self._get(self._api_url("/reference-data"), params=params)
