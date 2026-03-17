/**
 * Formateadores de datos antes de envío a Google Sheets
 */
import { v4 as uuidv4 } from 'uuid'

/**
 * Genera un ID corto único
 */
export function generateShortId() {
  return uuidv4().split('-')[0].toUpperCase()
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
  prepared.registro_id = generateShortId()
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
