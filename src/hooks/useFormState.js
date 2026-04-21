import { useState, useCallback, useEffect } from 'react'
import { getEpiWeek } from '../utils/formatters.js'

const STORAGE_KEY = 'sarampion_form_data'
const SUBMITTED_KEY = 'sarampion_submitted_records'

/**
 * Devuelve la fecha de hoy en zona horaria America/Guatemala (UTC-6 sin DST),
 * en formato YYYY-MM-DD listo para inputs type=date.
 */
function hoyGuatemala() {
  try {
    const parts = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'America/Guatemala',
      year: 'numeric', month: '2-digit', day: '2-digit',
    }).format(new Date())
    return parts // en-CA ya devuelve YYYY-MM-DD
  } catch {
    const d = new Date()
    const yyyy = d.getFullYear()
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const dd = String(d.getDate()).padStart(2, '0')
    return `${yyyy}-${mm}-${dd}`
  }
}

/**
 * Defaults iniciales del formulario. Incluye la fecha de notificación de hoy
 * (zona Guatemala) y la semana epidemiológica correspondiente — ambas deben
 * inyectarse JUNTAS porque semana_epidemiologica es required pero readOnly:
 * sin el pre-cálculo, el formulario bloquea el avance en page 1.
 */
function buildInitialDefaults() {
  const fecha = hoyGuatemala()
  const semana = getEpiWeek(fecha)
  return {
    fecha_notificacion: fecha,
    semana_epidemiologica: semana ? String(semana) : '',
  }
}

/**
 * Hook para manejar el estado global del formulario
 * con persistencia en localStorage
 */
export function useFormState(initialData = {}) {
  const [formData, setFormData] = useState(() => {
    const defaults = { ...buildInitialDefaults(), ...initialData }
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (!saved) return defaults
      const parsed = JSON.parse(saved)
      // Si el objeto guardado está vacío o tiene datos de un envío reciente
      // (afiliación que ya se marcó como submitted), empezar limpio
      if (!parsed || Object.keys(parsed).length === 0) return defaults
      // Verificar si estos datos ya fueron enviados (safety net)
      const submitted = JSON.parse(localStorage.getItem(SUBMITTED_KEY) || '[]')
      const afil = parsed.afiliacion
      const fecha = parsed.fecha_notificacion
      if (afil && fecha) {
        const key = `${afil}_${fecha}`
        const wasSubmitted = submitted.some(r => r.key === key && Date.now() - r.timestamp < 86400000)
        if (wasSubmitted) {
          localStorage.removeItem(STORAGE_KEY)
          return defaults
        }
      }
      // Si el parsed no tiene fecha_notificacion, inyectar hoy
      if (!parsed.fecha_notificacion) parsed.fecha_notificacion = hoyGuatemala()
      // Safety net: si falta la semana epi pero sí hay fecha, calcularla.
      // Cubre sesiones previas anteriores al fix (localStorage con fecha pero
      // sin semana, o copia-pega desde otra sesión).
      if (parsed.fecha_notificacion && !parsed.semana_epidemiologica) {
        const w = getEpiWeek(parsed.fecha_notificacion)
        if (w) parsed.semana_epidemiologica = String(w)
      }
      return { ...defaults, ...parsed }
    } catch {
      return defaults
    }
  })

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(formData))
    } catch {
      // localStorage lleno o no disponible
    }
  }, [formData])

  const updateField = useCallback((fieldId, value) => {
    setFormData(prev => ({
      ...prev,
      [fieldId]: value,
    }))
  }, [])

  const updateMultipleFields = useCallback((updates) => {
    setFormData(prev => ({
      ...prev,
      ...updates,
    }))
  }, [])

  const resetForm = useCallback(() => {
    setFormData({ fecha_notificacion: hoyGuatemala() })
    localStorage.removeItem(STORAGE_KEY)
  }, [])

  /**
   * Verifica si un registro con la misma afiliación + fecha de notificación
   * ya fue enviado recientemente (últimas 24 horas).
   * Esto permite re-enviar para un mismo paciente en otra fecha.
   */
  const isDuplicate = useCallback((afiliacion, fechaNotificacion) => {
    try {
      const records = JSON.parse(localStorage.getItem(SUBMITTED_KEY) || '[]')
      const key = `${afiliacion}_${fechaNotificacion}`
      // Limpiar registros mayores a 24 horas
      const recent = records.filter(r => Date.now() - r.timestamp < 86400000)
      localStorage.setItem(SUBMITTED_KEY, JSON.stringify(recent))
      return recent.some(r => r.key === key)
    } catch {
      return false
    }
  }, [])

  const markAsSubmitted = useCallback((afiliacion, fechaNotificacion) => {
    try {
      const records = JSON.parse(localStorage.getItem(SUBMITTED_KEY) || '[]')
      const key = `${afiliacion}_${fechaNotificacion}`
      records.push({ key, timestamp: Date.now() })
      localStorage.setItem(SUBMITTED_KEY, JSON.stringify(records))
    } catch {
      // ignore
    }
  }, [])

  const clearSubmitted = useCallback(() => {
    // No limpiar submitted records al crear nuevo formulario
    // solo limpiar los datos del formulario actual
  }, [])

  return {
    formData,
    updateField,
    updateMultipleFields,
    resetForm,
    isDuplicate,
    markAsSubmitted,
    clearSubmitted,
  }
}
