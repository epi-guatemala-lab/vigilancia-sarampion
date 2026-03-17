import TextField from './fields/TextField.jsx'
import SelectField from './fields/SelectField.jsx'
import DateField from './fields/DateField.jsx'
import RadioField from './fields/RadioField.jsx'
import CheckboxField from './fields/CheckboxField.jsx'
import TextAreaField from './fields/TextAreaField.jsx'
import NumberField from './fields/NumberField.jsx'
import PhoneField from './fields/PhoneField.jsx'
import FileField from './fields/FileField.jsx'

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
}

export default function FormPage({ fields, formData, onFieldChange, errors, pageLabel }) {
  let currentSection = null

  return (
    <div className="page-enter">
      <h2 className="text-lg font-bold text-igss-primary mb-5 pb-2 border-b-2 border-igss-light">
        {pageLabel}
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-5 gap-y-4">
        {fields.map((field) => {
          const FieldComponent = fieldComponents[field.type]
          if (!FieldComponent) return null

          const fieldErrors = errors[field.id] || []
          const hasError = fieldErrors.length > 0
          const isFullWidth = field.colSpan === 'full'

          // Section title rendering
          let sectionEl = null
          if (field.sectionTitle && field.sectionTitle !== currentSection) {
            currentSection = field.sectionTitle
            sectionEl = (
              <div className="col-span-1 md:col-span-2 mt-3 mb-1">
                <h3 className="text-sm font-bold text-igss-secondary uppercase tracking-wider border-b border-igss-light pb-1">
                  {field.sectionTitle}
                </h3>
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
                className="block text-sm font-semibold text-gray-700 mb-1.5"
              >
                {field.label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </label>

              <FieldComponent
                field={field}
                value={formData[field.id]}
                onChange={onFieldChange}
                error={hasError}
              />

              {field.helpText && !hasError && (
                <p className="mt-1 text-xs text-gray-400">{field.helpText}</p>
              )}

              {hasError && (
                <div className="mt-1 slide-up">
                  {fieldErrors.map((err, i) => (
                    <p key={i} className="text-xs text-red-500 font-medium">{err}</p>
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
