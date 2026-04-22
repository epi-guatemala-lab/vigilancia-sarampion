import { useState, useCallback, useRef } from 'react'
import FormPage from './FormPage.jsx'
import ProgressBar from './ui/ProgressBar.jsx'
import SuccessScreen from './ui/SuccessScreen.jsx'
import ErrorAlert from './ui/ErrorAlert.jsx'
import { useFormState } from '../hooks/useFormState.js'
import { useConditionalFields } from '../hooks/useConditionalFields.js'
import { cleanHiddenFieldData } from '../config/conditionalLogic.js'
import { useGoogleSheets } from '../hooks/useGoogleSheets.js'
import { validatePage, validateCrossFieldDates, validateCrossFieldDatesForPage } from '../utils/validation.js'
import { getEpiWeek } from '../utils/formatters.js'
import { pageLabels, formFields, diagnosticosMap, getMunicipios } from '../config/formSchema.js'
import { unidadesMedicas as STATIC_UNIDADES } from '../config/unidadesMedicas.js'
import { useUnidadesPublic } from '../hooks/useUnidadesPublic.js'

export default function FormWizard() {
  const [currentStep, setCurrentStep] = useState(1)
  const [errors, setErrors] = useState({})
  const [showSuccess, setShowSuccess] = useState(false)
  const [successInfo, setSuccessInfo] = useState(null)
  const [registroId, setRegistroId] = useState(null)
  const [dateWarnings, setDateWarnings] = useState([])
  const [deathConfirm, setDeathConfirm] = useState(null) // {fieldId, value, label}
  const pendingDeathChange = useRef(null)

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

  // Cargar unidades dinámicas del backend (fallback a estático mientras carga o si falla)
  const { unidades: dynUnidades } = useUnidadesPublic()
  const unidadesMedicas = dynUnidades && dynUnidades.length ? dynUnidades : STATIC_UNIDADES
  const unidadesNombresDyn = unidadesMedicas.map((u) => u.nombre)

  const totalSteps = visiblePages.length
  const currentPageNum = visiblePages[currentStep - 1]
  const rawFields = visibleFieldsByPage[currentPageNum] || []
  // Inyectar options dinámicas en fields select que originalmente usaban unidadesMedicasNombres
  const currentFields = rawFields.map((f) => {
    if (f.id === 'unidad_medica') {
      return { ...f, options: unidadesNombresDyn }
    }
    if (f.id === 'unidad_medica_trabaja' || f.id === 'hospital_deriva') {
      // Algunos campos agregan 'OTRA' / 'OTRO HOSPITAL' al final
      const extras = (f.options || []).filter(
        (o) => !unidadesNombresDyn.includes(o),
      )
      return { ...f, options: [...unidadesNombresDyn, ...extras] }
    }
    return f
  })
  const isLastStep = currentStep === totalSteps

  const handleFieldChange = useCallback((fieldId, value) => {
    // Normalize comma to dot for temperature
    if (fieldId === 'temperatura_celsius' && value) {
      value = value.replace(',', '.')
    }

    // Confirmación de fallecido — interceptar ANTES de guardar
    const isDeathSelection =
      (fieldId === 'condicion_final_paciente' && value === 'Fallecido') ||
      (fieldId === 'condicion_egreso' && value === 'MUERTO')
    if (isDeathSelection) {
      pendingDeathChange.current = { fieldId, value }
      setDeathConfirm({
        fieldId,
        value,
        label: fieldId === 'condicion_final_paciente' ? 'Condición Final: Fallecido' : 'Egreso: Muerto',
      })
      return // No guardar aún — esperar confirmación
    }

    updateField(fieldId, value)

    // Auto-map diagnóstico → código CIE-10
    if (fieldId === 'diagnostico_registrado' && diagnosticosMap[value]) {
      updateField('codigo_cie10', diagnosticosMap[value])
      // Auto-derive diagnostico_sospecha from CIE-10 (add to array, don't replace)
      const code = diagnosticosMap[value]
      if (code.startsWith('B05')) {
        const current = Array.isArray(formData.diagnostico_sospecha) ? formData.diagnostico_sospecha : []
        if (!current.includes('Sarampión')) {
          updateField('diagnostico_sospecha', [...current, 'Sarampión'])
        }
      } else if (code.startsWith('B06')) {
        const current = Array.isArray(formData.diagnostico_sospecha) ? formData.diagnostico_sospecha : []
        if (!current.includes('Rubéola')) {
          updateField('diagnostico_sospecha', [...current, 'Rubéola'])
        }
      }
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

    // Auto-clear motivo_no_3_muestras when all 3 samples are SI
    if (['muestra_suero', 'muestra_hisopado', 'muestra_orina'].includes(fieldId)) {
      const suero = (fieldId === 'muestra_suero' ? value : formData.muestra_suero) || ''
      const hisop = (fieldId === 'muestra_hisopado' ? value : formData.muestra_hisopado) || ''
      const orina = (fieldId === 'muestra_orina' ? value : formData.muestra_orina) || ''
      if (suero === 'SI' && hisop === 'SI' && orina === 'SI') {
        updateField('motivo_no_3_muestras', '')
      }
    }

    // Auto-calculate trimestre from semanas_embarazo
    if (fieldId === 'semanas_embarazo' && value) {
      const semanas = parseInt(value)
      if (!isNaN(semanas) && semanas > 0) {
        const trimestre = semanas <= 13 ? '1' : semanas <= 26 ? '2' : '3'
        updateField('trimestre_embarazo', trimestre)
      }
    }

    // Cascading reset al cambiar viaje_pais:
    //  - si NO es Guatemala, limpiar depto/municipio (catálogo GT)
    //  - si es Guatemala, limpiar viaje_pais_otro y viaje_ciudad_destino
    //  - si no es OTRO, limpiar viaje_pais_otro
    if (fieldId === 'viaje_pais') {
      const resets = {}
      if (value !== 'GUATEMALA') {
        resets.viaje_departamento = ''
        resets.viaje_municipio = ''
      }
      if (value === 'GUATEMALA') {
        resets.viaje_pais_otro = ''
        resets.viaje_ciudad_destino = ''
      }
      if (value !== 'OTRO') {
        resets.viaje_pais_otro = ''
      }
      if (Object.keys(resets).length > 0) updateMultipleFields(resets)
    }

    // Auto-infer destino_viaje from structured travel fields
    if (['viaje_pais', 'viaje_departamento', 'viaje_municipio', 'viaje_ciudad_destino', 'viaje_pais_otro'].includes(fieldId)) {
      let pais = fieldId === 'viaje_pais' ? value : (formData.viaje_pais || '')
      // Si el usuario eligió OTRO, preferir el texto libre como "país"
      if (pais === 'OTRO') {
        pais = fieldId === 'viaje_pais_otro' ? value : (formData.viaje_pais_otro || 'OTRO')
      }
      const depto = fieldId === 'viaje_departamento' ? value : (formData.viaje_departamento || '')
      const muni = fieldId === 'viaje_municipio' ? value : (formData.viaje_municipio || '')
      const ciudad = fieldId === 'viaje_ciudad_destino' ? value : (formData.viaje_ciudad_destino || '')
      // Si el país es Guatemala: usar muni/depto. Si es exterior: usar ciudad + pais.
      const pieces = pais === 'GUATEMALA' ? [muni, depto, pais] : [ciudad, pais]
      const destino = pieces.filter(Boolean).join(', ')
      if (destino) updateField('destino_viaje', destino)
    }

    // Auto-infer legacy vaccine fields from new per-type fields (bidirectional)
    if (fieldId === 'dosis_spr' && value) {
      updateMultipleFields({
        tipo_vacuna: 'SRP Sarampión Rubéola Paperas',
        numero_dosis_spr: value === 'Más de 3' ? 'Más de 3 dosis' : `${value} dosis`,
      })
    }
    if (fieldId === 'fecha_ultima_spr' && value) {
      updateField('fecha_ultima_dosis', value)
    }
    if (fieldId === 'dosis_sr' && value) {
      if (!formData.dosis_spr) { // Only override if SPR not set
        updateMultipleFields({
          tipo_vacuna: 'SR Sarampión Rubéola',
          numero_dosis_spr: value === 'Más de 3' ? 'Más de 3 dosis' : `${value} dosis`,
        })
      }
    }
    if (fieldId === 'fecha_ultima_sr' && value) {
      if (!formData.fecha_ultima_spr) updateField('fecha_ultima_dosis', value)
    }

    // Auto-generate complicaciones text from checkboxes (legacy compat)
    if (fieldId.startsWith('comp_') || fieldId === 'tiene_complicaciones') {
      const compFields = ['comp_neumonia', 'comp_encefalitis', 'comp_diarrea',
        'comp_trombocitopenia', 'comp_otitis', 'comp_ceguera']
      const compLabels = {
        comp_neumonia: 'Neumonía', comp_encefalitis: 'Encefalitis',
        comp_diarrea: 'Diarrea', comp_trombocitopenia: 'Trombocitopenia',
        comp_otitis: 'Otitis Media Aguda', comp_ceguera: 'Ceguera'
      }
      const activas = compFields
        .filter(f => (f === fieldId ? value : formData[f]) === 'SI')
        .map(f => compLabels[f])
      const otra = fieldId === 'comp_otra_texto' ? value : (formData.comp_otra_texto || '')
      if (otra) activas.push(otra)
      updateField('complicaciones', activas.join(', ') || '')
    }

    // Auto-derive asintomatico: if ALL signs are NO → asintomatico = SI
    if (fieldId.startsWith('signo_')) {
      const signs = ['signo_fiebre', 'signo_exantema', 'signo_manchas_koplik', 'signo_tos',
        'signo_conjuntivitis', 'signo_coriza', 'signo_adenopatias', 'signo_artralgia']
      const allNO = signs.every(s => {
        const v = (s === fieldId ? value : formData[s]) || ''
        return v === 'NO'
      })
      if (allNO) updateField('asintomatico', 'SI')
      else if (value === 'SI') updateField('asintomatico', 'NO')
    }

    // Cross-sync: symptom flags ↔ symptom dates
    // If signo_exantema = NO → clear fecha_inicio_erupcion
    // If signo_fiebre = NO → clear fecha_inicio_fiebre
    if (fieldId === 'signo_exantema' && value === 'NO') {
      updateField('fecha_inicio_erupcion', '')
    }
    if (fieldId === 'signo_fiebre' && value === 'NO') {
      updateField('fecha_inicio_fiebre', '')
    }
    // If fecha_inicio_erupcion is filled → auto-set signo_exantema = SI
    if (fieldId === 'fecha_inicio_erupcion' && value) {
      updateField('signo_exantema', 'SI')
    }
    // If fecha_inicio_fiebre is filled → auto-set signo_fiebre = SI
    if (fieldId === 'fecha_inicio_fiebre' && value) {
      updateField('signo_fiebre', 'SI')
    }

    // Auto-infer condicion_egreso from condicion_final_paciente (EPIWEB compat)
    if (fieldId === 'condicion_final_paciente') {
      const egresoMap = {
        'Recuperado': 'MEJORADO', 'Con Secuelas': 'MEJORADO',
        'Fallecido': 'MUERTO', 'Desconocido': ''
      }
      if (egresoMap[value] !== undefined) updateField('condicion_egreso', egresoMap[value])
    }
    // Sync inverso: condicion_egreso='MUERTO' → condicion_final_paciente='Fallecido'
    // (el campo condicion_egreso puede llenarse por import/carga aunque esté hidden
    // en la UI, así que mantenemos ambas direcciones sincronizadas)
    if (fieldId === 'condicion_egreso' && value === 'MUERTO'
        && formData.condicion_final_paciente !== 'Fallecido') {
      updateField('condicion_final_paciente', 'Fallecido')
    }

    // Cascading resets: area_salud_mspas → distrito_salud_mspas
    if (fieldId === 'area_salud_mspas') {
      updateField('distrito_salud_mspas', '')
    }

    // Auto-fill MSPAS: al elegir unidad médica IGSS, pre-llenar el departamento MSPAS.
    // El municipio MSPAS queda manual (nombre de unidad no mapea 1:1 a municipio).
    // Siempre sobreescribe para reflejar el departamento real de la unidad actual;
    // el usuario puede editarlo manualmente después si la dirección difiere.
    if (fieldId === 'unidad_medica' && value) {
      const match = unidadesMedicas.find((u) => u.nombre === value)
      if (match && match.departamento) {
        updateMultipleFields({
          area_salud_mspas: match.departamento,
          distrito_salud_mspas: '',
        })
      }
    }

    // Limpiar motivo_no_recoleccion* al cambiar recolecto_muestra=SI
    if (fieldId === 'recolecto_muestra' && value === 'SI') {
      updateMultipleFields({ motivo_no_recoleccion: '', motivo_no_recoleccion_otro: '' })
    }

    // Cascading resets: departamento → municipio → poblado
    if (fieldId === 'departamento_residencia') {
      updateMultipleFields({ municipio_residencia: '', poblado: '' })
    }
    if (fieldId === 'municipio_residencia') {
      updateField('poblado', '')
    }

    // IGSS organigrama cascading resets
    if (fieldId === 'subgerencia_igss') {
      updateMultipleFields({
        direccion_igss: '', direccion_igss_otra: '',
        departamento_igss: '', departamento_igss_otro: '',
        seccion_igss: '', seccion_igss_otra: ''
      })
    }
    if (fieldId === 'departamento_igss') {
      updateField('seccion_igss', '')
    }
    // Reset all IGSS fields when es_empleado_igss changes to NO
    if (fieldId === 'es_empleado_igss' && value === 'NO') {
      updateMultipleFields({
        unidad_medica_trabaja: '', puesto_desempena: '',
        subgerencia_igss: '', subgerencia_igss_otra: '',
        direccion_igss: '', direccion_igss_otra: '',
        departamento_igss: '', departamento_igss_otro: '',
        seccion_igss: '', seccion_igss_otra: '',
      })
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

    // Advertencias cruzadas de fechas — solo las aplicables a esta pestaña
    const pageFieldIds = currentFields.map((f) => f.id)
    const pageWarnings = validateCrossFieldDatesForPage(formData, pageFieldIds)
    if (pageWarnings.length > 0) {
      setDateWarnings(pageWarnings)
      // Mostrar banner rojo inline y hacer scroll al tope; usuario lee y decide
      window.scrollTo({ top: 0, behavior: 'smooth' })
      const proceed = window.confirm(
        'Se detectaron inconsistencias en fechas de esta pestaña:\n\n' +
        pageWarnings.map((w, i) => `${i + 1}. ${w}`).join('\n') +
        '\n\n¿Desea continuar a la siguiente pestaña?'
      )
      if (!proceed) return
    } else {
      setDateWarnings([])
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

    // Cross-field date validation (warnings, not blocking)
    const warnings = validateCrossFieldDates(formData)
    if (warnings.length > 0) {
      setDateWarnings(warnings)
      const proceed = window.confirm(
        'Se detectaron posibles inconsistencias en fechas:\n\n' +
        warnings.map((w, i) => `${i + 1}. ${w}`).join('\n') +
        '\n\n¿Desea continuar con el envío?'
      )
      if (!proceed) return
    } else {
      setDateWarnings([])
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

    // Clean hidden field data before submission
    const cleanedData = cleanHiddenFieldData(formData, formFields)
    // Hardcode IGSS values
    cleanedData.es_seguro_social = 'SI'           // Siempre Seguro Social
    cleanedData.establecimiento_privado = 'NO'     // Nunca privado
    cleanedData.establecimiento_privado_nombre = ''
    // fuente_notificacion: no aplica al IGSS (no hacen investigación de campo)
    cleanedData.form_version = 'v2'                // GoData format marker
    const result = await submit(cleanedData)
    if (result?.success) {
      setRegistroId(result.registro_id)
      markAsSubmitted(afiliacion, fecha)
      // Guardar datos de display ANTES de limpiar el formulario
      setSuccessInfo({
        nombre: formData.nombre_apellido || `${formData.nombres || ''} ${formData.apellidos || ''}`.trim(),
        diagnostico: formData.diagnostico_registrado,
      })
      // Limpiar localStorage inmediatamente para evitar datos residuales
      // si el usuario cierra/refresca en vez de click "Nuevo Registro"
      resetForm()
      setShowSuccess(true)
    }
  }, [currentFields, formData, submit, isDuplicate, markAsSubmitted, resetForm, setSubmitError])

  const handleNewForm = useCallback(() => {
    resetForm()
    setCurrentStep(1)
    setErrors({})
    setDateWarnings([])
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
        pacienteNombre={successInfo?.nombre || ''}
        diagnostico={successInfo?.diagnostico || ''}
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

      {dateWarnings.length > 0 && (
        <div className="mb-5 bg-red-50 border border-red-300 rounded-xl p-4 text-sm text-red-800 shadow-sm">
          <div className="flex items-center gap-2 mb-2 font-semibold">
            <svg className="w-5 h-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            Advertencias de fechas
          </div>
          <ul className="list-disc list-inside space-y-1">
            {dateWarnings.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
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

      {/* Modal de confirmación de fallecido */}
      {deathConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
          <div className="bg-white rounded-2xl shadow-2xl max-w-sm w-full overflow-hidden animate-in">
            <div className="bg-red-600 px-6 py-4 flex items-center gap-3">
              <svg className="w-8 h-8 text-white flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <div>
                <h3 className="text-white font-bold text-lg">Confirmar Fallecimiento</h3>
                <p className="text-red-100 text-xs">{deathConfirm.label}</p>
              </div>
            </div>
            <div className="px-6 py-5">
              <p className="text-gray-700 text-sm leading-relaxed">
                Está a punto de registrar a este paciente como <span className="font-bold text-red-700">fallecido</span>.
                Esta acción generará una alerta epidemiológica.
              </p>
              <p className="text-gray-500 text-xs mt-3">
                Si fue un error, presione Cancelar para corregir.
              </p>
            </div>
            <div className="px-6 pb-5 flex gap-3">
              <button
                onClick={() => {
                  setDeathConfirm(null)
                  pendingDeathChange.current = null
                }}
                className="flex-1 px-4 py-2.5 border-2 border-gray-300 text-gray-600 font-semibold text-sm rounded-xl hover:bg-gray-50 transition-all"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  if (pendingDeathChange.current) {
                    const { fieldId: fid, value: val } = pendingDeathChange.current
                    updateField(fid, val)
                    // Trigger downstream auto-mappings
                    if (fid === 'condicion_final_paciente') {
                      const egresoMap = { 'Fallecido': 'MUERTO' }
                      if (egresoMap[val]) updateField('condicion_egreso', egresoMap[val])
                    }
                  }
                  setDeathConfirm(null)
                  pendingDeathChange.current = null
                }}
                className="flex-1 px-4 py-2.5 bg-red-600 text-white font-bold text-sm rounded-xl hover:bg-red-700 transition-all shadow-sm"
              >
                Confirmar Fallecimiento
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
