export default function RadioField({ field, value, onChange, error }) {
  const options = field.options || []
  const labels = field.optionLabels || {}

  return (
    <div className="flex flex-wrap gap-2.5">
      {options.map((opt) => (
        <label
          key={opt}
          className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border-2 cursor-pointer transition-all duration-200 select-none ${
            value === opt
              ? 'bg-igss-800 text-white border-igss-800 shadow-igss'
              : error
                ? 'bg-white border-igss-red/30 hover:bg-red-50/50'
                : 'bg-white border-gray-200 hover:border-igss-400 hover:bg-igss-50'
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
          <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center transition-all ${
            value === opt
              ? 'border-white'
              : 'border-gray-300'
          }`}>
            {value === opt && <div className="w-2 h-2 rounded-full bg-white" />}
          </div>
          <span className="text-sm font-medium">
            {labels[opt] || opt}
          </span>
        </label>
      ))}
    </div>
  )
}
