export default function NumberField({ field, value, onChange, error }) {
  return (
    <input
      type="number"
      id={field.id}
      name={field.id}
      value={value ?? ''}
      onChange={(e) => onChange(field.id, e.target.value)}
      placeholder={field.placeholder || ''}
      min={field.validation?.min}
      max={field.validation?.max}
      className={`w-full px-4 py-3 rounded-lg border ${
        error
          ? 'border-red-400 focus:ring-red-300 focus:border-red-400'
          : 'border-gray-300 focus:ring-igss-accent focus:border-igss-accent'
      } bg-white shadow-sm focus:outline-none focus:ring-2 transition-colors`}
      inputMode="numeric"
    />
  )
}
