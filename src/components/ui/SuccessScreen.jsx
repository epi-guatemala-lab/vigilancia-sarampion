export default function SuccessScreen({ onNewForm, isOffline }) {
  return (
    <div className="text-center py-12 px-4 fade-in">
      {/* Animated checkmark */}
      <div className="mx-auto w-24 h-24 rounded-full bg-green-100 flex items-center justify-center mb-6">
        <svg
          className="w-14 h-14 text-igss-green"
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

      <h2 className="text-2xl font-bold text-gray-800 mb-3">
        Registro Enviado Exitosamente
      </h2>

      {isOffline ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6 max-w-md mx-auto">
          <p className="text-yellow-800 text-sm">
            <strong>Modo sin conexion:</strong> Los datos se han guardado localmente
            y se enviarán automáticamente cuando se restablezca la conexión a internet.
          </p>
        </div>
      ) : (
        <p className="text-gray-600 mb-6 max-w-md mx-auto">
          Los datos del caso han sido registrados correctamente en el sistema
          de vigilancia epidemiológica.
        </p>
      )}

      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <button
          onClick={onNewForm}
          className="inline-flex items-center justify-center px-6 py-3 bg-igss-primary text-white font-semibold rounded-lg hover:bg-igss-dark transition-colors shadow-md hover:shadow-lg"
        >
          <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
