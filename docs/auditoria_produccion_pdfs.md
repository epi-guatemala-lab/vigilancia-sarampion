# Auditoria de Produccion — PDFs y Excel Export

**Fecha:** 2026-03-27
**Auditor:** Claude Code (automated)
**Ambiente:** Servidor produccion 100.114.83.69

---

## Resumen Ejecutivo

| Componente | Estado | Hallazgos |
|---|---|---|
| PDF v1 (EPIWEB) | FUNCIONAL | Sin errores. 2 paginas, datos correctos. |
| PDF v2 (GoData) | FUNCIONAL con observaciones | 1 pagina. Datos escritos correctamente. Render de fechas clinicas puede verse comprimido por fitToPage. |
| Excel Export | FUNCIONAL con 7 columnas omitidas | 196 columnas exportadas de 203 en BD. Omisiones intencionales. |

---

## 1. PDF v1 (EPIWEB) — pdf_ficha.py

### Tests ejecutados

| Test | Resultado | Tamano |
|---|---|---|
| Datos largos (nombres >40 chars, direccion >80 chars, observaciones >200 chars) | OK | 45,478 bytes |
| Caracteres especiales (acentos, apostrofes, umlauts, comillas, <>, &) | OK | 44,792 bytes |
| Datos vacios (dict vacio) | OK | 44,454 bytes |

### Paginas
- Todas las pruebas: **2 paginas** (por diseno — pagina 1: datos generales/clinicos, pagina 2: laboratorio/clasificacion/contactos)

### Observaciones
- Texto largo en campo "Responsable" se trunca con elipsis (...) — comportamiento esperado para layout fijo con reportlab.
- Observaciones largas se truncan — esperado por espacio limitado en la ficha.
- Caracteres especiales (acentos, apostrofes, umlauts, comillas, angulares, ampersand) renderizan correctamente.
- Fechas en formato MSPAS (digitos individuales en casillas) funcionan correctamente.
- Logo MSPAS visible en esquina superior izquierda.

### Veredicto: APTO PARA PRODUCCION

---

## 2. PDF v2 (GoData) — pdf_ficha_v2.py

### Tests ejecutados

| Test | Resultado | Tamano | Paginas |
|---|---|---|---|
| Datos largos completos | OK | 58,117 bytes | 1 |
| Caracteres especiales | OK | 56,418 bytes | 1 |
| Datos minimos (solo nombres + sexo) | OK | 54,288 bytes | 1 |
| Dict vacio | OK | 54,166 bytes | 1 |

### Verificacion de celdas (post _fill_template)

Todas las celdas se escriben correctamente al Excel intermedio:

| Campo | Celda(s) | Valor verificado |
|---|---|---|
| Fecha Notificacion | R9:C5,C7,C9 | 25, 03, 2026 |
| Fecha Inicio Sintomas | R31:C6,C8,C10 | 10, 03, 2026 |
| Fecha Inicio Fiebre | R31:C16,C18,C20 | 10, 03, 2026 |
| Fecha Inicio Exantema | R32:C7,C9,C11 | 12, 03, 2026 |
| Nombres | R16:C3 | MARIA FERNANDA ALEJANDRA PATRICIA |
| Apellidos | R16:C11 | GONZALEZ HERNANDEZ CASTILLO DE RAMIREZ LOPEZ |
| Direccion | R22:C4 | (120+ chars, wraps correctamente) |
| Observaciones | R74:C1 | (390+ chars, wraps correctamente) |
| Checkboxes sintomas | R34-37:C5-7,C17-19 | Todos marcados segun datos |
| Clasificacion | R64:C4 | Sarampion marcado |
| Criterio confirmacion | R65:C5 | Laboratorio marcado |
| Caso analizado por | R69:C5 | CONAPI marcado |
| Condicion final | R71:C4 | Recuperado marcado |

### Logo
- **1 imagen** encontrada en el template Excel
- Visible en la esquina superior izquierda del PDF generado

