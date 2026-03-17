import { useState } from 'react'

export default function FileField({ field, value, onChange, error }) {
  const [fileName, setFileName] = useState('')

  const handleChange = (e) => {
    const file = e.target.files[0]
    if (!file) return

    if (file.size > 5 * 1024 * 1024) {
      alert('El archivo no debe exceder 5 MB')
      return
    }

    setFileName(file.name)

    const reader = new FileReader()
    reader.onloadend = () => {
      onChange(field.id, reader.result)
    }
    reader.readAsDataURL(file)
  }

  return (
    <div>
      <label className={`flex items-center justify-center w-full px-4 py-6 rounded-lg border-2 border-dashed cursor-pointer transition-colors ${
        error
          ? 'border-red-400 bg-red-50'
          : 'border-gray-300 bg-gray-50 hover:bg-igss-light hover:border-igss-accent'
      }`}>
        <div className="text-center">
          <svg className="mx-auto h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p className="mt-1 text-sm text-gray-600">
            {fileName || 'Haga clic para seleccionar archivo'}
          </p>
          <p className="text-xs text-gray-400 mt-1">Máximo 5 MB</p>
        </div>
        <input
          type="file"
          onChange={handleChange}
          accept="image/*,.pdf"
          className="hidden"
        />
      </label>
    </div>
  )
}
