/**
 * Funciones para enviar datos al backend.
 * Soporta: FastAPI (recomendado), Google Apps Script, Google Sheets API
 */
import { sheetsConfig } from '../config/googleSheets.js'

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
    throw new Error(err.detail || `Error ${response.status}`)
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

export async function retryPendingSubmissions() {
  const pending = getPendingSubmissions()
  for (let i = 0; i < pending.length; i++) {
    const item = pending[i]
    try {
      // Exponential backoff between retries: 2s, 4s, 8s... (avoids rate limit)
      if (i > 0) {
        const delay = Math.min(2000 * Math.pow(2, i - 1), 30000)
        await new Promise(r => setTimeout(r, delay))
      }
      await submitToSheets(item.data)
      removePendingSubmission(item.id)
    } catch {
      // Se reintentará después
    }
  }
}
