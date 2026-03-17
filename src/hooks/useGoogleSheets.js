import { useState, useCallback, useEffect } from 'react'
import { submitToSheets, savePendingSubmission, retryPendingSubmissions, getPendingSubmissions } from '../utils/sheetsApi.js'
import { prepareSubmissionData } from '../utils/formatters.js'
import { formFields } from '../config/formSchema.js'

/**
 * Hook para enviar datos a Google Sheets
 * con manejo de errores, reintentos y modo offline
 */
export function useGoogleSheets() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState(null)
  const [submitSuccess, setSubmitSuccess] = useState(false)
  const [isOnline, setIsOnline] = useState(navigator.onLine)

  // Escuchar cambios de conectividad
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      // Reenviar pendientes cuando vuelva la conexión
      retryPendingSubmissions().then(results => {
        const failed = results.filter(r => !r.success)
        if (failed.length > 0) {
          console.warn('Algunos envíos pendientes fallaron:', failed)
        }
      })
    }

    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  const submit = useCallback(async (formData) => {
    setIsSubmitting(true)
    setSubmitError(null)
    setSubmitSuccess(false)

    // Rate limiting: máximo 1 envío por minuto
    const lastSubmit = localStorage.getItem('sarampion_last_submit')
    if (lastSubmit) {
      const elapsed = Date.now() - parseInt(lastSubmit)
      if (elapsed < 60000) {
        setSubmitError('Debe esperar al menos 1 minuto entre envíos')
        setIsSubmitting(false)
        return false
      }
    }

    try {
      const prepared = prepareSubmissionData(formData, formFields)

      if (!isOnline) {
        // Guardar para envío posterior
        savePendingSubmission(prepared)
        setSubmitSuccess(true)
        setIsSubmitting(false)
        localStorage.setItem('sarampion_last_submit', String(Date.now()))
        return true
      }

      await submitToSheets(prepared)
      setSubmitSuccess(true)
      localStorage.setItem('sarampion_last_submit', String(Date.now()))
      return true
    } catch (error) {
      console.error('Error al enviar:', error)

      // Si falla, guardar como pendiente
      try {
        const prepared = prepareSubmissionData(formData, formFields)
        savePendingSubmission(prepared)
        setSubmitSuccess(true)
        localStorage.setItem('sarampion_last_submit', String(Date.now()))
        return true
      } catch {
        setSubmitError('Error al enviar los datos. Por favor intente de nuevo.')
        return false
      }
    } finally {
      setIsSubmitting(false)
    }
  }, [isOnline])

  const pendingCount = getPendingSubmissions().length

  return {
    submit,
    isSubmitting,
    submitError,
    submitSuccess,
    isOnline,
    pendingCount,
    setSubmitError,
    setSubmitSuccess,
  }
}
