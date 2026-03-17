export default function RadioField({ field, value, onChange, error }) {
  const options = field.options || []
  const labels = field.optionLabels || {}

  return (
    <div className="flex flex-wrap gap-3">
      {options.map((opt) => (
        <label
          key={opt}
          className={`inline-flex items-center px-4 py-2.5 rounded-lg border cursor-pointer transition-all ${
            value === opt
              ? 'bg-igss-primary text-white border-igss-primary shadow-md'
              : error
                ? 'bg-white border-red-300 hover:bg-red-50'
                : 'bg-white border-gray-300 hover:bg-igss-light hover:border-igss-accent'
          }`}
        >
          <input
            type="radio"
            name={field.id}
            value={opt}
            checked={value === opt}
            onChange={(e) => onChange(field.id, e.target.value)}
            className="sr-only"
          />
          <span className="text-sm font-medium">
            {labels[opt] || opt}
          </span>
        </label>
      ))}
    </div>
  )
}