### Caracteres especiales
- Acentos (Jose, Maria, Lopez): OK
- Apostrofes (D'Avila, O'Brien, K'iche'): OK
- Umlauts (Muller): OK
- Comillas dobles ("Las Torres"): OK
- Simbolos HTML (<penicilina>, &): OK
- Grado (40.2 grados C): OK

### Hallazgos

#### BUG MENOR: Llamada duplicada a _write_date (linea 199 y 206)
- `_write_date(ws, 9, 5, 7, 9, ...)` para fecha_notificacion se llama 2 veces
- **Impacto:** Ninguno funcional (escribe el mismo valor dos veces)
- **Accion:** Eliminar linea 199 o 206 (cosmetic cleanup)

#### OBSERVACION: Fechas clinicas pueden no ser visibles en PDF con mucho contenido
- Las celdas R31 (fecha sintomas/fiebre) y R32 (fecha exantema) se llenan correctamente en el .xlsx
- En conversiones donde el template esta muy lleno, LibreOffice `fitToPage=1` comprime el contenido
- En el test de solo fechas (sin otro contenido), las fechas se ven claramente
- En el test con datos completos, las fechas clinicas aparecen pero pueden verse extremadamente pequenas
- **Impacto:** Bajo. Los datos estan en el archivo Excel subyacente. El PDF es una representacion visual.
- **Mitigacion posible:** Ajustar `print_area` a "A1:X74" (en vez de X75) o incrementar row heights para seccion 4.

#### OBSERVACION: Fecha hospitalizacion usa formato compacto
- Codigo escribe `22/03/2026` en celda V38 en vez de usar celdas separadas Dia/Mes/Ano
- La plantilla tiene "Dia" en C21 y "Mes" en C23 pero NO celda de "Ano" en row 38
- El formato compacto es una solucion correcta dado el layout del template

#### Checkboxes de Seccion 5 (Factores de Riesgo)
- `caso_sospechoso_comunidad_3m='NO'` escribe correctamente a R43:C8
- `contacto_sospechoso_7_23='SI'` escribe correctamente a R43:C18
- Verificado que el patron `ws.cell(row, col).value = "marked"` funciona en celdas no-merged

#### Checkboxes de Seccion 6 (Acciones de Respuesta)
- BAI SI (R50:C3): Funcional
- Vacunacion bloqueo SI (R51:C7): Funcional
- Monitoreo rapido SI (R51:C14): Funcional
- Vitamina A SI (R52:C4): Funcional
- Numero casos BAI se escribe a R50:C8 (el codigo dice C8, template tiene C8:C9 como data area): Funcional

### Veredicto: APTO PARA PRODUCCION

---

## 3. Excel Export — main.py /api/export/excel

### Estructura

| Aspecto | Valor | Estado |
|---|---|---|
| Hojas | 3 (SOSPECHOSOS, CONFIRMADOS, SUSPENDIDOS) | OK |
| EXPORT_COLS | 196 columnas | OK |
| COL_HEADERS | 196 headers | MATCH con EXPORT_COLS |
| CATEGORIES | 18 grupos | Cobertura completa (196/196) |
| Filas header | 2 (categorias + nombres) | OK |
| Freeze panes | A3 (primeras 2 filas) | OK |
| Columna extra | "No. caso" (col A) | OK |

### Columnas por categoria

