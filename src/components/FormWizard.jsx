import { useState, useCallback } from 'react'
import FormPage from './FormPage.jsx'
import ProgressBar from './ui/ProgressBar.jsx'
import SuccessScreen from './ui/SuccessScreen.jsx'
import ErrorAlert from './ui/ErrorAlert.jsx'
import { useFormState } from '../hooks/useFormState.js'
import { useConditionalFields } from '../hooks/useConditionalFields.js'
import { useGoogleSheets } from '../hooks/useGoogleSheets.js'
import { validatePage } from '../utils/validation.js'
import { pageLabels } from '../config/formSchema.js'

export default function FormWizard() {
  const [currentStep, setCurrentStep] = useState(1)
  const [errors, setErrors] = useState({})
  const [showSuccess, setShowSuccess] = useState(false)

  const {
    formData,
    updateField,
    resetForm,
    hasBeenSubmitted,
    markAsSubmitted,
    clearSubmitted,
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
    // Clear error for this field when changed
    setErrors(prev => {
      const next = { ...prev }
      delete next[fieldId]
      return next
    })
  }, [updateField])

  const handleNext = useCallback(() => {
    const { isValid, errors: pageErrors } = validatePage(currentFields, formData)

    if (!isValid) {
      setErrors(pageErrors)
      // Scroll to first error
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
    // Validate current page first
    const { isValid, errors: pageErrors } = validatePage(currentFields, formData)
    if (!isValid) {
      setErrors(pageErrors)
      return
    }

    // Check duplicates
    if (hasBeenSubmitted()) {
      setSubmitError('Este formulario ya fue enviado recientemente. Espere antes de enviar otro.')
      return
    }

    const success = await submit(formData)
    if (success) {
      markAsSubmitted()
      setShowSuccess(true)
    }
  }, [currentFields, formData, submit, hasBeenSubmitted, markAsSubmitted, setSubmitError])

  const handleNewForm = useCallback(() => {
    resetForm()
    clearSubmitted()
    setCurrentStep(1)
    setErrors({})
    setShowSuccess(false)
    setSubmitError(null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [resetForm, clearSubmitted, setSubmitError])

  if (showSuccess) {
    return <SuccessScreen onNewForm={handleNewForm} isOffline={!isOnline} />
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

      {/* Offline banner */}
      {!isOnline && (
        <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex items-center gap-2 text-sm text-yellow-800">
          <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636a9 9 0 010 12.728M5.636 5.636a9 9 0 000 12.728M12 12h.01" />
          </svg>
          <span>
            <strong>Sin conexión.</strong> Los datos se guardarán localmente y se enviarán al reconectarse.
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

      {/* Navigation buttons */}
      <div className="flex justify-between items-center mt-8 pt-4 border-t border-gray-200">
        <button
          type="button"
          onClick={handlePrev}
          disabled={currentStep === 1}
          className={`inline-flex items-center px-5 py-2.5 rounded-lg font-medium transition-all ${
            currentStep === 1
              ? 'text-gray-400 cursor-not-allowed'
              : 'text-igss-primary hover:bg-igss-light'
          }`}
        >
          <svg className="w-5 h-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Anterior
        </button>

        {isLastStep ? (
          <button
            type="button"
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="inline-flex items-center px-8 py-3 bg-igss-green text-white font-bold rounded-lg hover:bg-green-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Enviando...
              </>
            ) : (
              <>
                Enviar Registro
                <svg className="w-5 h-5 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </>
            )}
          </button>
        ) : (
          <button
            type="button"
            onClick={handleNext}
            className="inline-flex items-center px-6 py-2.5 bg-igss-primary text-white font-semibold rounded-lg hover:bg-igss-dark transition-all shadow-md hover:shadow-lg"
          >
            Siguiente
            <svg className="w-5 h-5 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        )}
      </div>

      {/* Pending count */}
      {pendingCount > 0 && (
        <p className="text-center text-xs text-amber-600 mt-3">
          {pendingCount} registro(s) pendiente(s) de envío
        </p>
      )}
    </div>
  )
}
