import { useCallback } from 'react'

export default function SuccessScreen({ onNewForm, isOffline, registroId, pacienteNombre, diagnostico }) {
  const handleCopy = useCallback(() => {
    const text = `Constancia de Registro - Vigilancia Sarampión IGSS\n` +
      `No. Registro: ${registroId}\n` +
      `Paciente: ${pacienteNombre || 'N/A'}\n` +
      `Diagnóstico: ${diagnostico || 'N/A'}\n` +
      `Fecha: ${new Date().toLocaleString('es-GT', { timeZone: 'America/Guatemala' })}`

    navigator.clipboard?.writeText(text).then(() => {
      const btn = document.getElementById('copy-btn')
      if (btn) {
        btn.textContent = 'Copiado'
        setTimeout(() => { btn.textContent = 'Copiar Constancia' }, 2000)
      }
    })
  }, [registroId, pacienteNombre, diagnostico])

  const handlePrint = useCallback(() => {
    window.print()
  }, [])

  return (
    <div className="text-center py-8 px-4 fade-in">
      {/* Animated checkmark */}
      <div className="mx-auto w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mb-6">
        <svg
          className="w-12 h-12 text-igss-green"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          style={{ animation: 'checkDraw 0.5s ease-out 0.2s both' }}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2.5}
            d="M5 13l4 4L19 7"
          />
        </svg>
      </div>

      <h2 className="text-2xl font-bold text-gray-800 mb-2">
        Registro Enviado Exitosamente
      </h2>

      {isOffline && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4 max-w-md mx-auto">
          <p className="text-yellow-800 text-sm">
            <strong>Modo sin conexion:</strong> Los datos se guardarán localmente
            y se enviarán automáticamente al reconectarse.
          </p>
        </div>
      )}

      {/* Constancia de registro */}
      <div className="max-w-md mx-auto bg-gradient-to-b from-igss-light to-white border-2 border-igss-primary/20 rounded-xl p-6 mt-4 mb-6 shadow-lg print:shadow-none">
        <div className="flex items-center justify-center gap-2 mb-4">
          <img
            src={`${import.meta.env.BASE_URL}igss-logo.png`}
            alt="IGSS"
            className="w-10 h-10 object-contain"
          />
          <div className="text-left">
            <p className="text-xs text-igss-primary font-bold uppercase">IGSS - Epidemiología</p>
            <p className="text-[10px] text-gray-500">Vigilancia Brote Sarampión 2026</p>
          </div>
        </div>

        <div className="border-t border-igss-primary/20 pt-4">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">No. de Registro</p>
          <p className="text-lg font-mono font-bold text-igss-primary tracking-wide select-all">
            {registroId}
          </p>
        </div>

        <div className="grid grid-cols-1 gap-2 mt-4 text-left">
          {pacienteNombre && (
            <div>
              <p className="text-[10px] text-gray-400 uppercase">Paciente</p>
              <p className="text-sm text-gray-700 font-medium">{pacienteNombre}</p>
            </div>
          )}
          {diagnostico && (
            <div>
              <p className="text-[10px] text-gray-400 uppercase">Diagnóstico</p>
              <p className="text-sm text-gray-700 font-medium">{diagnostico}</p>
            </div>
          )}
          <div>
            <p className="text-[10px] text-gray-400 uppercase">Fecha y Hora de Envío</p>
            <p className="text-sm text-gray-700 font-medium">
              {new Date().toLocaleString('es-GT', {
                timeZone: 'America/Guatemala',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
          </div>
        </div>

        <p className="text-[10px] text-gray-400 mt-4 italic">
          Conserve este número como constancia de su registro.
        </p>
      </div>

      {/* Action buttons */}
      <div className="flex flex-col sm:flex-row gap-3 justify-center no-print">
        <button
          id="copy-btn"
          onClick={handleCopy}
          className="inline-flex items-center justify-center px-5 py-2.5 border-2 border-igss-primary text-igss-primary font-semibold rounded-lg hover:bg-igss-light transition-colors"
        >
          <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          Copiar Constancia
        </button>

        <button
          onClick={handlePrint}
          className="inline-flex items-center justify-center px-5 py-2.5 border-2 border-gray-300 text-gray-600 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
        >
          <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
          </svg>
          Imprimir
        </button>

        <button
          onClick={onNewForm}
          className="inline-flex items-center justify-center px-6 py-2.5 bg-igss-primary text-white font-semibold rounded-lg hover:bg-igss-dark transition-colors shadow-md hover:shadow-lg"
        >
          <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Nuevo Registro
        </button>
      </div>

      <style>{`
        @keyframes checkDraw {
          from {
            stroke-dasharray: 100;
            stroke-dashoffset: 100;
            opacity: 0;
          }
          to {
            stroke-dasharray: 100;
            stroke-dashoffset: 0;
            opacity: 1;
          }
        }
      `}</style>
    </div>
  )
}
