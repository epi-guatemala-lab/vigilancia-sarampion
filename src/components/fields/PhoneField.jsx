export default function PhoneField({ field, value, onChange, error }) {
  const handleChange = (e) => {
    // Solo permitir dígitos
    const cleaned = e.target.value.replace(/\D/g, '').slice(0, 8)
    onChange(field.id, cleaned)
  }

  return (
    <input
      type="tel"
      id={field.id}
      name={field.id}
      value={value || ''}
      onChange={handleChange}
      placeholder={field.placeholder || '0000 0000'}
      maxLength={8}
      className={`w-full px-4 py-3 rounded-lg border ${
        error
          ? 'border-red-400 focus:ring-red-300 focus:border-red-400'
          : 'border-gray-300 focus:ring-igss-accent focus:border-igss-accent'
      } bg-white shadow-sm focus:outline-none focus:ring-2 transition-colors`}
      inputMode="tel"
    />
  )
}
