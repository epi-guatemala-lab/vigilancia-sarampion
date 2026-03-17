/**
 * Configuración de Google Sheets API
 * Soporta dos métodos de envío:
 *   - "api": Google Sheets API v4 directa con Service Account
 *   - "script": Google Apps Script como proxy (recomendado para simpleza)
 */

export const sheetsConfig = {
  // Método de envío: "api" o "script"
  method: import.meta.env.VITE_SHEETS_METHOD || 'script',

  // Configuración para Google Sheets API (Opción A)
  api: {
    spreadsheetId: import.meta.env.VITE_GOOGLE_SHEETS_ID || '',
    apiKey: import.meta.env.VITE_GOOGLE_API_KEY || '',
    serviceAccountEmail: import.meta.env.VITE_GOOGLE_SERVICE_ACCOUNT_EMAIL || '',
    privateKey: import.meta.env.VITE_GOOGLE_PRIVATE_KEY || '',
    sheetName: 'SOSPECHOSOS',
  },

  // Configuración para Apps Script (Opción B)
  script: {
    url: import.meta.env.VITE_APPS_SCRIPT_URL || '',
  },

  // Configuración general
  retryAttempts: 3,
  retryDelay: 2000, // ms
}
