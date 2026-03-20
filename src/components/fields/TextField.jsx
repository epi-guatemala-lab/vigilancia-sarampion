export default function TextField({ field, value, onChange, error }) {
  const isReadOnly = field.readOnly

  return (
    <input
      type={field.type === 'email' ? 'email' : 'text'}
      id={field.id}
      name={field.id}
      value={value || ''}
      onChange={(e) => !isReadOnly && onChange(field.id, e.target.value)}
      placeholder={field.placeholder || ''}
      maxLength={field.validation?.maxLength}
      readOnly={isReadOnly}
      tabIndex={isReadOnly ? -1 : undefined}
      className={`w-full px-4 py-3 rounded-xl border-2 transition-all duration-200 ${
        isReadOnly
          ? 'border-igss-gold/40 bg-igss-gold-50 text-igss-800 font-bold cursor-default'
          : error
            ? 'border-igss-red/50 bg-red-50/50 focus:border-igss-red focus:ring-igss-red/20'
            : 'border-gray-200 bg-white hover:border-igss-300 focus:border-igss-600 focus:ring-igss-600/10'
      } shadow-sm focus:outline-none focus:ring-4 placeholder:text-gray-400`}
      autoComplete="off"
    />
  )
}
