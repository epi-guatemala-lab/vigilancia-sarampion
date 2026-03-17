export default function RadioField({ field, value, onChange, error }) {
  const options = field.options || []
  const labels = field.optionLabels || {}

  return (
    <div className="flex flex-wrap gap-2.5">
      {options.map((opt) => {
        const isSelected = value === opt
        return (
          <label
            key={opt}
            className={`inline-flex items-center gap-2 px-5 py-3 rounded-xl border-2 cursor-pointer transition-all duration-200 select-none ${
              isSelected
                ? 'bg-igss-800 text-white border-igss-800 shadow-igss'
                : error
                  ? 'bg-white text-gray-700 border-red-300 hover:bg-red-50'
                  : 'bg-white text-gray-700 border-gray-200 hover:border-igss-400 hover:bg-igss-50'
            }`}
          >
            <input
              type="radio"
              name={field.id}
              value={opt}
              checked={isSelected}
              onChange={(e) => onChange(field.id, e.target.value)}
              className="sr-only"
            />
            <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all ${
              isSelected
                ? 'border-white bg-white/20'
                : 'border-gray-400'
            }`}>
              {isSelected && <div className="w-2 h-2 rounded-full bg-white" />}
            </div>
            <span className="text-sm font-semibold">
              {labels[opt] || opt}
            </span>
          </label>
        )
      })}
    </div>
  )
}
