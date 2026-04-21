import { useMemo } from 'react'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SLOT_LABELS = {
  suero_1:    'Suero (Anticuerpo)',
  orina_1:    'Orina (ARN viral)',
  hisopado_1: 'Hisopado Nasofaríngeo (ARN viral)',
  otro:       'Otro',
}

const EMPTY_SAMPLE = (slot) => ({
  slot,
  numero_muestra:   '',
  fecha_toma:       '',
  fecha_envio:      '',
  sarampion_igm:    '',
  sarampion_igg:    '',
  sarampion_avidez: '',
  rubeola_igm:      '',
  rubeola_igg:      '',
  rubeola_avidez:   '',
  fecha_resultado:  '',
})

const DEFAULT_SAMPLES = [
  EMPTY_SAMPLE('suero_1'),
  EMPTY_SAMPLE('orina_1'),
  EMPTY_SAMPLE('hisopado_1'),
  EMPTY_SAMPLE('otro'),
]

// Select option sets
const IgM_IgG_OPTIONS = [
  { value: '0', label: '0 — Negativo' },
  { value: '1', label: '1 — Positivo' },
  { value: '2', label: '2 — Inadecuada' },
  { value: '3', label: '3 — Indeterminado' },
  { value: '4', label: '4 — No procesada' },
]

const AVIDEZ_OPTIONS = [
  { value: '5', label: '5 — Alta' },
  { value: '6', label: '6 — Baja' },
]

// Column definitions for each sample row
// type: 'text' | 'date' | 'igm_igg' | 'avidez'
const COLUMNS = [
  { key: 'numero_muestra',   label: 'Orden de laboratorio', type: 'text', group: null },
  { key: 'fecha_toma',       label: 'Fecha Toma',     type: 'date',    group: null },
  { key: 'fecha_envio',      label: 'Fecha Envío',    type: 'date',    group: null },
  { key: 'sarampion_igm',    label: 'IgM',            type: 'igm_igg', group: 'sarampion' },
  { key: 'sarampion_igg',    label: 'IgG',            type: 'igm_igg', group: 'sarampion' },
  { key: 'sarampion_avidez', label: 'Avidez',         type: 'avidez',  group: 'sarampion' },
  { key: 'rubeola_igm',      label: 'IgM',            type: 'igm_igg', group: 'rubeola'   },
  { key: 'rubeola_igg',      label: 'IgG',            type: 'igm_igg', group: 'rubeola'   },
  { key: 'rubeola_avidez',   label: 'Avidez',         type: 'avidez',  group: 'rubeola'   },
  { key: 'fecha_resultado',  label: 'Fecha Resultado', type: 'date',   group: null },
]

// ---------------------------------------------------------------------------
// Small inline input components (compact for matrix use)
// ---------------------------------------------------------------------------

function MatrixTextInput({ value, onChange }) {
  return (
    <input
      type="text"
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      className="w-full min-w-[80px] px-2 py-1 text-xs rounded-lg border border-gray-200 bg-white
                 hover:border-igss-300 focus:border-igss-600 focus:ring-2 focus:ring-igss-600/10
                 focus:outline-none transition-all duration-150 shadow-sm"
    />
  )
}

function MatrixDateInput({ value, onChange }) {
  const today = new Date().toISOString().split('T')[0]
  return (
    <input
      type="date"
      value={value || ''}
      max={today}
      onChange={(e) => onChange(e.target.value)}
      className="w-full min-w-[120px] px-2 py-1 text-xs rounded-lg border border-gray-200 bg-white
                 hover:border-igss-300 focus:border-igss-600 focus:ring-2 focus:ring-igss-600/10
                 focus:outline-none transition-all duration-150 shadow-sm"
    />
  )
}

