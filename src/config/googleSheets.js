/**
 * Configuración de envío de datos.
 * Soporta tres métodos:
 *   - "api": Backend FastAPI propio (recomendado)
 *   - "script": Google Apps Script como proxy
 *   - "sheets": Google Sheets API v4 directa
 */

export const sheetsConfig = {
  // Método: "api" | "script" | "sheets"
  method: import.meta.env.VITE_SHEETS_METHOD || 'api',

  // Backend FastAPI (Opción A - recomendada)
  api: {
    baseUrl: import.meta.env.VITE_API_URL || 'https://igss.mediclic.org/sarampion',
  },

  // Google Apps Script (Opción B)
  script: {
    url: import.meta.env.VITE_APPS_SCRIPT_URL || '',
  },

  // Google Sheets API (Opción C)
  sheets: {
    spreadsheetId: import.meta.env.VITE_GOOGLE_SHEETS_ID || '',
    apiKey: import.meta.env.VITE_GOOGLE_API_KEY || '',
    sheetName: 'SOSPECHOSOS',
  },

  retryAttempts: 3,
  retryDelay: 2000,
}
