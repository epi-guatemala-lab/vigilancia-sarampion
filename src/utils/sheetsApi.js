/**
 * Funciones para enviar datos a Google Sheets
 * Soporta Google Sheets API v4 y Google Apps Script como proxy
 */
import { sheetsConfig } from '../config/googleSheets.js'

/**
 * Envía datos usando Google Apps Script como proxy (Opción B - recomendada)
 */
async function sendViaAppsScript(data) {
  const url = sheetsConfig.script.url

  if (!url) {
    throw new Error('URL de Apps Script no configurada. Configure VITE_APPS_SCRIPT_URL en .env')
  }

  const response = await fetch(url, {
    method: 'POST',
    mode: 'no-cors',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  // Con mode: 'no-cors' no podemos leer la respuesta, pero el envío se realizó
  // Apps Script responderá 200 si todo está bien
  return { success: true, message: 'Datos enviados correctamente' }
}

/**
 * Envía datos usando Google Sheets API v4 directa (Opción A)
 * Requiere Service Account con acceso al Sheet
 */
async function sendViaSheetsApi(data) {
  const { spreadsheetId, apiKey, sheetName } = sheetsConfig.api

  if (!spreadsheetId || !apiKey) {
    throw new Error('Configuración de Google Sheets API incompleta. Verifique VITE_GOOGLE_SHEETS_ID y VITE_GOOGLE_API_KEY.')
  }

  const values = [Object.values(data)]
  const range = `${sheetName}!A1`

  const url = `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}/values/${range}:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS&key=${apiKey}`

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ values }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.error?.message || `Error ${response.status} al enviar datos`)
  }

  return await response.json()
}

/**
 * Envía datos al Google Sheet con reintentos
 */
export async function submitToSheets(data) {
  const { method, retryAttempts, retryDelay } = sheetsConfig
  let lastError = null

  for (let attempt = 1; attempt <= retryAttempts; attempt++) {
    try {
      if (method === 'api') {
        return await sendViaSheetsApi(data)
      } else {
        return await sendViaAppsScript(data)
      }
    } catch (error) {
      lastError = error
      console.warn(`Intento ${attempt} fallido:`, error.message)

      if (attempt < retryAttempts) {
        await new Promise(resolve => setTimeout(resolve, retryDelay * attempt))
      }
    }
  }

  throw lastError
}

/**
 * Guarda datos pendientes en localStorage para modo offline
 */
export function savePendingSubmission(data) {
  const pending = getPendingSubmissions()
  pending.push({
    data,
    timestamp: new Date().toISOString(),
    id: data.registro_id,
  })
  localStorage.setItem('sarampion_pending', JSON.stringify(pending))
}

/**
 * Obtiene envíos pendientes
 */
export function getPendingSubmissions() {
  try {
    return JSON.parse(localStorage.getItem('sarampion_pending') || '[]')
  } catch {
    return []
  }
}

/**
 * Elimina un envío pendiente
 */
export function removePendingSubmission(id) {
  const pending = getPendingSubmissions().filter(p => p.id !== id)
  localStorage.setItem('sarampion_pending', JSON.stringify(pending))
}

/**
 * Intenta reenviar todos los envíos pendientes
 */
export async function retryPendingSubmissions() {
  const pending = getPendingSubmissions()
  const results = []

  for (const item of pending) {
    try {
      await submitToSheets(item.data)
      removePendingSubmission(item.id)
      results.push({ id: item.id, success: true })
    } catch (error) {
      results.push({ id: item.id, success: false, error: error.message })
    }
  }

  return results
}