| Categoria | Rango | Columnas |
|---|---|---|
| DATOS GENERALES | 1-13 | 13 |
| DATOS DEL PACIENTE | 14-31 | 18 |
| EMBARAZO | 32-37 | 6 |
| INFORMACION CLINICA | 38-65 | 28 |
| HOSPITALIZACION | 66-77 | 12 |
| FACTORES DE RIESGO | 78-83 | 6 |
| LABORATORIO | 84-105 | 22 |
| CONTACTOS Y DATOS IGSS | 106-121 | 16 |
| FORMATO 2026 — ENCABEZADO | 122-123 | 2 |
| FORMATO 2026 — UNIDAD | 124-130 | 7 |
| FORMATO 2026 — PACIENTE | 131-139 | 9 |
| FORMATO 2026 — ANTECEDENTES | 140-151 | 12 |
| FORMATO 2026 — CLINICA | 152-161 | 10 |
| FORMATO 2026 — FACTORES DE RIESGO | 162-170 | 9 |
| FORMATO 2026 — ACCIONES DE RESPUESTA | 171-179 | 9 |
| FORMATO 2026 — LABORATORIO | 180-182 | 3 |
| FORMATO 2026 — CLASIFICACION | 183-192 | 10 |
| GODATA | 193-196 | 4 |

### Categorias: Sin huecos ni solapamientos
- Cada categoria empieza exactamente donde termina la anterior + 1
- Ultima categoria (GODATA) termina en col 196 = total EXPORT_COLS

### Columnas DB omitidas del export (7)

| Columna | Razon de omision |
|---|---|
| `registro_id` | ID interno generado automaticamente, no dato del usuario |
| `timestamp_envio` | Metadato de envio, no dato epidemiologico |
| `nombre_apellido` | Campo backward-compat, redundante con `nombres` + `apellidos` |
| `fecha_laboratorios` | Backward-compat, reemplazado por campos individuales |
| `tipo_muestra` | Backward-compat, reemplazado por campos booleanos individuales |
| `lab_muestras_json` | JSON interno para muestras de laboratorio (no tabular) |
| `godata_outbreak_id` | ID interno de GoData outbreak |

**Evaluacion:** Las 7 omisiones son intencionales y correctas. No se pierde informacion epidemiologica.

### No hay columnas duplicadas en EXPORT_COLS
- Verificado: 196 columnas unicas

### Formato 2026 presente
- Las 75 columnas nuevas del formato 2026 (cols 122-196) estan correctamente incluidas
- Headers en espanol con caracteres especiales correctos (tildes, signos de interrogacion)

### Clasificacion de hojas
- `CONFIRMADO` -> hoja CONFIRMADOS
- `SUSPENDIDO` -> hoja SUSPENDIDOS
- Todo lo demas -> hoja SOSPECHOSOS
- **Observacion:** Clasificaciones como "DESCARTADO", "PENDIENTE", "CONFIRMADO SARAMPION" van a SOSPECHOSOS. Podria requerir revision si se desea separar descartados.

### Veredicto: APTO PARA PRODUCCION

---

## 4. Resumen de acciones recomendadas

### Prioridad alta (ninguna)
No se encontraron bugs criticos que impidan el uso en produccion.

### Prioridad media

1. **Eliminar _write_date duplicado** en pdf_ficha_v2.py lineas 199/206 (cosmetic)
2. **Evaluar clasificacion de hojas Excel:** "CONFIRMADO SARAMPION", "DESCARTADO", etc. actualmente van a SOSPECHOSOS. Considerar agregar mas categorias al filtro de clasificacion.

### Prioridad baja

3. **Investigar compresion de fechas clinicas** en v2 con datos densos — posible ajuste de row heights o print_area.
4. **Agregar lab_muestras_json como hoja separada** en el Excel export si se necesita auditar muestras de laboratorio estructuradas.
5. **v1 trunca observaciones largas** — comportamiento esperado pero podria documentarse para usuarios.

---

## 5. Ambiente de prueba

```
Servidor: 100.114.83.69 (Tailscale)
Python: /opt/vigilancia-sarampion/venv/bin/python3 (3.12)
LibreOffice: headless mode
Template: /opt/vigilancia-sarampion/backend/assets/ficha_sarampion_template.xlsx (51,232 bytes)
Logo: /opt/vigilancia-sarampion/backend/assets/sello_mspas.png (34,163 bytes)
BD: SQLite WAL mode, 203 columnas en tabla registros
```
