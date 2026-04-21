import { useState, useRef, useEffect } from 'react'

export default function SearchableSelect({ field, value, onChange, error }) {
  const [isOpen, setIsOpen] = useState(false)
  const [search, setSearch] = useState('')
  const wrapperRef = useRef(null)
  const inputRef = useRef(null)

  const options = field.options || []

  // Normaliza tildes para que "PETEN" matchee "PETÉN", "pinula" matchee "Pinula"
  const normalize = (s) =>
    String(s || '')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .trim()

  const filtered = (() => {
    if (!search) return options
    const q = normalize(search)
    const scored = []
    for (const opt of options) {
      const n = normalize(opt)
      if (n === q) scored.push({ opt, rank: 0 })
      else if (n.startsWith(q)) scored.push({ opt, rank: 1 })
      else if (n.includes(q)) scored.push({ opt, rank: 2 })
    }
    return scored
      .sort((a, b) => a.rank - b.rank)
      .map((x) => x.opt)
  })()

  // Close on click outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelect = (opt) => {
    onChange(field.id, opt)
    setSearch('')
    setIsOpen(false)
  }

  const handleInputFocus = () => {
    setIsOpen(true)
    setSearch('')
  }

  const handleClear = () => {
    onChange(field.id, '')
    setSearch('')
    setIsOpen(false)
  }

  return (
    <div ref={wrapperRef} className="relative">
      {/* Input display */}
      <div
        className={`w-full flex items-center gap-2 px-4 py-3 rounded-xl border-2 transition-all duration-200 cursor-pointer ${
          isOpen
            ? 'border-igss-600 ring-4 ring-igss-600/10'
            : error
              ? 'border-red-300 bg-red-50/50'
              : 'border-gray-200 bg-white hover:border-igss-300'
        } shadow-sm`}
        onClick={() => { setIsOpen(true); inputRef.current?.focus() }}
      >
        {isOpen ? (
          <input
            ref={inputRef}
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onFocus={handleInputFocus}
            placeholder="Escriba para buscar..."
            className="flex-1 outline-none bg-transparent text-sm placeholder:text-gray-400"
            autoFocus
          />
        ) : (
          <span className={`flex-1 text-sm truncate ${value ? 'text-gray-800' : 'text-gray-400'}`}>
            {value || '— Seleccione —'}
          </span>
        )}

        <div className="flex items-center gap-1 flex-shrink-0">
          {value && !isOpen && (
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); handleClear() }}
              className="p-0.5 text-gray-400 hover:text-igss-red transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
          <svg className={`w-5 h-5 text-igss-600 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-xl shadow-lg max-h-60 overflow-y-auto">
          {filtered.length === 0 ? (
            <div className="px-4 py-3 text-sm text-gray-400 text-center">
              No se encontraron resultados
            </div>
          ) : (
            filtered.map((opt) => (
              <button
                key={opt}
                type="button"
                onClick={() => handleSelect(opt)}
                className={`w-full text-left px-4 py-2.5 text-sm transition-colors hover:bg-igss-50 ${
                  value === opt
                    ? 'bg-igss-100 text-igss-800 font-semibold'
                    : 'text-gray-700'
                }`}
              >
                {opt}
              </button>
            ))
          )}
        </div>
      )}
    </div>
  )
}