function MatrixSelect({ value, onChange, options, placeholder = '—' }) {
  return (
    <div className="relative">
      <select
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        className="w-full min-w-[110px] pl-2 pr-6 py-1 text-xs rounded-lg border border-gray-200 bg-white
                   hover:border-igss-300 focus:border-igss-600 focus:ring-2 focus:ring-igss-600/10
                   focus:outline-none transition-all duration-150 shadow-sm appearance-none"
      >
        <option value="">{placeholder}</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-1 flex items-center">
        <svg className="w-3 h-3 text-igss-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function LabSampleMatrix({ field, value, onChange }) {
  const fieldId = field?.id || 'lab_muestras_json'
  // Parse JSON → array
  const samples = useMemo(() => {
    if (!value) return DEFAULT_SAMPLES
    try {
      const parsed = JSON.parse(value)
      if (!Array.isArray(parsed) || parsed.length === 0) return DEFAULT_SAMPLES
      // Ensure all 5 slots are present in order
      return DEFAULT_SAMPLES.map((def) => {
        const found = parsed.find((s) => s.slot === def.slot)
        return found ? { ...def, ...found } : def
      })
    } catch {
      return DEFAULT_SAMPLES
    }
  }, [value])

  // Update a single field in a single row, convert back to JSON
  const handleCellChange = (slotKey, columnKey, cellValue) => {
    const updated = samples.map((row) =>
      row.slot === slotKey ? { ...row, [columnKey]: cellValue } : row
    )
    onChange(fieldId, JSON.stringify(updated))
  }

  // Render the correct input widget per column type
  const renderCell = (row, col) => {
    const cellValue = row[col.key]
    const update = (v) => handleCellChange(row.slot, col.key, v)

    switch (col.type) {
      case 'text':
        return <MatrixTextInput value={cellValue} onChange={update} />
      case 'date':
        return <MatrixDateInput value={cellValue} onChange={update} />
      case 'igm_igg':
        return <MatrixSelect value={cellValue} onChange={update} options={IgM_IgG_OPTIONS} />
      case 'avidez':
        return <MatrixSelect value={cellValue} onChange={update} options={AVIDEZ_OPTIONS} />
      default:
        return null
    }
  }

  return (
    <div className="rounded-xl border-2 border-gray-200 overflow-hidden shadow-sm bg-white">
      {/* Section header */}
      <div className="bg-igss-600 px-4 py-2">
        <h3 className="text-white font-semibold text-sm tracking-wide">
          Matriz de Resultados de Laboratorio
        </h3>
        <p className="text-igss-100 text-xs mt-0.5">
          Complete los datos de cada muestra recolectada
        </p>
      </div>

      {/* Scrollable table wrapper */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-xs" style={{ minWidth: '1100px' }}>
          <thead>
            {/* Row 1: group span headers */}
            <tr className="bg-igss-50">
              {/* Empty cell for "Muestra" column */}
              <th
                rowSpan={2}
                className="sticky left-0 z-10 bg-igss-100 border border-gray-200 px-3 py-2
                           text-igss-800 font-semibold text-left whitespace-nowrap min-w-[160px]"
              >
                Muestra
              </th>
              {/* General columns (no group) */}
              <th className="border border-gray-200 px-2 py-1 text-igss-700 font-medium text-center whitespace-nowrap bg-igss-50"
                  rowSpan={2}>
                Orden de laboratorio
              </th>
              <th className="border border-gray-200 px-2 py-1 text-igss-700 font-medium text-center whitespace-nowrap bg-igss-50"
                  rowSpan={2}>
                Fecha Toma
              </th>
              <th className="border border-gray-200 px-2 py-1 text-igss-700 font-medium text-center whitespace-nowrap bg-igss-50"
                  rowSpan={2}>
                Fecha Envío
              </th>
              {/* Sarampión group */}
              <th
                colSpan={3}
                className="border border-gray-200 px-2 py-1 text-center font-semibold bg-red-50 text-red-700"
              >
                Sarampión
              </th>
              {/* Rubéola group */}
              <th
                colSpan={3}
                className="border border-gray-200 px-2 py-1 text-center font-semibold bg-purple-50 text-purple-700"
              >
                Rubéola
              </th>
              {/* Fecha Resultado */}
              <th className="border border-gray-200 px-2 py-1 text-igss-700 font-medium text-center whitespace-nowrap bg-igss-50"
                  rowSpan={2}>
                Fecha Resultado
              </th>
            </tr>
            {/* Row 2: sub-headers for Sarampión and Rubéola */}
            <tr className="bg-igss-50">
              {/* Sarampión sub-columns */}
              <th className="border border-gray-200 px-2 py-1 text-center text-red-600 font-medium bg-red-50 whitespace-nowrap">
                IgM
              </th>
              <th className="border border-gray-200 px-2 py-1 text-center text-red-600 font-medium bg-red-50 whitespace-nowrap">
                IgG
              </th>
              <th className="border border-gray-200 px-2 py-1 text-center text-red-600 font-medium bg-red-50 whitespace-nowrap">
                Avidez
              </th>
              {/* Rubéola sub-columns */}
              <th className="border border-gray-200 px-2 py-1 text-center text-purple-600 font-medium bg-purple-50 whitespace-nowrap">
                IgM
              </th>
              <th className="border border-gray-200 px-2 py-1 text-center text-purple-600 font-medium bg-purple-50 whitespace-nowrap">
                IgG
              </th>
              <th className="border border-gray-200 px-2 py-1 text-center text-purple-600 font-medium bg-purple-50 whitespace-nowrap">
                Avidez
              </th>
            </tr>
          </thead>

          <tbody>
            {samples.map((row, rowIdx) => (
              <tr
                key={row.slot}
                className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50/60'}
              >
                {/* Row label — sticky on the left */}
                <td
                  className={`sticky left-0 z-10 border border-gray-200 px-3 py-2 font-medium
                              text-igss-800 whitespace-normal leading-tight min-w-[160px]
                              ${rowIdx % 2 === 0 ? 'bg-igss-50' : 'bg-igss-100/60'}`}
                >
                  {SLOT_LABELS[row.slot]}
                </td>

                {/* Data cells — iterate COLUMNS in declaration order */}
                {COLUMNS.map((col) => {
                  // Pick background tint based on group
                  let cellBg = ''
                  if (col.group === 'sarampion') cellBg = 'bg-red-50/30'
                  if (col.group === 'rubeola')   cellBg = 'bg-purple-50/30'

                  return (
                    <td
                      key={col.key}
                      className={`border border-gray-200 px-1.5 py-1.5 ${cellBg}`}
                    >
                      {renderCell(row, col)}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer note */}
      <div className="bg-gray-50 border-t border-gray-200 px-4 py-2">
        <p className="text-xs text-gray-500">
          * Solo complete las filas correspondientes a las muestras recolectadas. Deje vacías las que no apliquen.
        </p>
      </div>
    </div>
  )
}
