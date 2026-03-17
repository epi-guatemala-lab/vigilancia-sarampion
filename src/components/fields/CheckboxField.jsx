export default function CheckboxField({ field, value, onChange, error }) {
  const options = field.options || []
  const selected = Array.isArray(value) ? value : value ? [value] : []

  const handleChange = (opt) => {
    const newValue = selected.includes(opt)
      ? selected.filter(v => v !== opt)
      : [...selected, opt]
    onChange(field.id, newValue)
  }

  return (
    <div className="flex flex-wrap gap-2.5">
      {options.map((opt) => (
        <label
          key={opt}
          className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border-2 cursor-pointer transition-all duration-200 select-none ${
            selected.includes(opt)
              ? 'bg-igss-800 text-white border-igss-800 shadow-igss'
              : error
                ? 'bg-white border-igss-red/30 hover:bg-red-50/50'
                : 'bg-white border-gray-200 hover:border-igss-400 hover:bg-igss-50'
          }`}
        >
          <input
            type="checkbox"
            checked={selected.includes(opt)}
            onChange={() => handleChange(opt)}
            className="sr-only"
          />
          <div className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all ${
            selected.includes(opt)
              ? 'border-white bg-white/20'
              : 'border-gray-300'
          }`}>
            {selected.includes(opt) && (
              <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>
          <span className="text-sm font-medium">{opt}</span>
        </label>
      ))}
    </div>
  )
}
