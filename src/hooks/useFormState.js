import { useState, useCallback, useEffect } from 'react'

const STORAGE_KEY = 'sarampion_form_data'
const SUBMITTED_KEY = 'sarampion_submitted'

/**
 * Hook para manejar el estado global del formulario
 * con persistencia en localStorage
 */
export function useFormState(initialData = {}) {
  // Cargar datos guardados de localStorage
  const [formData, setFormData] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      return saved ? { ...initialData, ...JSON.parse(saved) } : initialData
    } catch {
      return initialData
    }
  })

  // Guardar en localStorage cuando cambien los datos
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
    setFormData({})
    localStorage.removeItem(STORAGE_KEY)
  }, [])

  const hasBeenSubmitted = useCallback(() => {
    try {
      const submitted = localStorage.getItem(SUBMITTED_KEY)
      if (!submitted) return false
      // El flag expira después de 1 hora
      const { timestamp } = JSON.parse(submitted)
      return Date.now() - timestamp < 3600000
    } catch {
      return false
    }
  }, [])

  const markAsSubmitted = useCallback(() => {
    localStorage.setItem(SUBMITTED_KEY, JSON.stringify({
      timestamp: Date.now(),
    }))
  }, [])

  const clearSubmitted = useCallback(() => {
    localStorage.removeItem(SUBMITTED_KEY)
  }, [])

  return {
    formData,
    updateField,
    updateMultipleFields,
    resetForm,
    hasBeenSubmitted,
    markAsSubmitted,
    clearSubmitted,
  }
}
