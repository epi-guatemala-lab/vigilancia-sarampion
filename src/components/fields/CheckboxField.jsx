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
    <div className="flex flex-wrap gap-3">
      {options.map((opt) => (
        <label
          key={opt}
          className={`inline-flex items-center px-4 py-2.5 rounded-lg border cursor-pointer transition-all ${
            selected.includes(opt)
              ? 'bg-igss-primary text-white border-igss-primary shadow-md'
              : error
                ? 'bg-white border-red-300 hover:bg-red-50'
                : 'bg-white border-gray-300 hover:bg-igss-light hover:border-igss-accent'
          }`}
        >
          <input
            type="checkbox"
            checked={selected.includes(opt)}
            onChange={() => handleChange(opt)}
            className="sr-only"
          />
          <span className="text-sm font-medium">{opt}</span>
        </label>
      ))}
    </div>
  )
}
