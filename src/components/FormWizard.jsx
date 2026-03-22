import { useState, useCallback } from 'react'
import FormPage from './FormPage.jsx'
import ProgressBar from './ui/ProgressBar.jsx'
import SuccessScreen from './ui/SuccessScreen.jsx'
import ErrorAlert from './ui/ErrorAlert.jsx'
import { useFormState } from '../hooks/useFormState.js'
import { useConditionalFields } from '../hooks/useConditionalFields.js'
import { useGoogleSheets } from '../hooks/useGoogleSheets.js'
import { validatePage } from '../utils/validation.js'
import { getEpiWeek } from '../utils/formatters.js'
import { pageLabels, formFields, diagnosticosMap, getMunicipios } from '../config/formSchema.js'

export default function FormWizard() {
  const [currentStep, setCurrentStep] = useState(1)
  const [errors, setErrors] = useState({})
  const [showSuccess, setShowSuccess] = useState(false)
  const [registroId, setRegistroId] = useState(null)

  const {
    formData,
    updateField,
    updateMultipleFields,
    resetForm,
    isDuplicate,
    markAsSubmitted,
  } = useFormState()

  const {
    visibleFieldsByPage,
    visiblePages,
    getPageLabel,
  } = useConditionalFields(formData)

  const {
    submit,
    isSubmitting,
    submitError,
    isOnline,
    pendingCount,
    setSubmitError,
  } = useGoogleSheets()

  const totalSteps = visiblePages.length
  const currentPageNum = visiblePages[currentStep - 1]
  const currentFields = visibleFieldsByPage[currentPageNum] || []
  const isLastStep = currentStep === totalSteps

  const handleFieldChange = useCallback((fieldId, value) => {
    updateField(fieldId, value)

    // Auto-map diagnóstico → código CIE-10
    if (fieldId === 'diagnostico_registrado' && diagnosticosMap[value]) {
      updateField('codigo_cie10', diagnosticosMap[value])
    }

    // Auto-compute nombre_apellido from nombres + apellidos
    if (fieldId === 'nombres' || fieldId === 'apellidos') {
      const nombres = fieldId === 'nombres' ? value : (formData.nombres || '')
      const apellidos = fieldId === 'apellidos' ? value : (formData.apellidos || '')
      const full = [nombres, apellidos].filter(Boolean).join(' ').trim()
      if (full) updateField('nombre_apellido', full)
    }

    // Auto-calculate age from fecha_nacimiento
    if (fieldId === 'fecha_nacimiento' && value) {
      const birth = new Date(value + 'T00:00:00')
      const today = new Date()
      if (!isNaN(birth.getTime())) {
        let years = today.getFullYear() - birth.getFullYear()
        let months = today.getMonth() - birth.getMonth()
        let days = today.getDate() - birth.getDate()
        if (days < 0) {
          months--
          const lastMonth = new Date(today.getFullYear(), today.getMonth(), 0)
          days += lastMonth.getDate()
        }
        if (months < 0) { years--; months += 12 }
        updateMultipleFields({
          edad_anios: String(Math.max(0, years)),
          edad_meses: String(Math.max(0, months)),
          edad_dias: String(Math.max(0, days)),
        })
      }
    }

    // Cascading resets: departamento → municipio → poblado
    if (fieldId === 'departamento_residencia') {
      updateMultipleFields({ municipio_residencia: '', poblado: '' })
    }
    if (fieldId === 'municipio_residencia') {
      updateField('poblado', '')
    }

    // Auto-calcular semana epidemiológica
    const autoFields = formFields.filter(f => f.autoCalculate === 'epiWeek' && f.dependsOnDate === fieldId)
    if (autoFields.length > 0) {
      const updates = {}
      for (const af of autoFields) {
        const week = getEpiWeek(value)
        if (week) updates[af.id] = week
      }
      if (Object.keys(updates).length > 0) {
        updateMultipleFields(updates)
      }
    }

    setErrors(prev => {
      const next = { ...prev }
      delete next[fieldId]
      return next
    })
  }, [updateField, updateMultipleFields, formData])

  const handleNext = useCallback(() => {
    const { isValid, errors: pageErrors } = validatePage(currentFields, formData)

    if (!isValid) {
      setErrors(pageErrors)
      const firstErrorId = Object.keys(pageErrors)[0]
      const el = document.getElementById(firstErrorId)
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      return
    }

    setErrors({})
    if (currentStep < totalSteps) {
      setCurrentStep(prev => prev + 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }, [currentFields, formData, currentStep, totalSteps])

  const handlePrev = useCallback(() => {
    if (currentStep > 1) {
      setErrors({})
      setCurrentStep(prev => prev - 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }, [currentStep])

  const handleSubmit = useCallback(async () => {
    const { isValid, errors: pageErrors } = validatePage(currentFields, formData)
    if (!isValid) {
      setErrors(pageErrors)
      return
    }

    // Verificar duplicado por afiliación + fecha (no bloqueo total)
    const afiliacion = formData.afiliacion || ''
    const fecha = formData.fecha_notificacion || ''
    if (afiliacion && fecha && isDuplicate(afiliacion, fecha)) {
      setSubmitError(
        `Ya se envió un registro para la afiliación ${afiliacion} con fecha ${fecha}. ` +
        'Si necesita enviar otro registro para este paciente, cambie la fecha de notificación.'
      )
      return
    }

    const result = await submit(formData)
    if (result?.success) {
      setRegistroId(result.registro_id)
      markAsSubmitted(afiliacion, fecha)
      setShowSuccess(true)
    }
  }, [currentFields, formData, submit, isDuplicate, markAsSubmitted, setSubmitError])

  const handleNewForm = useCallback(() => {
    resetForm()
    setCurrentStep(1)
    setErrors({})
    setShowSuccess(false)
    setRegistroId(null)
    setSubmitError(null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [resetForm, setSubmitError])

  if (showSuccess) {
    return (
      <SuccessScreen
        onNewForm={handleNewForm}
        isOffline={!isOnline}
        registroId={registroId}
        pacienteNombre={formData.nombre_apellido || `${formData.nombres || ''} ${formData.apellidos || ''}`.trim()}
        diagnostico={formData.diagnostico_registrado}
      />
    )
  }

  return (
    <div>
      <ProgressBar
        currentStep={currentStep}
        totalSteps={totalSteps}
        pageLabels={pageLabels}
        visiblePages={visiblePages}
      />

      <ErrorAlert
        message={submitError}
        onDismiss={() => setSubmitError(null)}
      />

      {!isOnline && (
        <div className="mb-5 bg-amber-50 border border-amber-200/60 rounded-xl p-4 flex items-center gap-3 text-sm text-amber-800 shadow-sm">
          <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
            <svg className="w-4 h-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span>
            <strong>Sin conexión.</strong> Los datos se guardarán y se enviarán al reconectarse.
          </span>
        </div>
      )}

      <FormPage
        fields={currentFields}
        formData={formData}
        onFieldChange={handleFieldChange}
        errors={errors}
        pageLabel={getPageLabel(currentPageNum)}
      />

      {/* Navigation */}
      <div className="flex justify-between items-center mt-10 pt-5 border-t border-gray-100">
        <button
          type="button"
          onClick={handlePrev}
          disabled={currentStep === 1}
          className={`inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl font-semibold text-sm transition-all duration-200 ${
            currentStep === 1
              ? 'text-gray-300 cursor-not-allowed'
              : 'text-igss-700 hover:bg-igss-100 hover:text-igss-900 active:scale-95'
          }`}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 19l-7-7 7-7" />
          </svg>
          Anterior
        </button>

        {isLastStep ? (
          <button
            type="button"
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="inline-flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-igss-800 to-igss-700 text-white font-bold text-sm rounded-xl hover:from-igss-900 hover:to-igss-800 transition-all duration-200 shadow-igss hover:shadow-igss-lg active:scale-[0.97] disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Enviando...
              </>
            ) : (
              <>
                Enviar Registro
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
              </>
            )}
          </button>
        ) : (
          <button
            type="button"
            onClick={handleNext}
            className="inline-flex items-center gap-1.5 px-6 py-3 bg-gradient-to-r from-igss-800 to-igss-700 text-white font-bold text-sm rounded-xl hover:from-igss-900 hover:to-igss-800 transition-all duration-200 shadow-igss hover:shadow-igss-lg active:scale-[0.97]"
          >
            Siguiente
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        )}
      </div>

      {pendingCount > 0 && (
        <p className="text-center text-[11px] text-igss-gold-dark mt-3 font-medium">
          {pendingCount} registro(s) pendiente(s) de envío
        </p>
      )}
    </div>
  )
}
