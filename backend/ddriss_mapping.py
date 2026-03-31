"""
Mapping de municipios a DDRISS (Dirección Departamental de Redes Integradas de Servicios de Salud).
Usado para reportes y generación de fichas por área DDRISS.

Guatemala, Petén y Quiché están subdivididos en múltiples DDRISS.
El resto de departamentos tienen un DDRISS 1:1.
"""

import unicodedata

# ──────────────────────────────────────────────────────────
# Guatemala: 4 sub-DDRISS
# ──────────────────────────────────────────────────────────
GUATEMALA_DDRISS = {
    # GUATEMALA SUR
    'SAN MIGUEL PETAPA': 'GUATEMALA SUR',
    'AMATITLAN': 'GUATEMALA SUR',
    'VILLA NUEVA': 'GUATEMALA SUR',
    'VILLA CANALES': 'GUATEMALA SUR',
    # GUATEMALA NOR ORIENTE
    'CHINAUTLA': 'GUATEMALA NOR ORIENTE',
    'FRAIJANES': 'GUATEMALA NOR ORIENTE',
    'PALENCIA': 'GUATEMALA NOR ORIENTE',
    'SAN JOSE DEL GOLFO': 'GUATEMALA NOR ORIENTE',
    'SAN JOSE PINULA': 'GUATEMALA NOR ORIENTE',
    'SANTA CATARINA PINULA': 'GUATEMALA NOR ORIENTE',
    'SAN PEDRO AYAMPUC': 'GUATEMALA NOR ORIENTE',
    # GUATEMALA NOR OCCIDENTE
    'MIXCO': 'GUATEMALA NOR OCCIDENTE',
    'SAN PEDRO SACATEPEQUEZ': 'GUATEMALA NOR OCCIDENTE',
    'SAN JUAN SACATEPEQUEZ': 'GUATEMALA NOR OCCIDENTE',
    'SAN RAYMUNDO': 'GUATEMALA NOR OCCIDENTE',
    'CHUARRANCHO': 'GUATEMALA NOR OCCIDENTE',
}

# ──────────────────────────────────────────────────────────
# Petén: 3 sub-DDRISS
# ──────────────────────────────────────────────────────────
PETEN_NORTE_MUNIS = {
    'FLORES', 'SAN BENITO', 'SAN ANDRES', 'SAN JOSE',
    'MELCHOR DE MENCOS', 'SAN FRANCISCO', 'SANTA ANA',
}
PETEN_SUR_OCC_MUNIS = {
    'SAYAXCHE', 'LA LIBERTAD', 'LAS CRUCES', 'SAN LUIS',
    'EL NARANJO', 'NUEVA ESPERANZA',
}
PETEN_SUR_ORI_MUNIS = {
    'DOLORES', 'POPTUN', 'EL CHAL', 'SANTA ELENA',
}

# ──────────────────────────────────────────────────────────
# Quiché: 3 sub-DDRISS
# ──────────────────────────────────────────────────────────
IXCAN_MUNIS = {'IXCAN', 'PLAYA GRANDE'}
IXIL_MUNIS = {'NEBAJ', 'SANTA MARIA NEBAJ', 'CHAJUL', 'SAN JUAN COTZAL', 'COTZAL'}

# ──────────────────────────────────────────────────────────
# Departamento directo → DDRISS (sin tildes, uppercase)
# ──────────────────────────────────────────────────────────
DEPTO_DIRECT = {
    'SOLOLA': 'SOLOLA',
    'TOTONICAPAN': 'TOTONICAPAN',
    'CHIMALTENANGO': 'CHIMALTENANGO',
    'SACATEPEQUEZ': 'SACATEPEQUEZ',
    'JALAPA': 'JALAPA',
    'QUETZALTENANGO': 'QUETZALTENANGO',
    'ESCUINTLA': 'ESCUINTLA',
    'HUEHUETENANGO': 'HUEHUETENANGO',
    'IZABAL': 'IZABAL',
    'CHIQUIMULA': 'CHIQUIMULA',
    'SANTA ROSA': 'SANTA ROSA',
    'RETALHULEU': 'RETALHULEU',
    'SUCHITEPEQUEZ': 'SUCHITEPEQUEZ',
    'EL PROGRESO': 'EL PROGRESO',
    'ZACAPA': 'ZACAPA',
    'BAJA VERAPAZ': 'BAJA VERAPAZ',
    'SAN MARCOS': 'SAN MARCOS',
    'ALTA VERAPAZ': 'ALTA VERAPAZ',
    'JUTIAPA': 'JUTIAPA',
}

