export default function SelectField({ field, value, onChange, error }) {
  return (
    <div className="relative">
      <select
        id={field.id}
        name={field.id}
        value={value || ''}
        onChange={(e) => onChange(field.id, e.target.value)}
        className={`w-full px-4 py-3 rounded-xl border-2 transition-all duration-200 appearance-none pr-10 ${
          error
            ? 'border-igss-red/50 bg-red-50/50 focus:border-igss-red focus:ring-igss-red/20'
            : 'border-gray-200 bg-white hover:border-igss-300 focus:border-igss-600 focus:ring-igss-600/10'
        } shadow-sm focus:outline-none focus:ring-4`}
      >
        <option value="">— Seleccione —</option>
        {(field.options || []).map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
      <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
        <svg className="w-5 h-5 text-igss-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  )
}
