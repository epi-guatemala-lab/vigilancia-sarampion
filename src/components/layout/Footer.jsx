export default function Footer({ isOnline, pendingCount }) {
  return (
    <footer className="bg-igss-dark text-white mt-8">
      <div className="max-w-3xl mx-auto px-4 py-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-400' : 'bg-red-400'}`} />
            <span className="text-blue-200">
              {isOnline ? 'Conectado' : 'Sin conexión'}
              {pendingCount > 0 && ` | ${pendingCount} envío(s) pendiente(s)`}
            </span>
          </div>
          <div className="text-blue-300 text-center">
            IGSS — Departamento de Medicina Preventiva — Sección de Epidemiología
          </div>
          <div className="text-blue-400">
            &copy; {new Date().getFullYear()} IGSS Guatemala
          </div>
        </div>
      </div>
    </footer>
  )
}
