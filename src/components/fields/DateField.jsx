export default function DateField({ field, value, onChange, error }) {
  const today = new Date().toISOString().split('T')[0]

  return (
    <input
      type="date"
      id={field.id}
      name={field.id}
      value={value || ''}
      onChange={(e) => onChange(field.id, e.target.value)}
      max={field.validation?.noFuture ? today : undefined}
      className={`w-full px-4 py-3 rounded-xl border-2 transition-all duration-200 ${
        error
          ? 'border-igss-red/50 bg-red-50/50 focus:border-igss-red focus:ring-igss-red/20'
          : 'border-gray-200 bg-white hover:border-igss-300 focus:border-igss-600 focus:ring-igss-600/10'
      } shadow-sm focus:outline-none focus:ring-4`}
    />
  )
}
