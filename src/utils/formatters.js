/**
 * Formateadores de datos antes de envío a Google Sheets
 */

/**
 * Calcula la semana epidemiológica según sistema MMWR/CDC (usado por MSPAS Guatemala y PAHO)
 * - Semana inicia en DOMINGO y termina en SÁBADO
 * - Semana 1 del año: la primera semana que contiene al menos 4 días del nuevo año
 *   (equivale a: la semana que contiene el 4 de enero)
 */
export function getEpiWeek(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr + 'T00:00:00')
  if (isNaN(date.getTime())) return ''

  const year = date.getFullYear()

  // Encontrar el inicio de la semana epi 1 del año
  // Semana 1 contiene el 4 de enero → encontrar el domingo de esa semana
  const jan4 = new Date(year, 0, 4)
  const jan4Day = jan4.getDay() // 0=domingo
  const epiWeek1Start = new Date(year, 0, 4 - jan4Day) // domingo de la semana que contiene ene 4

  // Si la fecha es anterior al inicio de semana 1, pertenece a la última semana del año anterior
  if (date < epiWeek1Start) {
    const jan4Prev = new Date(year - 1, 0, 4)
    const jan4PrevDay = jan4Prev.getDay()
    const prevWeek1Start = new Date(year - 1, 0, 4 - jan4PrevDay)
    const diffDays = Math.floor((date - prevWeek1Start) / 86400000)
    return Math.floor(diffDays / 7) + 1
  }

  const diffDays = Math.floor((date - epiWeek1Start) / 86400000)
  const weekNo = Math.floor(diffDays / 7) + 1

  return weekNo
}

/**
 * Genera un número de registro correlativo con código
 * Formato: IGSS-SAR-2026-XXXXX-ABCD
 *   IGSS: Institución
 *   SAR: Sarampión
 *   2026: Año
 *   XXXXX: Correlativo basado en timestamp
 *   ABCD: Código verificador de 4 caracteres
 */
function _uuid() {
  // crypto.randomUUID en navegadores modernos (contexto seguro). Fallback con
  // getRandomValues por si el navegador no lo expone.
  try {
    if (globalThis.crypto && typeof globalThis.crypto.randomUUID === 'function') {
      return globalThis.crypto.randomUUID()
    }
    const b = new Uint8Array(16)
    globalThis.crypto.getRandomValues(b)
    b[6] = (b[6] & 0x0f) | 0x40
    b[8] = (b[8] & 0x3f) | 0x80
    const h = [...b].map((x) => x.toString(16).padStart(2, '0')).join('')
    return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`
  } catch {
    // Último recurso (no criptográfico) — solo si todo lo anterior falla.
    return `${Date.now().toString(16)}-${Math.floor(Math.random() * 1e16).toString(16)}`
  }
}

/**
 * Clave de idempotencia ESTABLE por envío. Se genera una vez al preparar el
 * envío y se conserva entre reintentos de la cola offline para que el backend
 * deduplique sin crear duplicados. NO se reusa entre pacientes distintos.
 */
export function generateClientSubmissionUuid() {
  return _uuid()
}

/**
 * registro_id provisional del cliente (alta entropía). Solo se usa para mostrar
 * la constancia si no hay respuesta del servidor; el id DEFINITIVO lo asigna el
 * backend (server-authoritative). El esquema viejo (segundos + 4 chars con
 * Math.random + reuso de drafts en localStorage) causaba colisiones que
 * descartaban pacientes en silencio (incidente jun 2026) — por eso ahora va UUID.
 */
export function generateRegistroId() {
  const year = new Date().getFullYear()
  return `IGSS-SAR-${year}-${_uuid().toUpperCase()}`
}

/**
 * Obtiene timestamp actual formateado
 */
export function getTimestamp() {
  const now = new Date()
  return now.toLocaleString('es-GT', {
    timeZone: 'America/Guatemala',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

/**
 * Formatea una fecha para envío
 */
export function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('es-GT', {
    timeZone: 'America/Guatemala',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

/**
 * Prepara los datos del formulario para envío
 * Agrega campos automáticos y formatea datos
 */
export function prepareSubmissionData(formData, fields) {
  const prepared = {}

  // Agregar campos automáticos
  prepared.registro_id = generateRegistroId()
  // Clave de idempotencia estable por envío (sobrevive a reintentos de la cola
  // offline). El backend la usa para deduplicar sin crear duplicados.
  prepared.client_submission_uuid = generateClientSubmissionUuid()
  prepared.timestamp_envio = getTimestamp()

  // Copiar y formatear datos del formulario
  // Solo incluir datos de campos que son visibles (excluir condicionales ocultos)
  for (const field of fields) {
    // Si el campo es condicional, verificar si debe estar visible
    let visible = true
    if (field.conditional) {
      const { dependsOn, showWhen } = field.conditional
      const depValue = formData[dependsOn]
      if (depValue === undefined || depValue === null || depValue === '') {
        visible = false
      } else if (Array.isArray(showWhen)) {
        visible = showWhen.includes(depValue)
      } else {
        visible = String(depValue).trim() === String(showWhen).trim()
      }
    }

    const value = visible ? formData[field.id] : undefined

    if (value !== undefined && value !== null && String(value).trim() !== '') {
      if (field.type === 'date') {
        prepared[field.id] = formatDate(value)
      } else if (Array.isArray(value)) {
        // Checkbox multi-select: join as comma-separated string
        prepared[field.id] = value.join(', ')
      } else {
        prepared[field.id] = String(value).trim()
      }
    } else {
      prepared[field.id] = ''
    }
  }

  return prepared
}

/**
 * Convierte los datos a un array ordenado de valores para Sheets API
 */
export function dataToRow(data, fields) {
  const headers = ['registro_id', 'timestamp_envio', ...fields.map(f => f.id)]
  return headers.map(h => data[h] || '')
}

/**
 * Obtiene los headers del formulario
 */
export function getHeaders(fields) {
  return ['registro_id', 'timestamp_envio', ...fields.map(f => f.label || f.id)]
}
