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
export function generateRegistroId() {
  const now = new Date()
  const year = now.getFullYear()

  // Correlativo: segundos desde inicio del año (máx ~31M, 5 dígitos)
  const startOfYear = new Date(year, 0, 1)
  const secondsSinceYear = Math.floor((now - startOfYear) / 1000)
  const correlativo = String(secondsSinceYear).padStart(7, '0')

  // Código verificador: 4 caracteres alfanuméricos aleatorios
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789' // sin I,O,0,1 para evitar confusión
  let codigo = ''
  for (let i = 0; i < 4; i++) {
    codigo += chars.charAt(Math.floor(Math.random() * chars.length))
  }

  return `IGSS-SAR-${year}-${correlativo}-${codigo}`
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
  prepared.timestamp_envio = getTimestamp()

  // Copiar y formatear datos del formulario
  for (const field of fields) {
    const value = formData[field.id]
    if (value !== undefined && value !== null && String(value).trim() !== '') {
      if (field.type === 'date') {
        prepared[field.id] = formatDate(value)
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