# ──────────────────────────────────────────────────────────
# Lista completa de DDRISS (para dropdown/filtro)
# ──────────────────────────────────────────────────────────
DDRISS_LIST = sorted([
    'GUATEMALA CENTRAL',
    'GUATEMALA SUR',
    'GUATEMALA NOR ORIENTE',
    'GUATEMALA NOR OCCIDENTE',
    'SOLOLA',
    'TOTONICAPAN',
    'CHIMALTENANGO',
    'SACATEPEQUEZ',
    'JALAPA',
    'QUICHE',
    'IXCAN',
    'IXIL',
    'QUETZALTENANGO',
    'ESCUINTLA',
    'SIN ASIGNAR',
    'HUEHUETENANGO',
    'IZABAL',
    'CHIQUIMULA',
    'SANTA ROSA',
    'RETALHULEU',
    'SUCHITEPEQUEZ',
    'EL PROGRESO',
    'ZACAPA',
    'BAJA VERAPAZ',
    'SAN MARCOS',
    'PETEN NORTE',
    'PETEN SUR ORIENTAL',
    'PETEN SUR OCCIDENTAL',
    'ALTA VERAPAZ',
    'JUTIAPA',
])


def _parse_date_to_iso(date_str: str) -> str:
    """Parse a date string in DD/MM/YYYY or YYYY-MM-DD format to ISO YYYY-MM-DD.

    Returns empty string if parsing fails.
    """
    if not date_str:
        return ""
    date_str = date_str.strip()[:10]
    # Already ISO?
    if len(date_str) == 10 and date_str[4] == '-':
        return date_str
    # DD/MM/YYYY
    parts = date_str.split('/')
    if len(parts) == 3:
        dd, mm, yyyy = parts
        if len(yyyy) == 4:
            return f"{yyyy}-{mm.zfill(2)}-{dd.zfill(2)}"
        elif len(yyyy) == 3:
            # Handle typos like "226" -> "2026"
            return f"2{yyyy}-{mm.zfill(2)}-{dd.zfill(2)}"
    return ""


def _strip_accents(s: str) -> str:
    """Remove diacritics/accents for robust matching."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )


def get_ddriss(departamento: str, municipio: str = '') -> str:
    """Resolve DDRISS from departamento + municipio.

    Args:
        departamento: Department name (may contain accents).
        municipio: Municipality name (may contain accents).

    Returns:
        DDRISS name (uppercase, without accents).
    """
    depto = _strip_accents((departamento or '').upper().strip())
    muni = _strip_accents((municipio or '').upper().strip())

    # Empty department → SIN ASIGNAR
    if not depto:
        return 'SIN ASIGNAR'

    # Guatemala subdivisions
    if depto == 'GUATEMALA':
        return GUATEMALA_DDRISS.get(muni, 'GUATEMALA CENTRAL')

    # Petén subdivisions
    if depto in ('PETEN', 'EL PETEN'):
        if muni in PETEN_NORTE_MUNIS:
            return 'PETEN NORTE'
        if muni in PETEN_SUR_OCC_MUNIS:
            return 'PETEN SUR OCCIDENTAL'
        if muni in PETEN_SUR_ORI_MUNIS:
            return 'PETEN SUR ORIENTAL'
        return 'PETEN NORTE'  # default for unknown Petén municipalities

    # Quiché subdivisions
    if depto in ('QUICHE', 'EL QUICHE'):
        if muni in IXCAN_MUNIS:
            return 'IXCAN'
        if muni in IXIL_MUNIS:
            return 'IXIL'
        return 'QUICHE'

    # Direct department mapping
    return DEPTO_DIRECT.get(depto, depto)
