import { useState, useCallback, useEffect, useRef } from 'react'
import { submitToSheets, savePendingSubmission, retryPendingSubmissions, getPendingSubmissions } from '../utils/sheetsApi.js'
import { prepareSubmissionData } from '../utils/formatters.js'
import { formFields } from '../config/formSchema.js'

/**
 * Hook para enviar datos al backend
 * con manejo de errores, reintentos y modo offline
 */
export function useGoogleSheets() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState(null)
  const [submitSuccess, setSubmitSuccess] = useState(false)
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const lastRegistroId = useRef(null)

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      retryPendingSubmissions()
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
    lastRegistroId.current = null

    // Preparar datos UNA sola vez (genera el registro_id)
    const prepared = prepareSubmissionData(formData, formFields)
    lastRegistroId.current = prepared.registro_id

    try {
      if (!isOnline) {
        savePendingSubmission(prepared)
        setSubmitSuccess(true)
        return { success: true, registro_id: prepared.registro_id, offline: true }
      }

      const result = await submitToSheets(prepared)
      setSubmitSuccess(true)
      // Usar el registro_id del server si viene, si no el local
      const finalId = result?.registro_id || prepared.registro_id
      lastRegistroId.current = finalId
      return { success: true, registro_id: finalId }

    } catch (error) {
      console.error('Error al enviar:', error)

      // Si falla el envío online, guardar como pendiente
      savePendingSubmission(prepared)
      setSubmitSuccess(true)
      return { success: true, registro_id: prepared.registro_id, offline: true }

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
    lastRegistroId,
  }
}
