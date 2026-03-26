import TextField from './fields/TextField.jsx'
import SelectField from './fields/SelectField.jsx'
import SearchableSelect from './fields/SearchableSelect.jsx'
import DateField from './fields/DateField.jsx'
import RadioField from './fields/RadioField.jsx'
import CheckboxField from './fields/CheckboxField.jsx'
import TextAreaField from './fields/TextAreaField.jsx'
import NumberField from './fields/NumberField.jsx'
import PhoneField from './fields/PhoneField.jsx'
import FileField from './fields/FileField.jsx'
import LabSampleMatrix from './fields/LabSampleMatrix.jsx'
import { getMunicipios } from '../config/mspasMunicipios.js'
import { getPoblados } from '../config/mspasPoblados.js'
import { getDirecciones, getDepartamentosIGSS, getSecciones } from '../config/igssOrganizacion.js'

const fieldComponents = {
  text: TextField,
  email: TextField,
  select: SelectField,
  date: DateField,
  radio: RadioField,
  checkbox: CheckboxField,
  textarea: TextAreaField,
  number: NumberField,
  phone: PhoneField,
  file: FileField,
  lab_matrix: LabSampleMatrix,
}

function getFieldComponent(field) {
  if (field.searchable && field.type === 'select') return SearchableSelect
  return fieldComponents[field.type]
}

/**
 * Resolve cascading options for fields that depend on another field's value.
 * Supports: departamento → municipio, departamento+municipio → poblado
 */
function resolveFieldOptions(field, formData) {
  if (!field.cascadeFrom) return field.options

  if (field.cascadeFrom === 'departamento_residencia') {
    const depto = formData.departamento_residencia
    return depto ? getMunicipios(depto) : []
  }

  if (field.cascadeFrom === 'municipio_residencia') {
    const depto = formData.departamento_residencia
    const muni = formData.municipio_residencia
    return (depto && muni) ? getPoblados(depto, muni) : []
  }

  // IGSS Organigrama cascading
  if (field.cascadeFrom === 'subgerencia_igss') {
    const sg = formData.subgerencia_igss
    return sg ? getDirecciones(sg) : ['NO APLICA']
  }
  if (field.cascadeFrom === 'subgerencia_igss_depto') {
    const sg = formData.subgerencia_igss
    return sg ? getDepartamentosIGSS(sg) : ['OTRO']
  }
  if (field.cascadeFrom === 'departamento_igss_seccion') {
    const sg = formData.subgerencia_igss
    const depto = formData.departamento_igss
    return (sg && depto) ? getSecciones(sg, depto) : ['OTRA']
  }

  return field.options
}

export default function FormPage({ fields, formData, onFieldChange, errors, pageLabel }) {
  let currentSection = null

  return (
    <div className="page-enter">
      {/* Page title with decorative accent */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-1 h-8 rounded-full bg-gradient-to-b from-igss-700 to-igss-500" />
        <h2 className="text-lg font-extrabold text-igss-900 tracking-tight">
          {pageLabel}
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-5 gap-y-5">
        {fields.filter(f => !f.hidden).map((field) => {
          // Resolve cascading options if needed
          const resolvedField = field.cascadeFrom
            ? { ...field, options: resolveFieldOptions(field, formData) }
            : field

          const FieldComponent = getFieldComponent(resolvedField)
          if (!FieldComponent) return null

          const fieldErrors = errors[field.id] || []
          const hasError = fieldErrors.length > 0
          const isFullWidth = field.colSpan === 'full'

          // Section title
          let sectionEl = null
          if (field.sectionTitle && field.sectionTitle !== currentSection) {
            currentSection = field.sectionTitle
            sectionEl = (
              <div className="col-span-1 md:col-span-2 mt-4 mb-1">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-[2px] bg-igss-gold rounded-full" />
                  <h3 className="text-xs font-bold text-igss-brown uppercase tracking-[0.1em]">
                    {field.sectionTitle}
                  </h3>
                  <div className="flex-1 h-[1px] bg-gray-200" />
                </div>
              </div>
            )
          }

          return (
            <div
              key={field.id}
              className={`field-transition ${isFullWidth ? 'col-span-1 md:col-span-2' : ''}`}
            >
              {sectionEl}
              <label
                htmlFor={field.id}
                className="block text-sm font-semibold text-gray-700 mb-2"
              >
                {field.label}
                {field.required && (
                  <span className="text-igss-red ml-0.5 text-xs">*</span>
                )}
              </label>

              <FieldComponent
                field={resolvedField}
                value={formData[field.id]}
                onChange={onFieldChange}
                error={hasError}
              />

              {field.helpText && !hasError && (
                <p className="mt-1.5 text-[11px] text-gray-400 leading-snug">{field.helpText}</p>
              )}

              {hasError && (
                <div className="mt-1.5 slide-up">
                  {fieldErrors.map((err, i) => (
                    <p key={i} className="text-[11px] text-igss-red font-semibold flex items-center gap-1">
                      <svg className="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      {err}
                    </p>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
