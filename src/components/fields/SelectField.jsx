export default function SelectField({ field, value, onChange, error }) {
  return (
    <select
      id={field.id}
      name={field.id}
      value={value || ''}
      onChange={(e) => onChange(field.id, e.target.value)}
      className={`w-full px-4 py-3 rounded-lg border ${
        error
          ? 'border-red-400 focus:ring-red-300 focus:border-red-400'
          : 'border-gray-300 focus:ring-igss-accent focus:border-igss-accent'
      } bg-white shadow-sm focus:outline-none focus:ring-2 transition-colors appearance-none`}
      style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 8L1 3h10z'/%3E%3C/svg%3E")`,
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'right 12px center',
        paddingRight: '36px',
      }}
    >
      <option value="">— Seleccione —</option>
      {(field.options || []).map((opt) => (
        <option key={opt} value={opt}>
          {opt}
        </option>
      ))}
    </select>
  )
}
