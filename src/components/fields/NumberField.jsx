export default function NumberField({ field, value, onChange, error }) {
  const isReadOnly = field.readOnly

  return (
    <input
      type="number"
      id={field.id}
      name={field.id}
      value={value ?? ''}
      onChange={(e) => !isReadOnly && onChange(field.id, e.target.value)}
      placeholder={field.placeholder || ''}
      min={field.validation?.min}
      max={field.validation?.max}
      readOnly={isReadOnly}
      tabIndex={isReadOnly ? -1 : undefined}
      className={`w-full px-4 py-3 rounded-lg border ${
        isReadOnly
          ? 'border-igss-accent/30 bg-igss-light text-igss-primary font-bold cursor-default'
          : error
            ? 'border-red-400 focus:ring-red-300 focus:border-red-400 bg-white'
            : 'border-gray-300 focus:ring-igss-accent focus:border-igss-accent bg-white'
      } shadow-sm focus:outline-none focus:ring-2 transition-colors`}
      inputMode="numeric"
    />
  )
}
