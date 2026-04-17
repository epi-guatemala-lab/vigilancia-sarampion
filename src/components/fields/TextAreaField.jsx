export default function TextAreaField({ field, value, onChange, error }) {
  const shouldUppercase = field.preserveCase !== true

  const handleChange = (e) => {
    const raw = e.target.value
    onChange(field.id, shouldUppercase ? raw.toUpperCase() : raw)
  }

  return (
    <textarea
      id={field.id}
      name={field.id}
      value={value || ''}
      onChange={handleChange}
      placeholder={field.placeholder || ''}
      rows={3}
      maxLength={field.validation?.maxLength}
      style={shouldUppercase ? { textTransform: 'uppercase' } : undefined}
      className={`w-full px-4 py-3 rounded-xl border-2 transition-all duration-200 resize-y ${
        error
          ? 'border-igss-red/50 bg-red-50/50 focus:border-igss-red focus:ring-igss-red/20'
          : 'border-gray-200 bg-white hover:border-igss-300 focus:border-igss-600 focus:ring-igss-600/10'
      } shadow-sm focus:outline-none focus:ring-4 placeholder:text-gray-400`}
    />
  )
}
