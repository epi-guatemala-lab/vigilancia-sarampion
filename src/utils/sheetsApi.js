/**
 * Funciones para enviar datos al backend.
 * Soporta: FastAPI (recomendado), Google Apps Script, Google Sheets API
 */
import { sheetsConfig } from '../config/googleSheets.js'

/**
 * Error que representa validación de negocio (no red). No se debe reintentar.
 */
export class ValidationError extends Error {
  constructor(status, detail) {
    super(detail)
    this.name = 'ValidationError'
    this.status = status
    this.detail = detail
    this.isValidation = true
  }
}

/**
 * Envía datos al backend FastAPI (Opción A - recomendada)
 */
async function sendViaApi(data) {
  const url = `${sheetsConfig.api.baseUrl}/api/registro`

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    const detail = err.detail || `Error ${response.status}`
    // 429 (rate limit) NO es validación: es transitorio → reintentar
    if (response.status === 429) {
      throw new Error(detail)
    }
    // 4xx restantes = error de validación/negocio → no reintentar
    if (response.status >= 400 && response.status < 500) {
      throw new ValidationError(response.status, detail)
    }
    throw new Error(detail)
  }

  return await response.json()
}

/**
 * Envía datos usando Google Apps Script como proxy (Opción B)
 */
async function sendViaAppsScript(data) {
  const url = sheetsConfig.script.url
  if (!url) throw new Error('URL de Apps Script no configurada')

  await fetch(url, {
    method: 'POST',
    mode: 'no-cors',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

  return { success: true }
}

/**
 * Envía datos usando Google Sheets API v4 (Opción C)
 */
async function sendViaSheetsApi(data) {
  const { spreadsheetId, apiKey, sheetName } = sheetsConfig.sheets
  if (!spreadsheetId || !apiKey) throw new Error('Config Sheets API incompleta')

  const values = [Object.values(data)]
  const range = `${sheetName}!A1`
  const url = `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}/values/${range}:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS&key=${apiKey}`

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ values }),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.error?.message || `Error ${response.status}`)
  }

  return await response.json()
}

/**
 * Envía datos con reintentos automáticos
 */
export async function submitToSheets(data) {
  const { method, retryAttempts, retryDelay } = sheetsConfig
  let lastError = null

  for (let attempt = 1; attempt <= retryAttempts; attempt++) {
    try {
      switch (method) {
        case 'api':
          return await sendViaApi(data)
        case 'script':
          return await sendViaAppsScript(data)
        case 'sheets':
          return await sendViaSheetsApi(data)
        default:
          return await sendViaApi(data)
      }
    } catch (error) {
      lastError = error
      // Validación de negocio (409 duplicado, 400 inválido, etc.) — no reintentar
      if (error && error.isValidation) {
        throw error
      }
      if (attempt < retryAttempts) {
        await new Promise(r => setTimeout(r, retryDelay * attempt))
      }
    }
  }

  throw lastError
}

/**
 * Modo offline: guardar envíos pendientes en localStorage
 */
export function savePendingSubmission(data) {
  const pending = getPendingSubmissions()
  pending.push({ data, timestamp: new Date().toISOString(), id: data.registro_id })
  localStorage.setItem('sarampion_pending', JSON.stringify(pending))
}

export function getPendingSubmissions() {
  try {
    return JSON.parse(localStorage.getItem('sarampion_pending') || '[]')
  } catch {
    return []
  }
}

export function removePendingSubmission(id) {
  const pending = getPendingSubmissions().filter(p => p.id !== id)
  localStorage.setItem('sarampion_pending', JSON.stringify(pending))
}

// Mutex: evita que dos llamadas concurrentes (setInterval + evento online +
// focus) dupliquen POSTs del mismo item antes de que el primero lo borre.
let _retryInFlight = null

export async function retryPendingSubmissions() {
  if (_retryInFlight) return _retryInFlight
  _retryInFlight = (async () => {
    try {
      const pending = getPendingSubmissions()
      for (let i = 0; i < pending.length; i++) {
        const item = pending[i]
        try {
          // Espaciado mínimo entre items para no saturar el backend con
          // ráfagas (200ms). El backend ya no tiene rate limit por IP.
          if (i > 0) {
            await new Promise(r => setTimeout(r, 200))
          }
          await submitToSheets(item.data)
          removePendingSubmission(item.id)
        } catch {
          // Falla → se queda en cola, el siguiente tick lo reintenta
        }
      }
    } finally {
      _retryInFlight = null
    }
  })()
  return _retryInFlight
}
