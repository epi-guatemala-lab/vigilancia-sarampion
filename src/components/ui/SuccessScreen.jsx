import { useCallback } from 'react'

export default function SuccessScreen({ onNewForm, isOffline, registroId, pacienteNombre, diagnostico }) {
  const handleCopy = useCallback(() => {
    const text = [
      '════════════════════════════════',
      'CONSTANCIA DE REGISTRO',
      'Vigilancia Sarampión - IGSS',
      '════════════════════════════════',
      '',
      `No. Registro: ${registroId}`,
      `Paciente: ${pacienteNombre || 'N/A'}`,
      `Diagnóstico: ${diagnostico || 'N/A'}`,
      `Fecha: ${new Date().toLocaleString('es-GT', { timeZone: 'America/Guatemala' })}`,
      '',
      'IGSS - Medicina Preventiva',
      'Sección de Epidemiología',
    ].join('\n')

    navigator.clipboard?.writeText(text).then(() => {
      const btn = document.getElementById('copy-btn-text')
      if (btn) {
        btn.textContent = 'Copiado'
        setTimeout(() => { btn.textContent = 'Copiar' }, 2000)
      }
    })
  }, [registroId, pacienteNombre, diagnostico])

  return (
    <div className="py-6 fade-in">
      {/* Success animation */}
      <div className="text-center mb-6">
        <div className="mx-auto w-20 h-20 rounded-2xl bg-gradient-to-br from-igss-600 to-igss-800 flex items-center justify-center shadow-igss-lg mb-4">
          <svg
            className="w-10 h-10 text-white"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            style={{ animation: 'checkDraw 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.2s both' }}
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
          </svg>
        </div>

        <h2 className="text-xl font-extrabold text-igss-900 mb-1">
          Registro Enviado
        </h2>
        <p className="text-sm text-gray-500">
          {isOffline
            ? 'Guardado localmente — se enviará al reconectarse'
            : 'Los datos fueron registrados correctamente'
          }
        </p>
      </div>

      {/* Constancia card */}
      <div className="print-constancia max-w-sm mx-auto rounded-2xl overflow-hidden shadow-igss-lg border border-igss-200">
        {/* Card header */}
        <div className="bg-gradient-to-r from-igss-800 to-igss-700 px-5 py-3 flex items-center gap-3">
          <img
            src={`${import.meta.env.BASE_URL}igss-logo.png`}
            alt="IGSS"
            className="w-9 h-9 object-contain"
          />
          <div>
            <p className="text-[10px] text-igss-300 font-bold uppercase tracking-wider">Constancia de Registro</p>
            <p className="text-[9px] text-igss-400">Vigilancia Epidemiológica — Sarampión 2026</p>
          </div>
        </div>

        {/* Gold divider */}
        <div className="h-0.5 bg-gradient-to-r from-igss-gold-dark via-igss-gold to-igss-gold-light" />

        {/* Card body */}
        <div className="bg-white px-5 py-5">
          {/* Registration number - the star */}
          <div className="text-center mb-5">
            <p className="text-[10px] text-gray-400 uppercase tracking-widest mb-1">No. de Registro</p>
            <p className="text-base font-mono font-extrabold text-igss-800 tracking-wider select-all bg-igss-50 py-2 px-3 rounded-lg border border-igss-200">
              {registroId}
            </p>
          </div>

          {/* Details */}
          <div className="space-y-3">
            {pacienteNombre && (
              <div className="flex items-start gap-2">
                <svg className="w-4 h-4 text-igss-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <div>
                  <p className="text-[10px] text-gray-400 uppercase">Paciente</p>
                  <p className="text-sm text-gray-800 font-semibold">{pacienteNombre}</p>
                </div>
              </div>
            )}
            {diagnostico && (
              <div className="flex items-start gap-2">
                <svg className="w-4 h-4 text-igss-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div>
                  <p className="text-[10px] text-gray-400 uppercase">Diagnóstico</p>
                  <p className="text-sm text-gray-800 font-semibold">{diagnostico}</p>
                </div>
              </div>
            )}
            <div className="flex items-start gap-2">
              <svg className="w-4 h-4 text-igss-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-[10px] text-gray-400 uppercase">Fecha y hora</p>
                <p className="text-sm text-gray-800 font-semibold">
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
          </div>
        </div>

        {/* Card footer */}
        <div className="bg-igss-50 px-5 py-3 border-t border-igss-100">
          <p className="text-[10px] text-igss-700/50 text-center italic">
            Conserve este número como constancia de su registro
          </p>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex flex-col sm:flex-row gap-2.5 justify-center mt-6 no-print">
        <button
          id="copy-btn"
          onClick={handleCopy}
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 border-2 border-igss-700 text-igss-700 font-semibold text-sm rounded-xl hover:bg-igss-50 transition-all active:scale-95"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <span id="copy-btn-text">Copiar</span>
        </button>

        <button
          onClick={() => window.print()}
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 border-2 border-gray-300 text-gray-600 font-semibold text-sm rounded-xl hover:bg-gray-50 transition-all active:scale-95"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
          </svg>
          Imprimir
        </button>

        {/* Download Ficha PDF */}
        {registroId && (
          <a
            href={`${import.meta.env.VITE_API_URL || ''}/api/ficha-publica/${registroId}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-red-600 text-white font-semibold text-sm rounded-xl hover:bg-red-700 transition-all duration-200 shadow-sm active:scale-95"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Descargar Ficha PDF
          </a>
        )}

        <button
          onClick={onNewForm}
          className="inline-flex items-center justify-center gap-2 px-6 py-2.5 bg-gradient-to-r from-igss-800 to-igss-700 text-white font-bold text-sm rounded-xl hover:from-igss-900 hover:to-igss-800 shadow-igss hover:shadow-igss-lg transition-all active:scale-95"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
            transform: scale(0.8);
          }
          to {
            stroke-dasharray: 100;
            stroke-dashoffset: 0;
            opacity: 1;
            transform: scale(1);
          }
        }

        @media print {
          /* Ocultar todo excepto la constancia */
          body > *:not(#root) { display: none !important; }
          header, footer, nav, .no-print { display: none !important; }

          /* El contenedor principal del app */
          #root > * { display: none !important; }
          #root > *:has(.print-constancia) { display: block !important; }

          /* Solo mostrar la constancia */
          .fade-in > *:not(.print-constancia) { display: none !important; }
          .print-constancia {
            display: block !important;
            margin: 0 auto !important;
            max-width: 100% !important;
            width: 350px !important;
            box-shadow: none !important;
            border: 2px solid #1a3d2e !important;
            break-inside: avoid;
          }

          /* Ajustar página */
          @page {
            size: auto;
            margin: 15mm;
          }

          /* Mostrar título antes de la constancia */
          .print-constancia::before {
            content: "CONSTANCIA DE REGISTRO - Vigilancia Sarampión IGSS";
            display: block;
            text-align: center;
            font-size: 10pt;
            font-weight: bold;
            margin-bottom: 10px;
            color: #1a3d2e;
          }
        }
      `}</style>
    </div>
  )
}
